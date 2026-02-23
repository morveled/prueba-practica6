from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from app.core.config import settings
from typing import AsyncGenerator

# Se crea el motor asíncrono para PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,    # El parámetro echo refleja las consultas SQL en la terminal (útil en desarrollo)
    future=True,
    pool_pre_ping=True      # Verifica la validez de la conexión antes de usarla
)

# Generador de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency que provee una sesión de base de datos asíncrona.
    Se asegura de cerrar la conexión automáticamente al finalizar la petición.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_db_and_tables():
    """
    Inicializa la base de datos creando todas las tablas definidas en los modelos.
    Se recomienda su uso exclusivamente para entornos de desarrollo.
    Para produccion se recomienda usar migraciones con Alembic.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

