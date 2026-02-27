from pwdlib import PasswordHash
from app.models import *
from app.database import get_session
from sqlmodel import select
from datetime import timedelta, datetime, timezone
from app.database import SessionDep
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
import jwt
from jwt.exceptions import InvalidTokenError

SECRET_KEY = "ThisIsAnExampleOfWhatNotToUseAsTheSecretKeyIRL"
ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()

# Converts plaintext password to encrypted password
def encrypt_password(password:str):
    return password_hash.hash(password)

# Verifies if a plaintext password, when encrypted, gives the same output as the expected encrypted password
def verify_password(plaintext_password:str, encrypted_password):
    return password_hash.verify(password=plaintext_password, hash=encrypted_password)

# This takes some information and converts it into a JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Gets the current user who is making the request
async def get_current_user(request:Request, db:SessionDep)->User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    auth_header = request.headers.get("Authorization")
    auth_cookie = request.cookies.get("access_token")

    token = None
    if auth_header and auth_header.startswith("Bearer "): # Regular auth
        token = auth_header.split(" ")[1]
    elif auth_cookie: # Web auth
        token = auth_cookie.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub",None)
    except InvalidTokenError:
        raise credentials_exception
    user = db.get(User,user_id)

    if user is None:
        raise credentials_exception
    return user

async def is_logged_in(request: Request, db:SessionDep):
    try:
        await get_current_user(request, db)
        return True
    except Exception as e:
        print(e)
        return False

IsUserLoggedIn = Annotated[bool, Depends(is_logged_in)]
AuthDep = Annotated[User, Depends(get_current_user)]

async def is_admin(user:User):
    return user.role == "admin"

async def is_admin_dep(user: AuthDep):
    if not await is_admin(user):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "You are not authorized to access this page",
        )
    return user

AdminDep = Annotated[User, Depends(is_admin_dep)]