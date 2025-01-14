# main.py

from fastapi import FastAPI
from app.routes.sales_routes import router as sales_router
from app.database import create_db, get_session

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db() 

app.include_router(sales_router)

