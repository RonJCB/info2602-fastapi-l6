from fastapi import APIRouter, HTTPException, Depends, Request, Response, Form,Query
from sqlmodel import func, select
from app.database import SessionDep
from app.models import *
from app.utilities import flash
from app.auth import *
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status
from . import templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.utilities import flash
from . import templates

from app.pagination import Pagination
admin_router = APIRouter(tags =["Admin App"])

@admin_router.get("/admin")
def admin_page(request:Request, db:SessionDep, user:AdminDep,
    page: int = Query(default=1, ge=1), limit: int = Query(default=100, le=100)):
    todos = db.exec(select(Todo)).all()

    offset = (page - 1) * limit

    count_todos = db.exec(select(func.count(Todo.id))).one()
    todos = db.exec(select(Todo).offset(offset).limit(limit)).all()
    pagination = Pagination(total_count=count_todos, current_page=page, limit=limit)

    return templates.TemplateResponse(
        request = request,
        name = "admin.html",
        context={
            "current_user":user,
            "todos": todos,
            "pagination":pagination
            }
    )