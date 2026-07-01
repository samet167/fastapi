from pydantic import BaseModel
from app.schemas.category_schema import CategoryResponse  # <-- ហៅប្លង់ Category មកប្រើរួមគ្នា

# ប្លង់សម្រាប់បង្ហាញទិន្នន័យ Item ចេញទៅក្រៅ (Response)
class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    quantity: int
    image: str
    category_id: int
    category: CategoryResponse  # 🔗 វៃឆ្លាតត្រង់នេះ៖ វានឹងបង្ហាញព័ត៌មាន Category ពេញលេញមកជាមួយ Item តែម្ដង

    class Config:
        from_attributes = True
        