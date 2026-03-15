from fastapi import APIRouter, HTTPException, Depends, Request, Response, Form
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import encrypt_password, verify_password, create_access_token, AuthDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.utilities import flash
from . import templates


todo_router = APIRouter(tags=["Todo Management"])

@todo_router.post("/todos")
def create_todo_action(request: Request, text: Annotated[str, Form()], db:SessionDep, user:AuthDep):
    user.todos.append(Todo(text=text))
    db.add(user)
    db.commit()
    flash(request, "Item created successfully")
    return RedirectResponse(url="/app", status_code=status.HTTP_303_SEE_OTHER)

@todo_router.post('/toggle/{id}')
async def toggle_todo_action(request: Request, id: int, db:SessionDep, user:AuthDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        flash('Invalid id or unauthorized')
    else:
        todo.done = not todo.done
        db.add(todo)
        db.commit()
        flash(request, f'Todo { "done" if todo.done else "not done" }!')
    
    return RedirectResponse(url=request.url_for('app_dashboard'), status_code=status.HTTP_303_SEE_OTHER)


@todo_router.post('/editTodo/{id}')
def edit_todo_action(request: Request, id: int, text: Annotated[str, Form()], db:SessionDep, user:AuthDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        flash(request, 'Invalid id or unauthorized')
    else:
        todo.text = text
        db.add(todo)
        db.commit()
        flash(request, f'Todo updated!')
    return RedirectResponse(url=request.url_for('app_dashboard'), status_code=status.HTTP_303_SEE_OTHER)

@todo_router.get('/deleteTodo/{id}')
def delete_todo_action(request: Request, id: int, db:SessionDep, user:AuthDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    todos = []
    if not todo:
        flash(request, 'Invalid id or unauthorized')
    else:
        db.delete(todo)
        db.commit()
        flash(request, 'Deleted successfully')

    return RedirectResponse(url=request.url_for('app_dashboard'), status_code=status.HTTP_303_SEE_OTHER)

@todo_router.get('/editTodo/{id}')
def edit_todo_page(request: Request, id: int, db:SessionDep, user:AuthDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    todos = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).all()

    if not todo:
        flash(request, 'Invalid id or unauthorized')
    else:
        todos = user.todos
    
    return templates.TemplateResponse(
        request=request, 
        name="edit.html",
        context={
            "current_user": user,
            "todo": todo,
            "todos": todos
        }
    )