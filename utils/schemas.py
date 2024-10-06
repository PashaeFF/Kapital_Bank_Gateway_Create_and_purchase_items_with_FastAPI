from pydantic import BaseModel, Field

class Item(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        schema_extra = {
            "example": {
                "name": "Item",
                "price": 19.99
            }
        }


class Orders(BaseModel):
    id: int
    successfully_paid: bool
    bank_installment_paid: bool
    bank_installment_month: int


class PayOrders(BaseModel):
    id: int
    order_object_id:int
    order_status: str