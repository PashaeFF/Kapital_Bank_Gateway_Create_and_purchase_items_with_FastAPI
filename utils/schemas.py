from pydantic import BaseModel, Field

class Item(BaseModel):
    id: int
    name: str = Field(..., max_length=150)
    price: float = Field(...)

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