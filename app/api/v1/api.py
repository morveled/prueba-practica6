from fastapi import APIRouter

from app.api.v1.endpoints import users

api_router = APIRouter() #se crea el router principal de la API v1

api_router.include_router(users.router, prefix="/users", tags=["users"]) #se incluyen las rutas de usuarios con el prefijo /users y la etiqueta "users"