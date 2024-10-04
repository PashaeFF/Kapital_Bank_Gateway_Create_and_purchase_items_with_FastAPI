from fastapi import FastAPI
from configurations import models, database
from routes import item_route, payment_route

models.Base.metadata.create_all(database.engine)

app = FastAPI(
    title="KapitalBank Payment",
    version="v1.0"
)


app.include_router(item_route)




