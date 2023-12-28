import logging
import os

import structlog
from fastapi import HTTPException
from fastapi.applications import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from starlette.middleware.sessions import SessionMiddleware

from modules.api_key.controller import api_key_router
from modules.chat.controller import chat_router
from modules.contact_support.controller import contact_router
from modules.misc.controller import misc_router
from modules.notification.controller import notification_router
from modules.onboarding.controller import onboarding_router
from modules.prompt.controller import prompt_router
from modules.upload.controller import upload_router
from modules.user.controller import user_router
from packages.utils import handle_request_validation_error
from server.db import db
from server.db.database import DBSessionMiddleware
from server.settings import app_settings

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger(__name__)

app = FastAPI(
    title="Guardian Chatbot",
    description="The final chatbot.",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    default_response_class=JSONResponse,
    # root_path="/prod",
    servers=[  # TODO: wtf is this?
        {
            "url": "https://postgres-boilerplate.renedohmen.nl",
            "description": "Test environment",
        }
        if os.getenv("ENVIRONMENT") == "production"
        else {"url": "/", "description": "Local environment"},
    ],
)

app.include_router(chat_router)
app.include_router(onboarding_router)
app.include_router(misc_router)

app.include_router(upload_router)
app.include_router(user_router)
app.include_router(api_key_router)
app.include_router(prompt_router)
app.include_router(notification_router)
app.include_router(contact_router)


@app.exception_handler(HTTPException)
def http_exception_handler(_, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


handle_request_validation_error(app)

app.add_middleware(SessionMiddleware, secret_key=app_settings.SESSION_SECRET)
app.add_middleware(DBSessionMiddleware, database=db)
origins = app_settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=app_settings.CORS_ALLOW_METHODS,
    allow_headers=app_settings.CORS_ALLOW_HEADERS,
    expose_headers=app_settings.CORS_EXPOSE_HEADERS,
)


logger.info("Guardian is reporting for duty 🛡️🌟🗡️")
handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    # run main.py to debug backend
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5050)
