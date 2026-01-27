from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel 
from app.core.config import settings
from typing import AsyncGenerator

# Crear motor async y crea engine de la base de datos usando la URL de configuración 
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Para ver las queries SQL en desarrollo 
    future=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker( #para crear sesiones asíncronas
    engine, #parametro engine creado arriba
    class_=AsyncSession, #usar sesiones asíncronas
    expire_on_commit=False, 
    autocommit=False,
    autoflush=False,
)

# Dependency para obtener sesión de DB
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency que provee una sesión de base de datos.
    Se cierra automáticamente al final de la request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_db_and_tables(): #función para crear las tablas en la base de datos
    """
    Crear todas las tablas, se usa en desarrollo.
    Para produccion usar migraciones con Alembic.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)