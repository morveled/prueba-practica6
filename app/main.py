from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.api.v1.api import api_router
from app.core.exceptions.base import AppException
from app.core.handlers.exception_handlers import (
    app_exception_handler,
    validation_exception_handler
)

# Creamos la instancia principal de FastAPI
app = FastAPI(
    title="Users API",
    description="API para la gestión de usuarios con FastAPI y SQLModel",
    version="1.0.0"
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
        "mensaje": "¡Bienvenido a la Users API!",
        "estado": "Operativa",
        "version": "1.0.0"
    }

