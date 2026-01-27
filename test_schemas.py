from datetime import datetime, date
from uuid import uuid4
from pydantic import ValidationError
from fastapi import HTTPException
from datetime import datetime, timezone
from app.schemas.user import (
    UserCreateRequest,
    User,
    Gender,
    UserBasic,
    PagedUsersResult
)
from app.schemas.common import CommonQueryParams
from app.schemas.response import ApiResponseUser, ApiError
import json

print("\n========== PRUEBAS DE SCHEMAS ==========\n")

# UserCreateRequest
print("1) Probando que UserCreateRequest sea válido...")

user_create = UserCreateRequest(
    username="carlos123",
    password="Password123",
    email="carlos@test.com",
    first_name="Carlos",
    last_name="Gutierrez",
    gender=Gender.MALE
)
print("UserCreateRequest válido creado")

print("\n2) Probando que password sea inválido...")
try:
    UserCreateRequest(
        username="sara123",
        password="12345678",
        email="sara@test.com",
        first_name="Sara",
        last_name="Jimenez",
    )
    print("ERROR: Password débil aceptado")
except ValidationError:
    print("Password inválido rechazado")

# User schema
print("\n3) Probando User schema...")
user = User(
    id=uuid4(),
    username="lore123",
    email="lore@test.com",
    first_name="Lorena",
    last_name="Martinez",
    is_active=True,
    is_superuser=False,
    last_login=None,
    date_joined=datetime.now(timezone.utc), 
    created_at=datetime.now(timezone.utc),
    modified_at=datetime.now(timezone.utc),
    is_deleted=False,
    deleted_at=None,
    profile_picture=None,
    email_verified=False,
    email_verified_at=None,
    nationality=None,
    occupation=None,
    date_of_birth=date(1995, 5, 20),
    contact_phone_number=None,
    gender=Gender.MALE,
    address=None,
    address_number=None,
    address_interior_number=None,
    address_complement=None,
    address_neighborhood=None,
    address_zip_code=None,
    address_city=None,
    address_state=None,
    role="user"
)
print("User creado correctamente")

# PagedUsersResult
print("\n4) Probando el schema PagedUsersResult...")

paged = PagedUsersResult(
    total=1,
    page=1,
    limit=10,
    users=[user]
)
print("La paginación es válida")

# ApiResponse
print("\n5) Probando el schema ApiResponseUser...")
response = ApiResponseUser(
    codigo=200,
    mensaje="Usuario obtenido",
    resultado=user
)
print("El schema ApiResponseUser es válido")

# ApiError
print("\n6) Probando ApiError...")
error = ApiError(
    codigo=404,
    mensaje="Usuario no encontrado",
    resultado={"detail": "No existe"}
)
print("El schema ApiError es válido")

# CommonQueryParams
print("\n7) Probando que CommonQueryParams sea válido...")

params = CommonQueryParams(page=1, limit=10, sort="username", order="asc")
print("CommonQueryParams es válido")

print("\n8) Probando que sort  sea inválido...")
try:
    CommonQueryParams(sort="hacker")
    print("ERROR: sort inválido aceptado")
except HTTPException:
    print("sort inválido rechazado")

print("\n9) Probando order inválido...")

try:
    CommonQueryParams(order="up")
    print("ERROR: order inválido aceptado")
except HTTPException:
    print("order inválido rechazado")