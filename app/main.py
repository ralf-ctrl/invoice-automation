import streamlit as st
from datetime import date
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import Customer, PositionTemplate  # PositionTemplate muss im Modell definiert sein
from app.services.invoice_service import create_invoice_with_positions
from app.services.pdf_service import generate_invoice_pdf  # passe ggf. den Import an

# ---------------------------------------------------
# Hilfsfunktion für DB-Sessions
# ---------------------------------------------------
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------
# Positionsvorlagen verwalten
# ---------------------------------------------------
def manage_position_templates():
    st.header("Positionen verwalten")
    # Liste vorhandener Vorlagen anzeigen
    with SessionLocal() as db:
        templates = db.query(PositionTemplate).order_by(PositionTemplate.name).all()
        if templates:
            for tmpl in templates:
                st.write(f"**{tmpl.name}** – {tmpl.beschreibung}, {tmpl.einzelpreis} {tmpl.waehrung}")
        else:
            st.info("Es sind noch keine Positionsvorlagen angelegt.")

    st.divider()
    st.subheader("Neue Position anlegen")
    with SessionLocal() as db:
        name = st.text_input("Name")
        beschreibung = st.text_input("Beschreibung")
        menge = st.number_input("Standardmenge", min_value=0.0, value=1.0, step=0.5)
        einzelpreis = st.number_input("Einzelpreis", min_value=0.0, value=0.0, step=0.01)
        waehrung = st.text_input("Währung", value="EUR")
        if st.button("Position speichern"):
            tmpl = PositionTemplate(
                name=name,
                beschreibung=beschreibung,
                standard_menge=menge,
                einzelpreis=einzelpreis,
                waehrung=waehrung
            )
            db.add(tmpl)
            db.commit()
            st.success("Position gespeichert!")
            st.experimental_rerun()  # aktualisiert die Liste sofort

# ---------------------------------------------------
# Streamlit-Setup und Menü
# ---------------------------------------------------
st.set_page_config(page_title="Rechnungs-Tool", page_icon="🧾")

menu = st.sidebar.selectbox(
    "Menü",
    options=["Rechnung erstellen", "Positionen verwalten"],
)

# Wenn Positionen verwalten gewählt wurde, entsprechende Seite anzeigen
if menu == "Positionen verwalten":
    manage_position_templates()
    st.stop()

# ---------------------------------------------------
# Rechnung erstellen (Standardansicht)
# ---------------------------------------------------
st.title("🧾 Rechnung erstellen")

# Kunden laden
with next(get_db()) as db:
    kunden = db.query(Customer).order_by(Customer.name).all()

if not kunden:
    st.warning("Es sind noch keine Kunden in der Datenbank angelegt.")
    st.stop()

kunden_dict = {f"{k.name} (ID {k.id})": k for k in kunden}
kunde_label = st.selectbox("Kunde auswählen", options=list(kunden_dict.keys()))
selected_customer = kunden_dict[kunde_label]

# Monat und Jahr wählen
col1, col2 = st.columns(2)
with col1:
    jahr = st.number_input("Jahr", min_value=2000, max_value=2100, value=date.today().year, step=1)
with col2:
    monat = st.number_input("Monat", min_value=1, max_value=12, value=date.today().month, step=1)

st.markdown("### Rechnungspositionen")

# Anzahl Positionen definieren
anzahl_positionen = st.number_input("Anzahl Positionen", min_value=1, max_value=20, value=1, step=1)

# Dynamische Eingabefelder für Positionen
positionen = []
for idx in range(int(anzahl_positionen)):
    st.subheader(f"Position {idx + 1}")
    beschreibung = st.text_input("Beschreibung", key=f"desc_{idx}")
    menge = st.number_input("Menge", min_value=0.0, value=1.0, step=0.5, key=f"qty_{idx}")
    einzelpreis = st.number_input("Einzelpreis", min_value=0.0, value=0.0, step=0.01, key=f"price_{idx}")
    waehrung = st.text_input("Währung (z. B. EUR)", value="EUR", key=f"cur_{idx}")
    anhang = st.text_input("Pfad zum Anhang (optional)", key=f"attach_{idx}")
    positionen.append({
        "beschreibung": beschreibung,
        "menge": menge,
        "einzelpreis": einzelpreis,
        "waehrung": waehrung,
        "attachment_path": anhang or None,
    })
    st.divider()

# Button zum Erstellen der Rechnung
if st.button("Rechnung generieren"):
    with next(get_db()) as db:
        invoice = create_invoice_with_positions(
            db_session=db,
            customer=selected_customer,
            year=int(jahr),
            month=int(monat),
            positions=positionen
        )
        # PDF erzeugen
        pdf_path = generate_invoice_pdf(invoice)
    st.success(f"Rechnung {invoice.nummer} wurde erstellt.")
    # Download-Button anzeigen
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="PDF herunterladen",
            data=f.read(),
            file_name=f"Rechnung_{invoice.nummer}.pdf",
            mime="application/pdf",
        )

import uuid
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.models import Base  # falls Base hier nicht im Scope ist, entsprechend importieren

class PositionTemplate(Base):
    __tablename__ = "position_template"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    name = Column(String, nullable=False)
    beschreibung = Column(String, nullable=False)
    standard_menge = Column(Numeric, nullable=False, default=1)
    einzelpreis = Column(Numeric, nullable=False)
    waehrung = Column(String, nullable=False, default="EUR")

