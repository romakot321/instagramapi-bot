from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings
from loguru import logger
from fastapi_utils.tasks import repeat_every
from contextlib import asynccontextmanager
import asyncio
import datetime as dt

from api.services.subscription import SubscriptionService
from api.services.user import UserService
from app.controller import BotController
from app.main import setup_bot

# from db.admin import attach_admin_panel


class ProjectSettings(BaseSettings):
    LOCAL_MODE: bool = False


def register_exception(application):
    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        # or logger.error(f'{exc}')
        logger.debug(f'{exc}')
        content = {'status_code': 422, 'message': exc_str, 'data': None}
        return JSONResponse(
            content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


def register_cors(application):
    application.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@repeat_every(seconds=3600 * 2, wait_first=3600, raise_exceptions=True)
async def send_reports():
    async with UserService() as user_service:
        users = await user_service.list(count=10000000)
    async with SubscriptionService() as subscription_service:
        subscriptions = await subscription_service.list(count=10000000)
    now = dt.datetime.now(dt.UTC)
    user_id_to_subscriptions = {user.telegram_id: [s for s in subscriptions if s.user_telegram_id == user.telegram_id] for user in users}
    for user in users:
        for subscription in user_id_to_subscriptions.get(user.telegram_id, []):
            logger.debug(subscription.tracking_username)
            if subscription.tracking_username is None:
                continue
            # if now.hour * 3600 % int(subscription.tariff.tracking_report_interval) == 0:
            #     await UserService.create_report(user.telegram_id, subscription.tracking_username)
            await UserService.create_report(user.telegram_id, subscription.tracking_username)


@asynccontextmanager
async def application_lifespan(app: FastAPI):
    await send_reports()

    bot_events = setup_bot(app)
    if bot_events is not None:
        on_startup, on_shutdown = bot_events
    else:
        yield
        return

    if asyncio.iscoroutinefunction(on_startup):
        await on_startup()
    else:
        on_startup()
    yield
    if asyncio.iscoroutinefunction(on_shutdown):
        await on_shutdown()
    else:
        on_shutdown()


def init_web_application():
    project_settings = ProjectSettings()
    application = FastAPI(
        openapi_url='/openapi.json',
        docs_url='/docs',
        redoc_url='/redoc',
        lifespan=application_lifespan
    )

    if project_settings.LOCAL_MODE:
        register_exception(application)
        register_cors(application)

    from api.routes.subscription import router as subscription_router
    from api.routes.web import router as web_router
    from api.routes.user import router as user_router

    application.include_router(subscription_router)
    application.include_router(web_router)
    application.include_router(user_router)
    application.mount("/static", StaticFiles(directory="static"), name="static")

    # attach_admin_panel(application)

    return application


def run() -> FastAPI:
    logger.disable("sqlalchemy_service")
    application = init_web_application()
    return application


fastapi_app = run()
