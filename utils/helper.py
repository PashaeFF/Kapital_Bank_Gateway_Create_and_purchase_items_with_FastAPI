from fastapi.responses import JSONResponse
from configurations import models

def check_item_in_the_db(name, db):
    return db.query(models.Item).filter(models.Item.name==name).first()


def create_item_data(**kwargs):
    data = {"name":kwargs["name"],
            "price":kwargs["price"]}
    return data


def add_item_in_the_db(db, **kwargs):
    try:
        new_item = models.Item(name=kwargs["name"], price=kwargs["price"])
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except Exception as err:
        return JSONResponse(str(err), status_code=400)