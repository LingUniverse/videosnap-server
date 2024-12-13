"""llm service"""

import logging
from litellm import completion
from app.schema.i2v_task_schema import I2vType
from app.util.constant import IMAGINATIVE_SYSTEM_PROMPT, REALISTIC_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

async def call_generate_i2v_prompt_agent(image_base64: str, i2v_type: I2vType) -> str:
    """call generate i2v prompt agent"""
    message = _generate_message(image_base64, i2v_type)
    
    try:
        response = completion(
            model="azure/gpt-4-vision",  #TODO@ztp 抽为配置
            messages=message,
            temperature=1
        )
        #TODO@ztp update task status and data
        return response.choices[0].message.content
    except Exception as e: # pylint: disable=broad-except
        logger.error("Failed to generate prompt: %s", e)
        raise e

def _generate_message(image_base64: str, i2v_type: I2vType) -> list:
    """generate message"""

    if i2v_type is I2vType.IMAGINATIVE:
        system_prompt = IMAGINATIVE_SYSTEM_PROMPT
    elif i2v_type is I2vType.REALISTIC:
        system_prompt = REALISTIC_SYSTEM_PROMPT
    else:
        raise ValueError(f"unsupport i2v_type: {i2v_type}")
    
    return [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": "请根据这张图片生成一个详细的提示词描述。"
                }
            ]
        }
    ]
