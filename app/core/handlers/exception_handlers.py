from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions.base import AppException
from app.schemas.response import ApiError

async def app_exception_handler(
    request: Request,
    exc: AppException
):
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
    return JSONResponse(
        status_code=400,
        content=ApiError(
            codigo=400,
            mensaje="Datos inválidos",
        ).model_dump()
    )

