from fastapi import APIRouter
from app.api.v1.endpoints import users, products, auth

# Se crea el router principal para la versión 1 de la API
api_router = APIRouter()

# Se incluyen los endpoints de autenticación (públicos)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

# Se incluyen los endpoints del módulo de usuarios
api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["users"]
)

# Se incluyen los endpoints del módulo de productos
api_router.include_router(
    products.router,
    prefix="/products",
    tags=["products"]
)

