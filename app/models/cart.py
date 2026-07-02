from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)

    # 🔗 ភ្ជាប់ទំនាក់ទំនងដើម្បីទាញទិន្នន័យទំនិញមកបង្ហាញផ្ទាល់
    item = relationship("Item")