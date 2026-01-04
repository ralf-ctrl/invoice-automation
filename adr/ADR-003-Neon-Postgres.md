# ADR-003 – Zentrale Datenbank (Neon PostgreSQL)

## Status
Accepted

## Kontext
Die App soll von mehreren Computern verwendet werden (z. B. von mir und meiner Frau), daher muss die Datenbank zentral erreichbar sein. Eine lokale SQLite-Datenbank reicht nicht aus; Synchronisation per Cloud-Share birgt Risiken.

## Entscheidung
Wir setzen eine verwaltete PostgreSQL-Instanz bei Neon als zentrale Datenbank ein. Die Datenbank wird via SSL im Internet erreichbar sein. Die Anwendung liest den DB-URL aus einer Umgebungsvariable und verwendet SQLAlchemy.

## Begründung
- Gleichzeitiger Zugriff von mehreren Geräten ohne Sperrprobleme
- Automatische Backups und hohe Verfügbarkeit
- Geringe laufende Kosten (Neon bietet einen kostenlosen Plan)
- Keine Notwendigkeit einer eigenen Serveradministration
- Später leicht skalierbar und zu alternativen Postgres-Anbietern migrierbar

## Konsequenzen
- Internetverbindung ist Voraussetzung für die Nutzung der Anwendung.
- DB-Zugangsdaten müssen sicher in einer `.env`-Datei verwaltet werden.
- Für die lokale Entwicklung wird weiterhin SQLite als Testdatenbank verwendet.
- Ein Migrationswerkzeug wie Alembic wird benötigt, um Schemaänderungen zu verwalten.
