from fastapi import APIRouter, HTTPException, Depends, Request, Response, Form
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.utilities import flash
from app.auth import encrypt_password, verify_password, create_access_token, AuthDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status
from . import templates
from fastapi.responses import HTMLResponse, RedirectResponse

auth_router = APIRouter(tags=["Authentication"])

@auth_router.post("/login")
async def login_action(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
    request: Request
) -> Response:
    user = db.exec(select(User).where(User.username == form_data.username)).one_or_none()
    if not user or not verify_password(plaintext_password=form_data.password, encrypted_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": f"{user.id}", "role": user.role},)

    max_age = 1 * 24 * 60 * 60 # (1 day converted to secs)
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, max_age=max_age, samesite="lax")
    return response

@auth_router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup_user(request:Request, db:SessionDep, username: Annotated[str, Form()], email: Annotated[str, Form()], password: Annotated[str, Form()],):
    try:
        new_user = RegularUserCreate(
            username=username, 
            email=email, 
            password=encrypt_password(password)
        )
        new_user_db = User.model_validate(new_user)
        db.add(new_user_db)
        db.commit()
        flash(request, "Registration completed! Sign in now!")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(
                    status_code=400,
                    detail="Username or email already exists",
                    headers={"WWW-Authenticate": "Bearer"},
                )

@auth_router.get("/identify", response_model=UserResponse)
def get_user_by_id(db: SessionDep, user:AuthDep):
    return user


@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="login.html",
    )


@auth_router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="signup.html",
    )

@auth_router.get("/logout")
async def logout(request: Request, response: Response):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(
        key="access_token", 
        httponly=True,
        samesite="lax"
    )
   
    
    return response