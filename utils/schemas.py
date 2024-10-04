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