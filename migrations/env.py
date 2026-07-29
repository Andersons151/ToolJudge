from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool

# Import your Flask app + SQLAlchemy metadata
from app import create_app
from app.extensions import db

# Alembic Config object
config = context.config

# Logging configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load Flask app so Alembic can access models
app = create_app()

with app.app_context():
    target_metadata = db.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Alembic reads DB URL from alembic.ini, but we override it with Flask config
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = app.config["SQLALCHEMY_DATABASE_URI"]

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,        # detect column type changes
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
