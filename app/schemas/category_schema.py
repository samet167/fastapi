from pydantic import BaseModel

# Schema មូលដ្ឋាន
class CategoryBase(BaseModel):
    name: str

# Schema សម្រាប់ទទួលទិន្នន័យពេលបង្កើតថ្មី
class CategoryCreate(CategoryBase):
    pass

# ✨ ថែម Class នេះចូល ដើម្បីដោះស្រាយ Error អម្បាញ់មិញ
class CategoryUpdate(CategoryBase):
    pass

# Schema សម្រាប់បោះទិន្នន័យទៅឱ្យ Client វិញ
class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True  # ឬ orm_mode = True សម្រាប់ Pydantic v1