from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import bcrypt
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# JWT
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=settings.JWT_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    
    # Convert 'sub' to string (jose requires it)
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    logger.info(f"Created token with sub={to_encode.get('sub')}, secret_length={len(settings.JWT_SECRET)}")
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        logger.info(f"Successfully decoded token, sub={payload.get('sub')}")
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}, secret_length={len(settings.JWT_SECRET)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}")
        return None
