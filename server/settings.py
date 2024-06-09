from __future__ import annotations

import os
import secrets
import string
from typing import Any, Dict, List, Optional

from pydantic import field_validator
from pydantic.networks import EmailStr, PostgresDsn
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

SRC_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV = os.getenv('ENV', 'prod')


def read_prompts_to_dict(org_name: str) -> dict[str, str]:
    directory = os.path.join(SRC_ROOT, "bots", "prompts", org_name)
    if not os.path.exists(directory):
        directory = os.path.join(SRC_ROOT, "bots", "prompts", "langchain")

    prompts_dict = {}
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                base_name = os.path.splitext(file)[0]
                prompts_dict[base_name] = f.read()

    return prompts_dict


class AppSettings(BaseSettings):
    """
    Deal with global app settings.

    The goal is to provide some sensible default for developers here. All constants can be
    overloaded via ENV vars. The validators are used to ensure that you get readable error
    messages when an ENV var isn't correctly formatted; for example when you provide an incorrect
    formatted SQLALCHEMY_DATABASE_URI.

    ".env" loading is also supported. FastAPI will autoload "<env>.env" file, where <env> is the
    value of ENV environment variable (use local, dev, prod for example) if one can be found.
    """
    model_config = SettingsConfigDict(env_file=f'.env.{ENV}', extra='allow')

    PROJECT_NAME: str = "REsolution Team"
    TESTING: bool = True

    SESSION_SECRET: str = "".join(
        secrets.choice(string.ascii_letters) for i in range(16))  # noqa: S311
    # OAUTH settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str

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
    SQLALCHEMY_DATABASE_URI: str = "postgresql://postgres:postgres@localhost/postgres"

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
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
    SERVICE_NAME: str = "Guardian Server"
    LOGGING_HOST: str = "localhost"
    LOG_LEVEL: str = "INFO"

    FIRST_SUPERUSER: EmailStr = "justice@heaven.org"
    FIRST_SUPERUSER_PASSWORD: str = "CHANGEME"
    FIRST_USER: EmailStr = "honor@heaven.org"
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

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Analytics
    LANGCHAIN_API_KEY: str = None
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_PROJECT: str = None

    # OpenAI
    OPENAI_API_KEY: str
    GPT_35: str = "gpt-3.5-turbo-1106"
    GPT_4: str = "gpt-4o"

    # LlamaIndex
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # Project settings
    DEFAULT_CHAT_MEMORY_SIZE: int = 5
    KNOWLEDGE_URLS: Optional[str] = None
    KNOWLEDGE_DIR: Optional[str] = "upload"  # path relative to the SRC_ROOT


app_settings = AppSettings()
app_settings.SQLALCHEMY_DATABASE_URI = app_settings.SQLALCHEMY_DATABASE_URI
os.environ['OPENAI_API_KEY'] = app_settings.OPENAI_API_KEY
