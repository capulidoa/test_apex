from typing import List, Optional,Dict
from app.repositories.sales_repository import SalesRepository
from app.models.sales_models import Sales, AverageProduct

class SalesUseCase:
    def __init__(self, repository: SalesRepository):
        self.repository = repository

    def get_sales(self, search_term: Optional[str] = None) -> List[Sales]:
        return self.repository.get_sales(search_term)

    def get_sales_per_day(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        return self.repository.get_sales_per_day(start_date, end_date)

    def get_sales_metrics(self) -> List[Dict]:
        results = self.repository.get_sales_metrics()
        metrics = [
            {
                "category": result[0],
                "total_revenue": result[1],
                "average_price": result[2],
                "max_sales_day": result[3]
            }
            for result in results
        ]
        return metrics

    def get_sales_outliers(self):
        return self.repository.get_sales_outliers()
