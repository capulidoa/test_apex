from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from typing import Optional

class Sales(SQLModel, table=True):
    transaction_id: int | None = Field(primary_key=True)
    date: str
    category: str
    product: str
    quantity: float
    price: float
    total_sales: float
    day_of_week: str
    high_volume: bool
    outliers: Optional[bool] = None

    __tablename__ = "sales"
    class Config:
        orm_mode = True 

class AverageProduct(SQLModel, table=True):
    category: str = Field(index=True, primary_key=True)
    product: str = Field(index=True, primary_key=True)
    average_price: float | None
    total_sales: float

    __tablename__ = "average_product" 

class TotalSales(SQLModel, table=True):
    category: str = Field(primary_key=True, index=True)
    total_sales: float

    __tablename__ = "total_sales" 

class AveragePrice(SQLModel, table=True):
    category: str = Field(primary_key=True, index=True)
    average_price: float

    __tablename__ = "average_price" 

class BestSalesDay(SQLModel, table=True):
    category: str = Field(primary_key=True, index=True)
    date: str
    daily_sales: str

    __tablename__ = "best_sales_day" 
