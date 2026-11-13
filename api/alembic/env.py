from logging.config import fileConfig
import os
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import make_url

from app.models import Base

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option(
    "sqlalchemy.url",
    os.environ.get("DATABASE_URL", config.get_main_option("sqlalchemy.url")).replace("%", "%%"),
)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    database_url = config.get_main_option("sqlalchemy.url")
    connect_args = {}
    if make_url(database_url).get_backend_name() == "postgresql":
        connect_args["options"] = "-csearch_path=public"

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )
    with connectable.connect() as connection:
        if connection.dialect.name == "postgresql":
            with connection.begin():
                connection.exec_driver_sql(
                    """
                    CREATE TABLE IF NOT EXISTS public.alembic_version (
                        version_num VARCHAR(64) NOT NULL,
                        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                    )
                    """
                )
                connection.exec_driver_sql(
                    "ALTER TABLE public.alembic_version ALTER COLUMN version_num TYPE VARCHAR(64)"
                )
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
