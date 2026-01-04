import uuid
from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.models import Invoice, InvoicePosition

def generate_invoice_number(db: Session) -> str:
    """Generiert eine einfache fortlaufende Rechnungsnummer."""
    last_invoice = db.query(Invoice).order_by(Invoice.id.desc()).first()
    if last_invoice and last_invoice.nummer.isdigit():
        return str(int(last_invoice.nummer) + 1).zfill(5)
    return "00001"

def create_invoice_with_positions(
    db_session: Session,
    customer,
    year: int,
    month: int,
    positions: list[dict]
) -> Invoice:
    """Erstellt eine Rechnung und die zugehörigen Positionen."""
    # Rechnungsnummer und Bezeichner
    invoice_number = generate_invoice_number(db_session)
    invoice = Invoice(
        uuid=uuid.uuid4(),
        nummer=invoice_number,
        monat=f"{year:04d}-{month:02d}",
        kunde_id=customer.id,
        zielwaehrung=customer.standard_currency,
        status="Entwurf",
    )
    db_session.add(invoice)
    db_session.flush()  # erzeugt invoice.id

    total = Decimal("0.0")
    for pos in positions:
        # ggf. Währungsumrechnung einbauen
        betrag = Decimal(pos["menge"]) * Decimal(pos["einzelpreis"])
        total += betrag
        invoice_position = InvoicePosition(
            uuid=uuid.uuid4(),
            invoice_id=invoice.id,
            beschreibung=pos["beschreibung"],
            menge=Decimal(pos["menge"]),
            einzelpreis=Decimal(pos["einzelpreis"]),
            waehrung=pos["waehrung"],
            attachment_path=pos.get("attachment_path"),
        )
        db_session.add(invoice_position)

    invoice.gesamtbetrag = total
    invoice.status = "versendet"  # Beispielstatus
    db_session.commit()
    db_session.refresh(invoice)
    return invoice
