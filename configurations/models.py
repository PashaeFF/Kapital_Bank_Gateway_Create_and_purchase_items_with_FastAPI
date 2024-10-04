from sqlalchemy import Column, Integer, Boolean, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from configurations.database import Base
from datetime import datetime


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)

    name = Column(String(150), nullable=False, unique=True)
    price = Column(Float, nullable=False, default=0.0)

    payment = relationship("PaymentData", back_populates="item", cascade="all, delete-orphan")
    item_order = relationship("ItemOrder", back_populates="item", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.now())


class ItemOrder(Base):
    __tablename__ = "item_order"

    id = Column(Integer, primary_key=True)

    successfully_paid = Column(Boolean, default=False)
    bank_installment_paid = Column(Boolean, default=False)
    bank_installment_month = Column(Integer, default=0)

    item_id = Column(Integer(), ForeignKey("item.id", ondelete='CASCADE'), nullable=True)
    item = relationship("Item", back_populates="item_order") 



class PaymentData(Base):
    __tablename__ = "payment_data"

    id = Column(Integer, primary_key=True)

    order_id = Column(Integer(), nullable=False),
    currency = Column(String(), nullable=False)
    order_status = Column(String(), nullable=False),
    amount = Column(Float(), nullable=False, default=0.0)
    order_type= Column(String(), nullable=False),

    item_id = Column(Integer(), ForeignKey("item.id", ondelete='CASCADE'), nullable=True)
    item = relationship("Item", back_populates="payment") 

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.now())