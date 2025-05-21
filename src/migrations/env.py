from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from config import settings  # <-- Add this line

# Import Base from your database module and models
from database import Base
from models.role_permissions import RolePermission
from models.users import User
from models.roles import Role
from models.ai_personas import AIPersona
from models.feedback import Feedback
from models.sessions import Session
from models.subscriptions import Subscription
from models.interaction_modes import InteractionMode
from models.performance_reports import PerformanceReport
from models.payments import Payment
from models.user_subscriptions import UserSubscription
from models.ai_roles import AIRole
from models.manufacturing_models import ManufacturingModel
from models.plant_size_impacts import PlantSizeImpact
from models.industries import Industry
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate support
target_metadata = Base.metadata

# Configure the database URL dynamically from settings
def get_url():
    return (
        f"mysql+pymysql://{settings.database_username}:{settings.database_password}"
        f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
    )

# Override the SQLAlchemy URL in the Alembic config
config.set_main_option("sqlalchemy.url", get_url())


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

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
