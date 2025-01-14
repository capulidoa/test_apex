from sqlmodel import Session, select
from app.models.sales_models import Sales,AverageProduct,TotalSales,AveragePrice,BestSalesDay
from typing import List, Optional, Dict
from sqlalchemy import func

class SalesRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_sales(self, search_term: Optional[str] = None) -> List[AverageProduct]:
        query = self.session.query(AverageProduct)
        if search_term:
            query = query.filter(
                (AverageProduct.product.ilike(f"%{search_term}%")) | 
                (AverageProduct.category.ilike(f"%{search_term}%"))
            )
        return query.all()

    def get_sales_per_day(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[dict]:
        query = self.session.query(
            Sales.date, 
            func.sum(Sales.total_sales).label('total_sales')
        ).group_by(Sales.date)
        if start_date:
            query = query.filter(Sales.date >= start_date)
        if end_date:
            query = query.filter(Sales.date <= end_date)
        return query.all()
    
    def get_sales_metrics(self) -> List[Dict]:
        statement = select(
            TotalSales.category,
            TotalSales.total_sales,
            AveragePrice.average_price,
            BestSalesDay.daily_sales
        ).join(
            AveragePrice, TotalSales.category == AveragePrice.category
        ).join(
            BestSalesDay, TotalSales.category == BestSalesDay.category
        )
        results = self.session.execute(statement).fetchall()
        return results

    def get_sales_outliers(self):
        statement = select(Sales).where(Sales.outliers == True)
        return self.session.exec(statement).all()
