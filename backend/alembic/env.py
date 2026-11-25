import os
import sys

# Add backend to path so `app` module is discoverable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import engine_from_config
from sqlalchemy import create_engine
from alembic import context

# Add model's MetaData for autogenerate support
from app.models import SQLModel as Base
target_metadata = Base.metadata

# Get URL from environment or config
url = os.environ.get("DATABASE_URL", "postgresql://smartwork:smartwork@localhost:5432/smartwork")

def run_migrations_offline() -> None:
    """Run migrations in 'offline mode'."""
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online mode'."""
    connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
