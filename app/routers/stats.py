from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import *
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status
from . import templates

stats_router = APIRouter()

@stats_router.get("/stats", response_class=HTMLResponse)
async def stats_page(
    request: Request,
    user: AdminDep
):
    return templates.TemplateResponse(
        request=request, 
        name="stats.html",
        context={
            "request": request,
            "current_user": user
        }
    )

@stats_router.get("/todo-stats")
async def stats_page(
    request: Request,
    user: AdminDep,
    db: SessionDep
):
    todos = db.exec(select(Todo)).all()
    res = {}
    for todo in todos:
        if todo.user.username in res:
            res[todo.user.username] += 1
        else:
            res[todo.user.username] = 1
    return res
    