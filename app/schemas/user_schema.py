from pydantic import BaseModel, EmailStr
from typing import Optional

# --- ១. សម្រាប់ទទួលទិន្នន័យពេលចុះឈ្មោះថ្មី (Register Request) ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str  # 🔑 ថែមបន្ទាត់នេះ ដើម្បីឱ្យភ្ញៀវវាយ Password ពេល Register ចូលមក
    role: str

# --- ២. សម្រាប់ទទួលទិន្នន័យពេល Update (User Update Request) ---
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None  # 🔒 ថែមសម្រាប់ករណី User ចង់ប្តូរលេខសម្ងាត់ថ្មីថ្ងៃក្រោយ
    role: Optional[str] = None      # 🛡️ ថែមសម្រាប់ករណី Admin ចង់ប្តូរ Role ឱ្យ User

# --- ៣. សម្រាប់បោះទិន្នន័យត្រឡប់ទៅ Frontend វិញ (User Response) ---
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str  # 🛡️ បង្ហាញសិទ្ធិ (admin/user) ទៅកាន់អេក្រង់ច្បាស់លាស់

    class Config:
        from_attributes = True  # អនុញ្ញាតឱ្យបំលែងទិន្នន័យពី SQLAlchemy Object មកជា JSON អូតូ