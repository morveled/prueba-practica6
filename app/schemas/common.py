from fastapi import Query, HTTPException
from typing import Optional

class CommonQueryParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Número de página"), #página actual
        limit: int = Query(10, ge=1, le=100, description="Cantidad de usuarios por página (por defecto 10)."), #límite de items por página
        sort: str = Query("created_at", description="Campo por el cual ordenar"), #campo para ordenar
        order: str = Query("acs", description="Orden de los resultados") #orden ascendente o descendente
    ):

        # Validar campo sort según el enum del YAML
        allowed_sort_fields = {
            "username", "email", "date_joined", "first_name", "last_name",
            "is_active", "is_deleted", "is_superuser", "email_verified",
            "date_of_birth", "nationality", "occupation", "gender", "role"
        }
        
        if sort not in allowed_sort_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Campo de ordenamiento '{sort}' no válido. "
                       f"Campos permitidos: {', '.join(sorted(allowed_sort_fields))}"
            )
        
        # Validar order
        if order not in {"asc", "desc"}:
            raise HTTPException(
                status_code=400,
                detail="El orden debe ser 'asc' o 'desc'"
            )

        self.page = page
        self.limit = limit
        self.sort = sort
        self.order = order
        self.skip = (page - 1) * limit