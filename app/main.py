import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.exception_handlers import register_exception_handlers
from app.lifetime import lifespan
from app.router import status_router, video_router
from app.app_logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(redirect_slashes=False,
            docs_url="/admin/docs",
            redoc_url="/admin/redoc",
            openapi_url="/admin/openapi.json",
            lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()
api_router.include_router(video_router.router)
api_router.include_router(status_router.router)

app.include_router(router=api_router)


register_exception_handlers(app)

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/admin/metrics")
FastAPIInstrumentor.instrument_app(
    app, excluded_urls="^/$|^/ws$|/admin/metrics$|/admin/openapi.json|/ws websocket receive"
)
