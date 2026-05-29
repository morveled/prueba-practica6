from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions.base import AppException
from app.schemas.response import ApiError

async def app_exception_handler(
    request: Request,
    exc: AppException
):
    """
    Captura las excepciones personalizadas de la aplicación (AppException)
    y retorna una respuesta JSON estructurada con el esquema ApiError.
    """
    return JSONResponse(
        status_code=exc.code,
        content=ApiError(
            codigo=exc.code,
            mensaje=exc.message,
            resultado=exc.result,
        ).model_dump()
    )

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """
    Captura los errores de validación de FastAPI (Pydantic) y los
    formatea bajo el esquema estándar de la aplicación.
    """
    # Podemos extraer más detalle de exc.errors() si quisiéramos ser más específicos
    errors = [
        {**e, "ctx": {k: str(v) for k, v in e["ctx"].items()}} if "ctx" in e else e
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=400,
        content=ApiError(
            codigo=400,
            mensaje="Datos inválidos",
            resultado=errors
        ).model_dump()
    )

