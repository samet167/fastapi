from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from app.models.user import User
from app.models.item import Item
from app.models.category import Category

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    return {
        "total_users": db.query(func.count(User.id)).scalar() or 0,
        "total_items": db.query(func.count(Item.id)).scalar() or 0,
        "total_categories": db.query(func.count(Category.id)).scalar() or 0,
        "total_value": float(db.query(func.sum(Item.price)).scalar() or 0.0),
    }

@router.get("/chart-data")
def get_chart_data(db: Session = Depends(get_db)):
    # គណនាចំនួនទំនិញតាម Category
    results = db.query(Category.name, func.count(Item.id)).join(Item).group_by(Category.name).all()
    return [{"name": name, "views": count} for name, count in results]