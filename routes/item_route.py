from fastapi import (APIRouter, Depends, Request, 
                     Form, Query, UploadFile)
from sqlalchemy.orm import Session

from fastapi.responses import JSONResponse
from configurations import models, database
from utils import schemas
from utils.helper import *
from typing import List

item_route = APIRouter("/items")


@item_route.post("/add-item")
async def add_item(db: Session = Depends(database.get_db),
                   name: str = Form(..., max_length=150),
                   price: float = Form(...)):
    check_item_name = check_item_in_the_db(name, db)
    if check_item_name:
        return JSONResponse("Name exists", status_code=409)
    data = create_item_data(name=name, price=price)
    new_item = add_item_in_the_db(db, name=name, price=price)
    if new_item:
        return new_item
    return JSONResponse(data, status_code=200)


@item_route.post("/get-items", response_model=List[schemas.Item])
def get_items(db: Session = Depends(database.get_db),
              limit: int = Query(10, description="Number of items per page"),
              offset: int = Query(0, description="Offset for pagination (starting item)")
              ):
    return db.query(models.Item).offset(offset).limit(limit).all()
