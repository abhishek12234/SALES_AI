from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Create declarative base for models to inherit from
Base = declarative_base()

# Database URL for MySQL using asyncmy
SQLALCHEMY_DATABASE_URL = (
    f"mysql+asyncmy://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
)

# Create the async engine
async_engine: AsyncEngine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
)

# Initialize the database (create all tables)
async def init_db():
    print("⏳ Initializing DB...")
    from models.role_permissions import RolePermission
    from models.users import User
    from models.roles import Role
    from models.ai_personas import AIPersona
    from models.feedback import Feedback
    from models.sessions import Session
    from models.subscriptions import Subscription
    from models.interaction_modes import InteractionMode
    from models.payments import Payment
    from models.user_subscriptions import UserSubscription
    from models.ai_roles import AIRole
    from models.manufacturing_models import ManufacturingModel
    from models.plant_size_impacts import PlantSizeImpact
    from models.industries import Industry
    from models.interaction_mode_report_details import InteractionModeReportDetail



    async with async_engine.begin() as conn:

        print("📥 Creating tables...")
        await conn.run_sync(Base.metadata.create_all)  # Recreate all tables
    print("✅ Database recreated successfully.")

# Dependency to get the DB session
async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())