from logging.config import fileConfig
import os
import sys
import sqlalchemy as sa
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context

# Projektroot in sys.path (damit "import app..." sicher funktioniert)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.models import Base  # <-- wichtig!

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata  # <-- WICHTIG

def get_url():
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    url = config.get_main_option("sqlalchemy.url")
    if url and url != "driver://user:pass@localhost/dbname":
        return url

    raise RuntimeError(
        "DATABASE_URL is not set and alembic.ini sqlalchemy.url is not configured. "
        "Set DATABASE_URL (recommended) or set sqlalchemy.url in alembic.ini."
    )


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    url = get_url()

    connectable = sa.create_engine(
        url,
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
