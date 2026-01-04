from app.db.session import SessionLocal
from app.db.models import Customer
import uuid

def seed():
    db = SessionLocal()
    try:
        kunde = Customer(
            uuid=uuid.uuid4(),
            name="Beispiel GmbH",
            adresse="Musterstraße 1, 12345 Musterstadt, DE",
            standard_currency="EUR",
            company_number="HRB 12345",
            vat_number="DE123456789",
            tax_number="12/345/67890"
        )
        db.add(kunde)
        db.commit()
        print("Kunde wurde angelegt!")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
