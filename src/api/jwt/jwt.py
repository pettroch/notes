import jwt
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from typing import Union

from api.jwt.config import SECRET_KEY, ALGORITHM
from api.schemes.jwt import TokenData


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt



def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(**payload)
    except jwt.PyJWTError:
        return None


def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        user_id: int = payload.get("id")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return TokenData(username=username, id=user_id)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    