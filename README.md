# API REST de Usuarios

API REST para la gestión de usuarios, implementando arquitectura de 3 capas (controlador, servicio, repositorio).

## Características

-  Arquitectura de 3 capas (Controller-Service-Repository)
-  Base de datos SQLite/PostgreSQL con SQLModel
-  Paginación y filtros 
-  Documentación automática OpenAPI/Swagger
-  CORS configurable
-  Manejo de errores

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/BackEnd-FastAPI-Material/api-rest-user.git
   cd api-rest-user

## Entorno virtual

2. **Crear entorno virtual**
python -m venv .venv

3. **Activar entorno virtual**

# En Windows:
.venv\Scripts\activate.bat

# En Linux/Mac:
source .venv/bin/activate

## Dependencias

4. **Instalar dependencias**
pip install "fastapi[standard]" sqlmodel pydantic-settings pydantic[email] passlib[bcrypt] python-jose[cryptography] python-dotenv python-multipart aiosqlite psycopg2-binary

## Ejecución
5. **Ejecutar proyecto**
fastapi dev app/main.py

6. **Desactivar entorno virtual**
deactivate

## Estructura
app/
├── api/              # Capa de controladores (Routers)
│   └── v1/
│       └── endpoints/
├── core/             # Configuración y utilidades
├── models/           # Modelos de datos (SQLModel, ORM)
├── schemas/          # Esquemas Pydantic (DTOs)
├── services/         # Capa de servicios (lógica de negocio)
├── repositories/     # Capa de repositorio (DAO)
├── dependencies.py   # Inyección de dependencias
└── main.py           # Archivo principal