from datetime import datetime, timedelta
import os
from typing import Optional
import bcrypt
import jwt
import hashlib

SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days defaults

def _pre_hash(password: str) -> str:
    # Bcrypt limits passwords to 72 bytes. 
    # Pre-hashing with SHA256 lets us support arbitrarily long passwords securely.
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pre_hashed = _pre_hash(plain_password).encode('utf-8')
    return bcrypt.checkpw(pre_hashed, hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    pre_hashed = _pre_hash(password).encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pre_hashed, salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
