from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.sales_models import AverageProduct, Sales
from app.use_cases.sales_use_case import SalesUseCase
from app.repositories.sales_repository import SalesRepository
from app.database import get_session
from sqlmodel import Session

router = APIRouter()

@router.get("/sales/product", response_model=List[AverageProduct])
def read_sales(search_term: Optional[str] = None, session: Session = Depends(get_session)) -> List[AverageProduct]:
    sales_repository = SalesRepository(session)
    sales_use_case = SalesUseCase(sales_repository)
    results = sales_use_case.get_sales(search_term)

    if not results:
        raise HTTPException(status_code=404, detail="No matching sales found")

    return results

@router.get("/sales/day", response_model=List[dict])
def get_sales_per_day(start_date: Optional[str] = None, end_date: Optional[str] = None, session: Session = Depends(get_session)):
    sales_repository = SalesRepository(session)
    sales_use_case = SalesUseCase(sales_repository)
    results = sales_use_case.get_sales_per_day(start_date, end_date)

    if not results:
        raise HTTPException(status_code=404, detail="No sales data found.")

    return [{"date": result[0], "total_sales": result[1]} for result in results]

@router.get("/sales/category", response_model=List[dict])
def get_sales_metrics(session: Session = Depends(get_session)):
    sales_repository = SalesRepository(session)
    sales_use_case = SalesUseCase(sales_repository)
    results = sales_use_case.get_sales_metrics()
    if not results:
        raise HTTPException(status_code=404, detail="No sales data found.")
    return results

@router.get("/sales/outliers", response_model=List[Sales])
async def get_sales_outliers(session: Session = Depends(get_session)):
    query = session.query(Sales)
    query = query.filter(
        (Sales.outliers == True)
    )
    results = query.all()

    if not results:
        raise HTTPException(status_code=404, detail="No outliers found.")
    return results