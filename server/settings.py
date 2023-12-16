from __future__ import annotations

import os
import secrets
import string
from typing import Any, Dict, List, Optional

from pydantic import field_validator
from pydantic.networks import EmailStr, PostgresDsn
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings

SRC_ROOT = os.path.dirname(os.path.abspath(__file__))


def read_prompts_to_dict():
    files_content = {}
    directory = os.path.join(SRC_ROOT, 'bots', 'prompts')
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                base_name = os.path.splitext(file)[0]
                files_content[base_name] = f.read()
    return files_content


class AppSettings(BaseSettings):
    """
    Deal with global app settings.

    The goal is to provide some sensible default for developers here. All constants can be
    overloaded via ENV vars. The validators are used to ensure that you get readable error
    messages when an ENV var isn't correctly formatted; for example when you provide an incorrect
    formatted DATABASE_URI.

    ".env" loading is also supported. FastAPI will autoload and ".env" file if one can be found
    """

    PROJECT_NAME: str = "Boilerplate webservice"
    TESTING: bool = True

    SESSION_SECRET: str = "".join(
        secrets.choice(string.ascii_letters) for i in range(16))  # noqa: S311
    # OAUTH settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"
    # CORS settings
    CORS_ORIGINS: str = "*"
    CORS_ALLOW_METHODS: List[str] = [
        "GET",
        "PUT",
        "PATCH",
        "POST",
        "DELETE",
        "OPTIONS",
        "HEAD",
    ]
    CORS_ALLOW_HEADERS: List[str] = [
        "If-None-Match",
        "Authorization",
        "If-Match",
        "Content-Type",
    ]
    CORS_EXPOSE_HEADERS: List[str] = [
        "Cache-Control",
        "Content-Language",
        "Content-Length",
        "Content-Type",
        "Expires",
        "Last-Modified",
        "Pragma",
        "Content-Range",
        "ETag",
    ]
    SWAGGER_PORT: int = 8080
    ENVIRONMENT: str = "local"
    SWAGGER_HOST: str = "localhost"
    GUI_URI: str = "http://localhost:3000"
    DATABASE_URI: str = "postgresql://boilerplate:boilerplate@localhost/boilerplate"

    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    MAX_WORKERS: int = 5
    CACHE_HOST: str = "127.0.0.1"
    CACHE_PORT: int = 6379
    POST_MORTEM_DEBUGGER: str = ""
    SERVICE_NAME: str = "Boilerplate"
    LOGGING_HOST: str = "localhost"
    LOG_LEVEL: str = "DEBUG"

    FIRST_SUPERUSER: EmailStr = "admin@banaan.org"
    FIRST_SUPERUSER_PASSWORD: str = "CHANGEME"
    FIRST_USER: EmailStr = "user@banaan.org"
    FIRST_USER_PASSWORD: str = "CHANGEME"

    # Mail settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @field_validator("EMAILS_FROM_NAME")
    @classmethod
    def get_project_name(cls, v: Optional[str], info: ValidationInfo) -> str:
        if not v:
            return info.data["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    # Todo: check path. The original had one extra folder "app"
    EMAIL_TEMPLATES_DIR: str = "/server/email-templates/build"

    EMAILS_ENABLED: bool = False

    @field_validator("EMAILS_ENABLED", mode="before")
    @classmethod
    def get_emails_enabled(cls, v: bool, info: ValidationInfo) -> bool:
        return bool(
            info.data["SMTP_HOST"] and info.data["SMTP_PORT"] and info.data["EMAILS_FROM_EMAIL"])

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore

    SUPABASE_URL: str
    SUPABASE_KEY: str
    OPENAI_API_KEY: str
    LANGCHAIN_WANDB_TRACING: bool = False
    WANDB_PROJECT: str = "guardian"
    KNOWLEDGE_URLS: str

    # Llamaindex configs
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    PROMPTS: dict[str, str] = read_prompts_to_dict()


ENV = os.getenv('ENV', 'prod')
app_settings = AppSettings(_env_file=f'{ENV}.env')
