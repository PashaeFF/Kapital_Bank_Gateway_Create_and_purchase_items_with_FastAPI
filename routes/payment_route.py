from fastapi import (APIRouter, Depends, Request, 
                     Form, Query, UploadFile)
from sqlalchemy.orm import Session

from fastapi.responses import JSONResponse
from configurations import models, database
from utils import schemas
from utils.helper import *
from typing import List
from payment import KapitalPayment
import os

payment_route = APIRouter(prefix="/payment")


def check_the_existing_item(item_id, db):
    return db.query(models.Item).filter(models.Item.id==item_id).first()


def create_new_order_object(item_id, db):
    try:
        new_object = models.ItemOrder(item_id=item_id)
        db.add(new_object)
        db.commit()
        db.refresh(new_object)
    except Exception as err:
        return JSONResponse(str(err), status_code=400)


@payment_route.post("/buy-the-item/{item_id}")
async def buy_the_item(item_id:int, db: Session = Depends(database.get_db)):
    item = check_the_existing_item(item_id, db)
    if not item:
        return JSONResponse("Item not found", status_code=404)
    
    host = os.getenv("BACKEND_HOST")
    redirect_page = f"{host}/payment/item/{item_id}"
    
    # data = KapitalPayment.check_installment_or_cash_order(created_object, redirect_page, price, subscribe_id)
    return JSONResponse("ok", status_code=200)


@payment_route.get("/orders", response_model=List[schemas.Orders])
def get_items(db: Session = Depends(database.get_db),
              limit: int = Query(10, description="Number of items per page"),
              offset: int = Query(0, description="Offset for pagination (starting item)")
              ):
    return db.query(models.ItemOrder).offset(offset).limit(limit).all()
