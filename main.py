from fastapi import FastAPI, Depends, HTTPException, Response, status
from typing import List, Annotated, Optional
from models import Base, engine, ToDoItem, SessionLocal, ToDoItemCreate, ToDoItemResponse
from sqlalchemy.orm import Session
import pandas as pd
import io
from fastapi.security import HTTPBasic, HTTPBasicCredentials

def create_tables():
    Base.metadata.create_all(bind=engine)
create_tables()

app = FastAPI()

security = HTTPBasic()

# type hinting that the todo_list is a list of ToDoItems, then initialize to an empty list
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_all_todos(db: Session):
    return db.query(ToDoItem).all()

def get_non_completed_todos(db: Session):
    return db.query(ToDoItem).filter(ToDoItem.completed == False).all()

def get_num_entries(db: Session):
    num_entries = db.query(ToDoItem).count()
    return num_entries

@app.post("/todos/", response_model=ToDoItemResponse, status_code=201)
def create_todo(todo: ToDoItemCreate, db: Session = Depends(get_db)):
    db_item = ToDoItem(title=todo.title, description=todo.description, completed=todo.completed)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/todos/", response_model=List[ToDoItemResponse], status_code=200)
def return_todos(retrieve_all_todos: Optional[bool] = False, db: Session = Depends(get_db)):
    if retrieve_all_todos:
        return get_all_todos(db)
    db_todo_items = get_non_completed_todos(db)
    num_entries = get_num_entries(db)
    if num_entries > 0:
        if db_todo_items:
            return db_todo_items
        else:
            raise HTTPException(status_code=404, detail="All todos are completed")
    else:
        raise HTTPException(status_code=404, detail="ToDoList is empty")

@app.put("/todos/{title}", status_code=200, response_model=ToDoItemResponse)
def complete_todo(title: str, db: Session = Depends(get_db)):
    fetched_item = db.query(ToDoItem).filter(ToDoItem.title.ilike(title.strip())).first()
    if fetched_item is None:
        raise HTTPException(status_code=404, detail="No todo with that title")
    if fetched_item.completed:
        raise HTTPException(status_code=404, detail="Todo is already completed")
    fetched_item.completed = True
    db.commit()

    return fetched_item

@app.delete("/todos/", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    fetched_item = db.query(ToDoItem).filter(ToDoItem.id == id)
    if fetched_item:
        db.delete(fetched_item)
        db.commit()
        return
    raise HTTPException(status_code=404, detail="ToDoItem with inputted id was not found")

@app.get("/todos/export_csv", response_class=Response)
def export_as_csv(db: Session = Depends(get_db)):
    todos = get_all_todos(db)
    # Convert each entry in the database to a dictionary and then convert it to a dataframe
    df = pd.DataFrame([todo.__dict__ for todo in todos])

    # Drop the column that is specifically for sqlalchemy
    df = df.drop('_sa_instance_state', axis=1)

    #convert dataframe to csv
    stream = io.StringIO()
    df.to_csv(stream, index=False)

    response = Response(content=stream.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=todos.csv"

    return response

@app.get("/users/me")
def read_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    return {"username": credentials.username, "password": credentials.password}