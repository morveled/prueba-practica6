from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI( #se crea instancia de FastAPI
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",  #documentación Swagger
    redoc_url="/redoc",  #documentación ReDoc
)

# Configurar CORS 
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware( # Configurar CORS con orígenes específicos en modo producción
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") 
            for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Cuando esta en modo desarrollo se permite todo
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Incluir las rutas de la API v1 
app.include_router(api_router, prefix=settings.API_V1_STR)

# JSON que se muestra al inicio en la raíz / para mostrar info básica
@app.get("/")
async def root():
    return {
        "message": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/docs",
        "api_version": settings.API_V1_STR,
    }


# Esto es para correr el servidor con python app/main.py directamente en modo desarrollo 
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,  # Usar setting para reload
    )