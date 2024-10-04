from fastapi import (APIRouter, Depends, Request, 
                     Form, Query, UploadFile)
from sqlalchemy.orm import Session

from fastapi.responses import JSONResponse
from configurations import models, database
from utils import schemas
from utils.helper import *
from typing import List
from payment import KapitalPayment, NewOrderObject
import os

payment_route = APIRouter(prefix="/payment")


def check_the_existing_item(item_id, db):
    return db.query(models.Item).filter(models.Item.id==item_id).first()


def create_new_order_object(item_id, price, bank_installment_paid, bank_installment_month, db):
    try:
        new_object = models.ItemOrder(item_id=item_id, 
                                      bank_installment_paid=bank_installment_paid,
                                      bank_installment_month=bank_installment_month,
                                      price=price)
        db.add(new_object)
        db.commit()
        db.refresh(new_object)
        return new_object
    except Exception as err:
        return JSONResponse(str(err), status_code=400)



@payment_route.post("/buy-the-item/{item_id}")
async def buy_the_item(item_id:int, db: Session = Depends(database.get_db),
                       bank_installment_paid: bool = Form(...), 
                       bank_installment_month: int = Form(...)):
    pay_order_object = NewOrderObject()
    item = check_the_existing_item(item_id, db)
    if not item:
        return JSONResponse("Item not found", status_code=404)
    created_object = create_new_order_object(item_id=item_id, 
                                             price=item.price,
                                             bank_installment_paid=bank_installment_paid,
                                             bank_installment_month=bank_installment_month,
                                             db=db)
    host = os.getenv("BACKEND_HOST")
    redirect_page = f"{host}/payment/item/{item_id}"
    pay_order = pay_order_object.create_order(
            redirect_page=redirect_page,
            package_object=item, 
            created_object=created_object, 
            payment_model=models.PaymentData, 
            subscribe_id=item.id,
            db=db)
    return pay_order


@payment_route.get("/orders", response_model=List[schemas.Orders])
def get_items(db: Session = Depends(database.get_db),
              limit: int = Query(10, description="Number of items per page"),
              offset: int = Query(0, description="Offset for pagination (starting item)")
              ):
    return db.query(models.ItemOrder).offset(offset).limit(limit).all()
