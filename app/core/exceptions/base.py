from typing import Any, Optional

class AppException(Exception):
    """
    Excepción base para toda la aplicación.
    Permite capturar errores de negocio y transformarlos en respuestas uniformes.
    """
    def __init__(
        self,
        message: str,
        code: int = 400,
        result: Optional[Any] = None
    ):
        self.message = message
        self.code = code
        self.result = result
        # Llamamos al constructor base de Exceptions con el mensaje descriptivo
        super().__init__(self.message)

