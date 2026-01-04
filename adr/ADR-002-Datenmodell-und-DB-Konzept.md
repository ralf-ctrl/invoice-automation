# ADR-002 – Datenmodell und Datenbank-Konzept

## Status
Accepted

## Kontext
Für die Rechnungsautomations-App müssen Rechnungen, Positionen, Kunden und Wechselkurse dauerhaft gespeichert und von mehreren Endgeräten aus abrufbar sein. Die bisherige Entscheidung (ADR‑011) favorisiert eine zentral gehostete PostgreSQL‑Datenbank (Neon).

## Entscheidung
Wir verwenden ein relationales Datenmodell mit folgenden Tabellen:

- **customer**: id (PK), name, adresse, standard_währung
- **invoice**: id (PK), nummer, monat, kunde_id (FK -> customer.id), gesamtbetrag, zielwährung, status, created_at
- **invoice_position**: id (PK), invoice_id (FK -> invoice.id), beschreibung, menge, einzelpreis, währung
- **exchange_rate**: id (PK), datum, von, nach, kurs

Als Datenbank-Backend wird eine **verwaltete PostgreSQL-Instanz (Neon)** eingesetzt. Für die lokale Entwicklung und Tests kann weiterhin SQLite verwendet werden.

## Begründung
- Relationale Struktur passt gut zu Rechnungs- und Positionsdaten.
- PostgreSQL bietet Transaktionen, ACID‑Eigenschaften und wird von Neon gemanagt.
- Die Trennung der Entitäten ermöglicht einfache Erweiterungen (z. B. weitere Positionstypen oder Kundeninformationen).
- Wechselkurse werden historisch gespeichert, um nachvollziehbare Umrechnungen zu gewährleisten.

## Konsequenzen
- Die Applikation benötigt Netzwerkzugriff auf die Neon‑Instanz.
- SQL‑Alchemy wird als ORM eingesetzt; Migrationen werden mit Alembic verwaltet.
- SQLite bleibt für Tests und lokale Experimente bestehen, ist aber nicht für den Mehrbenutzerbetrieb geeignet.
- Änderungen am Datenmodell müssen über ADRs dokumentiert und via Migration eingespielt werden.
