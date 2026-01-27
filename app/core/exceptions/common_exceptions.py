from app.core.exceptions.base import AppException

class InvalidPaginationException(AppException):
    def __init__(self):
        super().__init__(
            message="Parámetros de paginación inválidos.",
            code=400
        )

class InternalServerException(AppException):
    def __init__(self):
        super().__init__(
            message="Error interno del servidor.",
            code=500
        )