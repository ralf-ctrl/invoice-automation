import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
    name = Column(String, nullable=False)
    adresse = Column(String, nullable=False)
    standard_currency = Column(String, nullable=False)
    company_number = Column(String, nullable=True)
    vat_number = Column(String, nullable=True)
    tax_number = Column(String, nullable=True)
    invoices = relationship("Invoice", back_populates="customer")

class Invoice(Base):
    __tablename__ = "invoice"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
    nummer = Column(String, nullable=False)
    monat = Column(String, nullable=False)
    kunde_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    gesamtbetrag = Column(Numeric, nullable=True)
    zielwaehrung = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Entwurf")
    customer = relationship("Customer", back_populates="invoices")
    positions = relationship("InvoicePosition", back_populates="invoice")

class InvoicePosition(Base):
    __tablename__ = "invoice_position"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=False)
    beschreibung = Column(String, nullable=False)
    menge = Column(Numeric, nullable=False)
    einzelpreis = Column(Numeric, nullable=False)
    waehrung = Column(String, nullable=False)
    attachment_path = Column(String, nullable=True)
    invoice = relationship("Invoice", back_populates="positions")

class ExchangeRate(Base):
    __tablename__ = "exchange_rate"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
    datum = Column(DateTime, nullable=False)
    von = Column(String, nullable=False)
    nach = Column(String, nullable=False)
    kurs = Column(Numeric, nullable=False)
class PositionTemplate(Base):
    __tablename__ = "position_template"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    name = Column(String, nullable=False)  # z.B. "Beratung"
    beschreibung = Column(String, nullable=False)
    standard_menge = Column(Numeric, nullable=False, default=1)
    einzelpreis = Column(Numeric, nullable=False)
    waehrung = Column(String, nullable=False, default="EUR")
    attachment_path = Column(String, nullable=True)
