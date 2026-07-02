from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, paid, shipped, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # រក្សាតម្លៃទុក ក្រែងលោថ្ងៃក្រោយទំនិញឡើង/ចុះថ្លៃ

    order = relationship("Order", back_populates="items")
    item = relationship("Item")