from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Usar bcrypt para hashing de contraseñas


def verify_password(plain_password: str, hashed_password: str) -> bool: #verifica la contraseña con hash 
    """Verifica si la contraseña coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str: #se genera el hash de la contraseña para almacenarla en la base de datos
    """Genera hash de la contraseña."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str: #crea token de acceso JWT
    """Crea un token JWT de acceso."""
    to_encode = data.copy() 
    
    if expires_delta: #si se proporciona un tiempo de expiración personalizado
        expire = datetime.utcnow() + expires_delta #se calcula la fecha de expiración
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) #si no, se usa el valor por defecto de configuración
    
    to_encode.update({"exp": expire}) #se agrega la fecha de expiración al payload del token
    encoded_jwt = jwt.encode( 
        to_encode, 
        settings.SECRET_KEY,  
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt #se retorna el token JWT generado


def decode_access_token(token: str) -> Optional[dict]: #decodifica y verifica el token JWT para autenticación
    """Decodifica y verifica un token JWT."""
    try:
        payload = jwt.decode( 
            token,  #token a verificar
            settings.SECRET_KEY, #clave secreta para verificar el token (debe coincidir con la usada para crearlo)
            algorithms=[settings.ALGORITHM] #algoritmo usado para firmar el token
        )
        return payload
    except JWTError:
        return None