from fastapi import Query
from typing import Literal, Optional

SortField = Literal[
    "username",
    "email",
    "date_joined",
    "first_name",
    "last_name",
    "is_active",
    "is_deleted",
    "is_superuser",
    "email_verified",
    "date_of_birth",
    "nationality",
    "occupation",
    "gender",
    "role",
]

OrderField = Literal["asc", "desc"]

class CommonQueryParams:
    def __init__(  #no tocar
        self,
        page: int = Query(1, ge=1, description="Número de página"), #página actual
        limit: int = Query(10, ge=1, le=100, description="Cantidad de usuarios por página (por defecto 10)."), #límite de items por página
        sort: Optional[SortField] = Query(None, description="Campo por el cual ordenar",), #campo para ordenar
        order: OrderField = Query("asc", description="Orden de los resultados",), #orden ascendente o descendente
    ):

        self.page = page
        self.limit = limit
        self.sort = sort
        self.order = order
        self.skip = (page - 1) * limit