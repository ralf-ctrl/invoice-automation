# scripts/db_dump.py
from __future__ import annotations

from typing import Iterable
from decimal import Decimal

from app.db.session import SessionLocal
from app.db.models import Customer, PositionTemplate, Invoice, InvoicePosition, ExchangeRate


def _fmt(v):
    """Pretty-print helper for Decimal/None."""
    if v is None:
        return ""
    if isinstance(v, Decimal):
        # keep readable
        return f"{v:.4f}".rstrip("0").rstrip(".")
    return str(v)


def _print_table(title: str, headers: list[str], rows: Iterable[Iterable]):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    rows = [list(map(_fmt, r)) for r in rows]
    widths = [len(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(cell))

    def line(cells):
        return " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cells))

    print(line(headers))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(line(r))

    if not rows:
        print("(no rows)")


def main():
    with SessionLocal() as db:
        # Customers
        customers = db.query(Customer).order_by(Customer.id).all()
        _print_table(
            "CUSTOMERS",
            ["id", "name", "standard_currency", "vat_number", "company_number", "tax_number"],
            [
                (c.id, c.name, c.standard_currency, c.vat_number, c.company_number, c.tax_number)
                for c in customers
            ],
        )

        # Position Templates
        templates = db.query(PositionTemplate).order_by(PositionTemplate.id).all()
        _print_table(
            "POSITION_TEMPLATES",
            ["id", "name", "beschreibung", "standard_menge", "einzelpreis", "waehrung", "attachment_path"],
            [
                (t.id, t.name, t.beschreibung, t.standard_menge, t.einzelpreis, t.waehrung, t.attachment_path)
                for t in templates
            ],
        )

        # Invoices
        invoices = db.query(Invoice).order_by(Invoice.id).all()
        _print_table(
            "INVOICES",
            ["id", "nummer", "monat", "kunde_id", "zielwaehrung", "gesamtbetrag", "status"],
            [
                (inv.id, inv.nummer, inv.monat, inv.kunde_id, inv.zielwaehrung, inv.gesamtbetrag, inv.status)
                for inv in invoices
            ],
        )

        # Invoice Positions
        positions = db.query(InvoicePosition).order_by(InvoicePosition.id).all()
        _print_table(
            "INVOICE_POSITIONS",
            ["id", "invoice_id", "beschreibung", "menge", "einzelpreis", "waehrung", "attachment_path"],
            [
                (
                    p.id,
                    p.invoice_id,
                    p.beschreibung,
                    p.menge,
                    p.einzelpreis,
                    p.waehrung,
                    p.attachment_path,
                )
                for p in positions
            ],
        )

        # Exchange Rates
        rates = db.query(ExchangeRate).order_by(ExchangeRate.id).all()
        _print_table(
            "EXCHANGE_RATES",
            ["id", "datum", "von", "nach", "kurs"],
            [(r.id, r.datum, r.von, r.nach, r.kurs) for r in rates],
        )


if __name__ == "__main__":
    main()
