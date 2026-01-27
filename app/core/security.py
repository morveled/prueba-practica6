import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.core.config import settings


def get_password_hash(password: str) -> str:
    """Convierte texto plano en un hash seguro usando bcrypt 5.0.0+"""
    # Convertimos el string a bytes
    pwd_bytes = password.encode('utf-8')
    # Generamos la sal (salt)
    salt = bcrypt.gensalt()
    # Generamos el hash
    hash_bytes = bcrypt.hashpw(pwd_bytes, salt)
    # Lo devolvemos como string para guardarlo en la DB
    return hash_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash almacenado"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

# ========== JWT TOKEN ==========
def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Crea un token JWT de acceso.
    
    Args:
        data: Diccionario con los datos a incluir en el token (claims)
              Ejemplo: {"sub": "user_id", "email": "user@example.com"}
        expires_delta: Tiempo de expiración del token (opcional)
                      Si no se proporciona, usa el valor por defecto de config
    
    Returns:
        str: Token JWT codificado
    
    Example:
        >>> token_data = {"sub": str(user.id), "email": user.email}
        >>> token = create_access_token(token_data)
    """
    to_encode = data.copy()
    
    # Calcular tiempo de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Usar tiempo por defecto desde config (ej: 30 minutos, 24 horas, etc.)
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Agregar claims estándar
    to_encode.update({
        "exp": expire,  # Tiempo de expiración
        "iat": datetime.utcnow()  # Issued at (emitido en)
    })
    
    # Codificar token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica y valida un token JWT.
    Args:
        token: Token JWT a decodificar
    Returns:
        Optional[Dict[str, Any]]: Payload del token si es válido, None si es inválido
    Raises:
        JWTError: Si el token es inválido o ha expirado
    Example:
        >>> payload = decode_access_token(token)
        >>> user_id = payload.get("sub")
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Crea un token JWT de refresco (opcional, para refresh token pattern).
    Args:
        data: Diccionario con los datos a incluir en el token
        expires_delta: Tiempo de expiración del token (opcional)
    
    Returns:
        str: Token JWT de refresco
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Refresh tokens suelen durar más (ej: 7 días, 30 días)
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"  # Identificar como refresh token
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:  # puede lanzar JWTError. lo uso para act un usuario completo
    """Verifica y decodifica un token JWT.
    Args:
        token: Token JWT a verificar
    Returns:
        Dict[str, Any]: Payload del token si es válido
    Raises:
        JWTError: Si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise e

