from pydantic import BaseModel
from app.schemas.item_schema import ItemResponse

class CartItemCreate(BaseModel):
    item_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    quantity: int
    item: ItemResponse  # ✅ បោះទិន្នន័យផលិតផល (ឈ្មោះ, តម្លៃ, រូបភាព) ទៅឱ្យ Frontend តែម្តង

    class Config:
        from_attributes = True