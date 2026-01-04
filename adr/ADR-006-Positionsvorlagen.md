# ADR-006 – Positionsvorlagen (wiederkehrende Rechnungspositionen)

## Status
Accepted

## Kontext
In der Rechnungsstellung gibt es wiederkehrende Positionen (z. B. „Beratung“, „Maintenance“, „Lizenzgebühr“), die monatlich/regelmäßig erneut verwendet werden. Das erneute manuelle Erfassen ist zeitaufwändig und fehleranfällig.

Die Streamlit-App soll diese Positionen zentral speichern, wiederverwenden und pflegen können. Dabei sollen die Vorlagen bei der Rechnungserstellung auswählbar sein und anschließend bei Bedarf pro Rechnung/Position angepasst werden können (Menge/Preis/Text/Währung).

## Entscheidung
Wir führen eine zusätzliche Tabelle **`position_template`** ein, die wiederverwendbare Positionsvorlagen speichert. Diese Vorlagen werden in der Streamlit-App über eine eigene Verwaltungsseite gepflegt (CRUD).

### Schema (MVP)
- `id` (PK, Integer)
- `uuid` (UUID, unique, not null)
- `created_at` (timestamp, not null)
- `updated_at` (timestamp, not null)
- `name` (String, not null) – Kurzname/Vorlagenname (z. B. „Beratung“)
- `beschreibung` (String, not null) – Default-Beschreibung
- `standard_menge` (Numeric, not null, default 1)
- `einzelpreis` (Numeric, not null)
- `waehrung` (String, not null, default „EUR“)
- optional: `attachment_path` (String, nullable) – Default-Anhang (iCloud relativer Pfad), falls sinnvoll

### Verwendung in der Rechnungserstellung (MVP)
- In der „Rechnung erstellen“-Maske kann pro Position optional eine Vorlage ausgewählt werden.
- Bei Auswahl werden die Felder (Beschreibung/Menge/Preis/Währung/Anhang) vorbefüllt.
- Änderungen in der Rechnung wirken **nicht** zurück auf die Vorlage (Vorlagen bleiben stabil).
- Positionen in Rechnungen bleiben weiterhin in `invoice_position` gespeichert (Vorlage ist nur ein „Starter“).

## Begründung
- Deutlich weniger manuelle Eingabe, konsistente Texte/Preise.
- Vorlagen sind unabhängig von einzelnen Rechnungen und können zentral gepflegt werden.
- Das Modell bleibt relational und ist gut migrierbar (Alembic).
- Passt zu Multi-Device-Setup: Vorlagen liegen zentral in Postgres (Neon).

## Alternativen
- Vorlagen in JSON-Datei im Dateisystem (verworfen: Synchronisations-/Konfliktrisiko, keine Mehrbenutzer-Sicherheit).
- Vorlagen pro Kunde (customer_id) als Pflichtfeld (verschoben: kann später ergänzt werden, wenn Bedarf).
- Hardcoded Vorlagen im Code (verworfen: nicht wartbar, nicht UI-pflegbar).

## Konsequenzen
- Neue Alembic-Migration (`Add position_template`) erforderlich.
- `app/db/models.py` wird um `PositionTemplate` erweitert.
- Streamlit erhält eine zusätzliche Seite „Positionen verwalten“.
- Optional: spätere Erweiterungen:
  - `customer_id` (nullable) für kundenbezogene Vorlagen
  - `is_active`, `sort_order`, `unit`, `tax_rate`
