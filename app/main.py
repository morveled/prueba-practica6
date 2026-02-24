from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.api.v1.api import api_router
from app.core.exceptions.base import AppException
from app.core.handlers.exception_handlers import (
    app_exception_handler,
    validation_exception_handler
)
from app.core.database import create_db_and_tables

# Importamos TODOS los modelos para que SQLModel.metadata los registre
# antes de ejecutar create_all. Sin esto, las tablas no se crean.
from app.models.user import User        # noqa: F401
from app.models.product import Product  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Evento de ciclo de vida de la aplicación.
    Al iniciar: crea las tablas que no existan en la BD.
    """
    await create_db_and_tables()
    yield


# Creamos la instancia principal de FastAPI
app = FastAPI(
    title="Users & Products API",
    description="API para la gestión de usuarios y productos con FastAPI y SQLModel",
    version="2.0.0",
    lifespan=lifespan
)

# ---------- REGISTRO DE MANEJADORES DE EXCEPCIONES ----------

# Registramos el handler para excepciones personalizadas del negocio
app.add_exception_handler(AppException, app_exception_handler)

# Registramos el handler para errores de validación de esquemas (Pydantic)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# ---------- REGISTRO DE RUTAS ----------

# Incluimos el router de la versión 1 de la API
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Salud"])
async def root():
    """
    Endpoint de bienvenida para verificar que la API está operativa.
    """
    return {
        "mensaje": "¡Bienvenido a la Users & Products API!",
        "estado": "Operativa",
        "version": "2.0.0"
    }

