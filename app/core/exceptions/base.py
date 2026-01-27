class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: int = 400,
        result=None
    ):
        self.message = message
        self.code = code
        self.result = result
