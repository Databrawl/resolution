from typing import Any

import structlog
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.sql.schema import SchemaItem

from db.models import BaseModel, Reflected
from server.settings import app_settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

logger = structlog.get_logger()

config.set_main_option("sqlalchemy.url", app_settings.DATABASE_URI)

target_metadata = BaseModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(obj: SchemaItem,
                   name: Any,
                   type_: str,
                   reflected: Any,
                   compare_to: Any) -> bool:
    if type_ == "table" and obj.schema == "auth":
        # We don't track auth schema changes, as those tables are controlled by Supabase
        return False
    else:
        return True


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):  # type: ignore
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    Reflected.prepare(engine)

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
        compare_type=True,
        include_object=include_object
    )
    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
