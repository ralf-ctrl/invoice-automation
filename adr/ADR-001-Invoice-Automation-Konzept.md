# ADR-001 – Invoice Automation App

## Status
Accepted

## Kontext
Monatlich wiederkehrende Rechnungsprozesse verursachen manuellen Aufwand,
sind fehleranfällig und zeitintensiv.

## Entscheidung
Es wird eine Python-basierte Applikation zur Automatisierung der Rechnungsstellung entwickelt:
- Streamlit als Benutzeroberfläche
- zentrale PostgreSQL-Datenbank (Managed, Neon)
- PDF-Rechnungsausgabe
- ADR-getriebene Weiterentwicklung

## Begründung
- Reduktion manueller Tätigkeiten
- reproduzierbare Ergebnisse
- einfache Bedienbarkeit
- kostengünstiger Betrieb

## Konsequenzen
- MVP-first-Ansatz
- kein Ersatz für ein ERP-System
- Fokus auf interne Nutzung
