from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base

# BigInteger PKs are mapped to Integer for SQLite (used in tests) while
# remaining BigInteger for production databases (PostgreSQL/MySQL).
_BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class FeedbackCategory(Base):
    __tablename__ = "feedback_categories"

    id = Column(_BigIntPK, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    feedbacks = relationship("CustomerFeedbackForm", back_populates="category")


class CustomerFeedbackForm(Base):
    __tablename__ = "customer_feedback_forms"

    id = Column(_BigIntPK, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    feedback_category_id = Column(BigInteger, ForeignKey("feedback_categories.id"), nullable=True)
    rating = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    category = relationship("FeedbackCategory", back_populates="feedbacks")
    files = relationship("FileUpload", back_populates="feedback_form", cascade="all, delete-orphan")


class FileUpload(Base):
    __tablename__ = "file_uploads"

    id = Column(_BigIntPK, primary_key=True, index=True)
    customer_feedback_id = Column(BigInteger, ForeignKey("customer_feedback_forms.id"), nullable=False)
    name = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    feedback_form = relationship("CustomerFeedbackForm", back_populates="files")
