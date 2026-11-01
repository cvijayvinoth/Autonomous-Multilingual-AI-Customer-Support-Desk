"""SQLAlchemy Database Schema for Support Desk with Threaded Messages."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    customer_name = Column(String(100), default="Anonymous")
    customer_email = Column(String(150), default="", index=True)
    detected_language = Column(String(50), default="English")
    category = Column(String(50), default="Other")
    urgency = Column(String(20), default="Medium")
    sentiment = Column(String(30), default="Neutral")
    status = Column(String(30), default="Resolved")  # Resolved, Escalated, Human Resolved
    escalation_reason = Column(Text, default="None")

    # One-to-many threaded messages relationship
    messages = relationship(
        "TicketMessage",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketMessage.timestamp.asc()",
    )


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(50), ForeignKey("tickets.ticket_id"), nullable=False, index=True)
    sender = Column(String(50), nullable=False)  # 'Customer', 'AI_Assistant', 'Human_Agent'
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    ticket = relationship("Ticket", back_populates="messages")


class KBDeficiency(Base):
    __tablename__ = "kb_deficiencies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    query = Column(String(255), nullable=False)
    customer_name = Column(String(100), default="")
    notes = Column(Text, default="")


def init_db(db_url: str = "sqlite:///database/support_desk.db"):
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)