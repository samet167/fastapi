from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    image = Column(String, nullable=False)

    # 🔑 បង្កើត ForeignKey ចងជើងជាមួយតារាង categories
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)

    # 🔗 បង្កើតផ្លូវលីងទិន្នន័យត្រឡប់ទៅរក Category វិញ
    category = relationship("Category", back_populates="items")