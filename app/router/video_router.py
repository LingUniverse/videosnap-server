import aiohttp
import logging
from typing import List

from fastapi import APIRouter, Depends, BackgroundTasks, Request, HTTPException
from app.schema.base import ResponseModel, StatusCode
from app.schema.i2v_task_schema import I2vTaskCreateReuqest, I2vTaskResponse, VideoGenerationProvider, TaskStatus
from app.dependencies import get_db, get_independent_db_session
from app.repository import i2v_task_dao
from app.repository.i2v_task_model import I2vTask
from app.service.llm_service import call_generate_i2v_prompt_agent
from app.service.i2v_service import VideoGeneratorFactory
from app.utils.file_utils import save_base64_file, read_file_to_base64, save_binary_file

router = APIRouter()
logger = logging.getLogger(__name__)

VIDEOPROVIDER = VideoGenerationProvider.MINIMAX_VIDEO_01

@router.post("/i2v", response_model=ResponseModel[I2vTaskResponse], response_model_exclude_none=True)
async def create_i2v_task(
    i2v_task_request: I2vTaskCreateReuqest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    """create i2v task"""
    
    try:
        image_filename = await save_base64_file(
            i2v_task_request.image_base64,
            "input.png"
        )

        task = await i2v_task_dao.create_i2v_task(
            db,
            image_filename,
            VIDEOPROVIDER,
            i2v_task_request.type
        )
        background_tasks.add_task(process_image_to_video, task)
        return ResponseModel(code=StatusCode.SUCCESS, data=task)
    except Exception as e: # pylint: disable=broad-except
        logger.error("Create i2v task failed: %s", e, exc_info=True)
        return ResponseModel(code=StatusCode.ERROR, msg="create task error")

@router.post("/i2v/status", response_model=ResponseModel[List[I2vTaskResponse]], response_model_exclude_none=True)
async def get_i2v_tasks_status(task_ids: List[str], db=Depends(get_db)):
    """get tasks status"""
    try:
        results = []
        for task_id in task_ids:
            task_status = await query_task_status(task_id, db)
            if task_status:
                results.append(task_status)
                
        return ResponseModel(
            code=StatusCode.SUCCESS,
            data=results
        )
    except Exception as e:
        logger.error("get task status failure: %s", str(e))
        return ResponseModel(
            code=StatusCode.ERROR,
            msg="get task status failure"
        )

@router.post("/iv2/minimax/get_callback")
async def get_callback(request: Request):
    """get callback"""
    try:
        json_data = await request.json()
        challenge = json_data.get("challenge")
        if challenge is not None:
          return {"challenge": challenge}
        else:
            #TODO@ztp 看文档这里还需要什么特殊处理吗
            return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

async def process_image_to_video(task: I2vTask):
    """start image2video task"""
    db = await get_independent_db_session()
    try:
        image_base64 = await read_file_to_base64(task.source_image_filename)
        # 生成图片的描述词
        vision_prompt = await call_generate_i2v_prompt_agent(image_base64, task.i2v_type)
        logger.info("vision_prompt: %s", vision_prompt)

        update_data = {
            "video_generation_prompt": vision_prompt,
            "status": TaskStatus.PROMPT_GENERATED
        }
        await i2v_task_dao.update_i2v_task(db, task.id, update_data)

        # 创建图生视频任务
        generator = VideoGeneratorFactory.create(task.video_generation_provider)
        video_generator_id = await generator.generate(image_base64, vision_prompt)
        
        logger.info("video_generator_id is %s", video_generator_id)
        if video_generator_id is None:
            update_data = {
               "status": TaskStatus.FAILED
            }
            logger.info("set video status failed")
            await i2v_task_dao.update_i2v_task(db, task.id, update_data)
            return

        update_data = {
            "video_generation_id": video_generator_id,
            "status": TaskStatus.TASK_SUBMITTED
        }
        await i2v_task_dao.update_i2v_task(db, task.id, update_data)
        
    except Exception as e: # pylint: disable=broad-except
        logger.error("process_image_to_video: %s", e, exc_info=True)
        await i2v_task_dao.update_i2v_task(db, task.id, {"status": "FAILED"})
    finally:
        await db.close()

async def query_task_status(task_id: str, db) -> I2vTask:
    """query task status"""
    try:
        task = await i2v_task_dao.get_i2v_task_by_id(db, task_id)
        if not task:
            logger.warning("task not found, tid: %s", task_id)
            return None

        logger.info("query task status %s", task.__dict__)

        if task.status in [TaskStatus.IDLE, TaskStatus.PROMPT_GENERATED, TaskStatus.FAILED]:
            return task
            
        elif task.status == TaskStatus.TASK_SUBMITTED:
            try:
                generator = VideoGeneratorFactory.create(task.video_generation_provider)
                status, download_url = await generator.check_status(task.video_generation_id)

                if status == TaskStatus.TASK_SUBMITTED:
                    return task

                if status == TaskStatus.TASK_COMPLETED and download_url:
                    #TODO@ztp 这里封装一下
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(download_url) as response:
                                if response.status != 200:
                                    raise Exception(f"download video failure: HTTP {response.status}")
                                video_content = await response.read()
                        
                        # 使用file_utils保存视频文件到videos子目录
                        video_filename = await save_binary_file(
                            video_content,
                            "output.mp4"
                        )

                        update_data = {
                            "output_video_filename": video_filename,
                            "status": TaskStatus.TASK_COMPLETED
                        }
                        return await i2v_task_dao.update_i2v_task(db, task_id, update_data)
                        
                    except Exception as e:
                        logger.error(f"Error processing video download: {str(e)}")
                        update_data = {
                            "status": TaskStatus.FAILED
                        }
                        return await i2v_task_dao.update_i2v_task(db, task_id, update_data)

                elif status == TaskStatus.FAILED:
                    pass
                    # update_data = {
                    #     "status": TaskStatus.FAILED
                    # }
                    # return await i2v_task_dao.update_i2v_task(db, task_id, update_data)
            
            except Exception as e:
                logger.error("查询任务{task_id}状态失败: {str(e)}")
                return task
            
        elif task.status in [TaskStatus.TASK_COMPLETED, TaskStatus.FAILED]:
            return task

    except Exception as e: # pylint: disable=broad-except
        logger.error("query task status error, tid: %s", task_id, exc_info=True)
        return None