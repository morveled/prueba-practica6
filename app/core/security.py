import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from app.core.config import settings
from app.schemas.auth import TokenData


def get_password_hash(password: str) -> str:
    """Convierte texto plano en un hash seguro usando bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hash_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash almacenado."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un access token JWT firmado.
    Incluye el claim 'token_type': 'access' para diferenciarlo del refresh token.
    """
    to_encode = data.copy()
    to_encode["token_type"] = "access"

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un refresh token JWT firmado.
    Por defecto expira en REFRESH_TOKEN_EXPIRE_DAYS (configurado en settings).
    """
    to_encode = data.copy()
    to_encode["token_type"] = "refresh"

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, expected_type: str = "access") -> Optional[TokenData]:
    """
    Decodifica y valida un token JWT.
    Retorna TokenData si es válido, None si es inválido o expirado.

    Args:
        token: El token JWT a verificar.
        expected_type: Tipo esperado ('access' o 'refresh').
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        token_type: str = payload.get("token_type", "")
        if token_type != expected_type:
            return None

        sub: str = payload.get("sub")
        if sub is None:
            return None

        return TokenData(
            sub=sub,
            username=payload.get("username"),
            role=payload.get("role"),
            is_superuser=payload.get("is_superuser", False),
            token_type=token_type,
        )
    except JWTError:
        return None

