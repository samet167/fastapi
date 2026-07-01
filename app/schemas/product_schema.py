from pydantic import BaseModel
from typing import Optional

# 1. សម្រាប់ទទួលទិន្នន័យពេលបង្ហោះទំនិញថ្មី
class ProductCreate(BaseModel):
    name: str
    description: str
    price: int
    quantity: int
    image: str

# 2. សម្រាប់ទទួលទិន្នន័យពេលកែប្រែ (Update)
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    quantity: Optional[int] = None
    image: Optional[str] = None

# 3. សម្រាប់បោះទិន្នន័យទំនិញទៅបង្ហាញលើអេក្រង់វិញ
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    quantity: int
    image: str

    class Config:
        from_attributes = True