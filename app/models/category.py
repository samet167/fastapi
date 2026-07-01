from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # 🔗 បង្កើតទំនាក់ទំនងទៅកាន់តារាង Item (តារាងកូន)
    items = relationship("Item", back_populates="category", cascade="all, delete-orphan")