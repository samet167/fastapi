from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base  # ប្រាកដថាផ្លូវទៅរក Base ក្នុង database.py ត្រឹមត្រូវ

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    
    # 🔒 កែសម្រួល៖ ប្រើ String ទទេ (មិនបាច់ដាក់លេខកំណត់ប្រវែង) ដើម្បីផ្ទុកកូដ Hash របស់ Argon2 បានដោយសុវត្ថិភាព
    password = Column(String, nullable=False)
    
    # 🛡️ បន្ថែមថ្មី៖ កូឡោនសម្រាប់បែងចែកសិទ្ធិ (លំនាំដើមគឺ "user" ហើយអាចដូរទៅ "admin" ក្នុង DB បាន)
    role = Column(String(50), default="user", nullable=False)
    
    # 📅 ប្រព័ន្ធពិនិត្យមើលថ្ងៃបង្កើតគណនី (លំអាប់អូតូ)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())