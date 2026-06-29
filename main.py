import json
import os.path
from datetime import date
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from resources import EntryManager, Entry
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="To-Do Backend",
              description="Бэкенд для списка дел")

origins = [
    "https://wexler.io"  # адрес на котором работает фронт-энд
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # Список разрешенных доменов
    allow_credentials=True,   # Разрешить Cookies и Headers
    allow_methods=["*"],      # Разрешить все HTTP методы
    allow_headers=["*"],      # Разрешить все хедеры
)


class User(BaseModel):
    first_name: str
    last_name: str
    birthday: date


class Settings(BaseSettings):
    data_folder: str = '/Users/viktor/Egor_Vexler_Course/todo_list_backend/data'

settings = Settings()

@app.post("/add_user")
def add_user(user: User) -> User:
    """
    Создает новых юзеров
    """
    with open(f"{user.first_name}.json", "w") as f:
        f.write(user.model_dump_json())
    return user

@app.get("/ger_user",
         responses={
             404: {"description": "Пользователь не найден"}
         })
def get_user(username: str) -> User:
    """
    Возвращает имеющихся юзеров
    """
    filename = f"{username}.json"
    if not os.path.isfile(filename):
        raise HTTPException(status_code= 404,
                            detail=f"пользователь {username} не найден")
    with open(filename, "r") as f:
        data = json.load(f)
        user = User(**data)
        return user

@app.get("/hello_world")
async def hello_world(name: str = None) -> dict:
    """
    Возвращает Hello + name
    """
    return {"hello": name}

@app.get("/api/entries/")
async def get_entries():
    """
    Возвращает массив записи EntryManager
    """
    entry_manager =EntryManager(settings.data_folder)
    entry_manager.load()
    result = []
    for entry in entry_manager.entries:
        result.append(entry.json())
    return result

@app.post("/api/save_entries/")
async def save_entries(data: List[dict]):
    entry_manager = EntryManager(settings.data_folder)
    for entry_data in data:
        entry = Entry.from_json(entry_data)
        entry_manager.entries.append(entry)
    entry_manager.save()
    return {'status': 'success'}


@app.get('/api/get_data_folder/')
async def get_data_folder():
    """
    Возвращает путь к папке Data
    """
    return {
        "folder": settings.data_folder
    }

@app.delete("/api/delete_entries/",
            responses={
             404: {"description": "Запись не найден"}
         })
async def delete_entries(entry: str):
    """
    Удаляет сущность по названию
    """
    entry_manager = EntryManager(settings.data_folder).load()

    success = entry_manager.delete(entry)
    if not success:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"status": "success", "message": f"Запись {entry} удалена"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)





