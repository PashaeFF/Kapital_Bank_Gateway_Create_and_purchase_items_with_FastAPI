from fastapi import FastAPI
from pydantic import BaseModel
from configurations import models, database

models.Base.metadata.create_all(database.engine)

app = FastAPI()


class Item(BaseModel):
    id: int
    name: str
    price: float

