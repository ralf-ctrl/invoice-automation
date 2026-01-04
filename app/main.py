import streamlit as st
from datetime import date

from app.db.session import SessionLocal
from app.db.models import Customer, PositionTemplate
from app.services.invoice_service import create_invoice_with_positions
from app.services.pdf_service import generate_invoice_pdf


# ---------------------------------------------------
# Helper
# ---------------------------------------------------
def _fmt_customer(c: Customer) -> str:
    return f"{c.name} (ID {c.id})"


def _fmt_template(t: PositionTemplate) -> str:
    return f"{t.name} (ID {t.id})"


# ---------------------------------------------------
# Kunden verwalten (Create / Update / Delete)
# ---------------------------------------------------
def manage_customers():
    st.title("👥 Kunden verwalten")

    with SessionLocal() as db:
        customers = db.query(Customer).order_by(Customer.name).all()

    if customers:
        st.subheader("Vorhandene Kunden")
        for c in customers:
            st.write(f"**{c.name}** — {c.standard_currency} — ID {c.id}")
    else:
        st.info("Noch keine Kunden vorhanden.")

    st.divider()
    st.subheader("Neuen Kunden anlegen")

    with st.form("create_customer"):
        name = st.text_input("Name / Firma")
        adresse = st.text_area("Adresse (Straße, PLZ, Ort, Land)")
        standard_currency = st.text_input("Standardwährung", value="EUR")
        company_number = st.text_input("Handelsregister (optional)", value="")
        vat_number = st.text_input("USt-IdNr. (optional)", value="")
        tax_number = st.text_input("Steuernummer (optional)", value="")
        submitted = st.form_submit_button("Kunde speichern")

    if submitted:
        if not name.strip():
            st.error("Bitte Name / Firma angeben.")
            return
        if not adresse.strip():
            st.error("Bitte Adresse angeben.")
            return

        with SessionLocal() as db:
            c = Customer(
                name=name.strip(),
                adresse=adresse.strip(),
                standard_currency=(standard_currency.strip() or "EUR"),
                company_number=(company_number.strip() or None),
                vat_number=(vat_number.strip() or None),
                tax_number=(tax_number.strip() or None),
            )
            db.add(c)
            db.commit()

        st.success("Kunde wurde angelegt.")
        st.rerun()

    if not customers:
        return

    st.divider()
    st.subheader("Kunde bearbeiten / löschen")

    customer_map = {_fmt_customer(c): c.id for c in customers}
    selected_label = st.selectbox("Kunde auswählen", list(customer_map.keys()))
    selected_id = customer_map[selected_label]

    with SessionLocal() as db:
        c = db.get(Customer, selected_id)

        with st.form("edit_customer"):
            name = st.text_input("Name / Firma", value=c.name)
            adresse = st.text_area("Adresse", value=c.adresse)
            standard_currency = st.text_input("Standardwährung", value=c.standard_currency)
            company_number = st.text_input("Handelsregister (optional)", value=c.company_number or "")
            vat_number = st.text_input("USt-IdNr. (optional)", value=c.vat_number or "")
            tax_number = st.text_input("Steuernummer (optional)", value=c.tax_number or "")

            save = st.form_submit_button("Änderungen speichern")

        if save:
            if not name.strip():
                st.error("Name / Firma darf nicht leer sein.")
                return
            if not adresse.strip():
                st.error("Adresse darf nicht leer sein.")
                return

            c.name = name.strip()
            c.adresse = adresse.strip()
            c.standard_currency = (standard_currency.strip() or "EUR")
            c.company_number = (company_number.strip() or None)
            c.vat_number = (vat_number.strip() or None)
            c.tax_number = (tax_number.strip() or None)

            db.commit()
            st.success("Kunde aktualisiert.")
            st.rerun()

        st.warning("⚠️ Löschen ist endgültig. Falls bereits Rechnungen existieren, kann das durch FK-Constraints scheitern.")
        confirm = st.checkbox("Ich verstehe, dass Löschen endgültig ist.", key=f"confirm_delete_customer_{selected_id}")

        if st.button("Kunde löschen", disabled=not confirm, key=f"delete_customer_{selected_id}"):
            try:
                db.delete(c)
                db.commit()
                st.success("Kunde gelöscht.")
                st.rerun()
            except Exception as e:
                db.rollback()
                st.error(f"Kunde konnte nicht gelöscht werden (wahrscheinlich verknüpfte Rechnungen). Fehler: {e}")


# ---------------------------------------------------
# Positionsvorlagen verwalten (Create / Update / Delete)
# ---------------------------------------------------
def manage_position_templates():
    st.title("🧩 Positionsvorlagen verwalten")

    with SessionLocal() as db:
        templates = db.query(PositionTemplate).order_by(PositionTemplate.name).all()

    if templates:
        st.subheader("Vorhandene Vorlagen")
        for t in templates:
            st.write(f"**{t.name}** – {t.beschreibung}, {t.einzelpreis} {t.waehrung} — ID {t.id}")
    else:
        st.info("Es sind noch keine Positionsvorlagen angelegt.")

    st.divider()
    st.subheader("Neue Positionsvorlage")

    with st.form("create_position_template"):
        name = st.text_input("Name")
        beschreibung = st.text_input("Beschreibung")
        standard_menge = st.number_input("Standardmenge", min_value=0.0, value=1.0, step=0.5)
        einzelpreis = st.number_input("Einzelpreis", min_value=0.0, value=0.0, step=0.01)
        waehrung = st.text_input("Währung", value="EUR")
        attachment_path = st.text_input("Anhangspfad (optional)", value="")
        submitted = st.form_submit_button("Speichern")

    if submitted:
        if not name.strip() or not beschreibung.strip():
            st.error("Name und Beschreibung sind Pflichtfelder.")
            return

        with SessionLocal() as db:
            tmpl = PositionTemplate(
                name=name.strip(),
                beschreibung=beschreibung.strip(),
                standard_menge=standard_menge,
                einzelpreis=einzelpreis,
                waehrung=(waehrung.strip() or "EUR"),
                attachment_path=(attachment_path.strip() or None),
            )
            db.add(tmpl)
            db.commit()

        st.success("Positionsvorlage gespeichert.")
        st.rerun()

    if not templates:
        return

    st.divider()
    st.subheader("Vorlage bearbeiten / löschen")

    tmpl_map = {_fmt_template(t): t.id for t in templates}
    selected_label = st.selectbox("Vorlage auswählen", list(tmpl_map.keys()))
    selected_id = tmpl_map[selected_label]

    with SessionLocal() as db:
        t = db.get(PositionTemplate, selected_id)

        with st.form("edit_template"):
            name = st.text_input("Name", value=t.name)
            beschreibung = st.text_input("Beschreibung", value=t.beschreibung)
            standard_menge = st.number_input("Standardmenge", min_value=0.0, value=float(t.standard_menge), step=0.5)
            einzelpreis = st.number_input("Einzelpreis", min_value=0.0, value=float(t.einzelpreis), step=0.01)
            waehrung = st.text_input("Währung", value=t.waehrung)
            attachment_path = st.text_input("Anhangspfad (optional)", value=t.attachment_path or "")

            save = st.form_submit_button("Änderungen speichern")

        if save:
            if not name.strip() or not beschreibung.strip():
                st.error("Name und Beschreibung sind Pflichtfelder.")
                return

            t.name = name.strip()
            t.beschreibung = beschreibung.strip()
            t.standard_menge = standard_menge
            t.einzelpreis = einzelpreis
            t.waehrung = (waehrung.strip() or "EUR")
            t.attachment_path = (attachment_path.strip() or None)
            db.commit()
            st.success("Vorlage aktualisiert.")
            st.rerun()

        st.warning("⚠️ Löschen ist endgültig.")
        confirm = st.checkbox("Ich verstehe, dass Löschen endgültig ist.", key=f"confirm_delete_template_{selected_id}")

        if st.button("Vorlage löschen", disabled=not confirm, key=f"delete_template_{selected_id}"):
            db.delete(t)
            db.commit()
            st.success("Vorlage gelöscht.")
            st.rerun()


# ---------------------------------------------------
# Rechnung erstellen
# ---------------------------------------------------
def create_invoice_page():
    st.title("🧾 Rechnung erstellen")

    with SessionLocal() as db:
        kunden = db.query(Customer).order_by(Customer.name).all()
        templates = db.query(PositionTemplate).order_by(PositionTemplate.name).all()

    if not kunden:
        st.warning("Es sind noch keine Kunden in der Datenbank angelegt.")
        st.info("Bitte zuerst unter „Kunden verwalten“ einen Kunden anlegen.")
        return

    kunden_map = {f"{k.name} (ID {k.id})": k for k in kunden}
    kunde_label = st.selectbox("Kunde auswählen", list(kunden_map.keys()))
    customer = kunden_map[kunde_label]

    col1, col2 = st.columns(2)
    with col1:
        jahr = st.number_input("Jahr", value=date.today().year, step=1)
    with col2:
        monat = st.number_input("Monat", min_value=1, max_value=12, value=date.today().month)

    st.markdown("### Rechnungspositionen")
    count = st.number_input("Anzahl Positionen", min_value=1, max_value=20, value=1)

    template_labels = ["(frei)"] + [f"{t.id}: {t.name}" for t in templates]
    template_map = {t.id: t for t in templates}

    positionen = []
    for i in range(int(count)):
        st.subheader(f"Position {i + 1}")

        sel = st.selectbox("Vorlage", template_labels, key=f"tmpl_{i}")
        if sel != "(frei)":
            if st.button("Vorlage übernehmen", key=f"use_{i}"):
                tid = int(sel.split(":")[0])
                t = template_map[tid]
                st.session_state[f"desc_{i}"] = t.beschreibung
                st.session_state[f"qty_{i}"] = float(t.standard_menge)
                st.session_state[f"price_{i}"] = float(t.einzelpreis)
                st.session_state[f"cur_{i}"] = t.waehrung
                st.session_state[f"att_{i}"] = t.attachment_path or ""
                st.rerun()

        beschreibung = st.text_input("Beschreibung", value=st.session_state.get(f"desc_{i}", ""), key=f"desc_{i}")
        menge = st.number_input("Menge", value=float(st.session_state.get(f"qty_{i}", 1.0)), key=f"qty_{i}")
        einzelpreis = st.number_input("Einzelpreis", value=float(st.session_state.get(f"price_{i}", 0.0)), key=f"price_{i}")
        waehrung = st.text_input("Währung", value=st.session_state.get(f"cur_{i}", "EUR"), key=f"cur_{i}")
        anhang = st.text_input("Anhang", value=st.session_state.get(f"att_{i}", ""), key=f"att_{i}")

        positionen.append({
            "beschreibung": beschreibung,
            "menge": menge,
            "einzelpreis": einzelpreis,
            "waehrung": waehrung,
            "attachment_path": anhang or None,
        })

        st.divider()

    if st.button("Rechnung generieren"):
        for p in positionen:
            if not (p["beschreibung"] or "").strip():
                st.error("Bitte alle Beschreibungen ausfüllen (keine leeren Positionen).")
                return

        with SessionLocal() as db:
            invoice = create_invoice_with_positions(
                db_session=db,
                customer=customer,
                year=int(jahr),
                month=int(monat),
                positions=positionen,
            )
            pdf_path = generate_invoice_pdf(invoice)

        st.success(f"Rechnung {invoice.nummer} erstellt.")
        with open(pdf_path, "rb") as f:
            st.download_button(
                "PDF herunterladen",
                f.read(),
                file_name=f"Rechnung_{invoice.nummer}.pdf",
                mime="application/pdf",
            )


# ---------------------------------------------------
# App Shell
# ---------------------------------------------------
st.set_page_config(page_title="Invoice Automation", page_icon="🧾")

menu = st.sidebar.selectbox(
    "Menü",
    ["Rechnung erstellen", "Kunden verwalten", "Positionen verwalten"],
)

if menu == "Kunden verwalten":
    manage_customers()
elif menu == "Positionen verwalten":
    manage_position_templates()
else:
    create_invoice_page()
