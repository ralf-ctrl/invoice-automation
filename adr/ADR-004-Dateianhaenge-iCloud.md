# ADR-004 – Anhangsspeicherung mit iCloud

## Status
Accepted

## Kontext
Für Rechnungspositionen sollen optional Belege (z. B. PDF‑Anhänge) hinterlegt werden, die zusammen mit der Rechnung ausgegeben werden können. Diese Belege können groß sein und sollten nicht direkt in der Datenbank gespeichert werden.

## Entscheidung
Alle Anhänge werden in einem gemeinsamen iCloud‑Drive Ordner `InvoiceAttachments` gespeichert. In der Tabelle `invoice_position` wird eine neue Spalte `attachment_path` (VARCHAR) eingeführt, die den relativen Pfad zum Anhang (z. B. `2026/02/invoice_012-pos1.pdf`) enthält. Die Applikation prüft beim Erstellen einer Rechnung, ob der angegebene Anhang existiert und bindet ihn als Anlage ein oder legt ihn als separate Datei ab.

## Begründung
- iCloud‑Drive ist kostengünstig, integriert sich nahtlos in macOS und unterstützt die gemeinsame Nutzung eines Ordners zwischen den Rechnern.
- Die Datenbank bleibt schlank und Backups bleiben effizient, weil keine großen Binärdateien gespeichert werden.
- Die Ablage über ein Jahr‑/Monat‑Verzeichnis und ein konventionelles Dateinamensschema (z. B. `invoice_<Rechnungsnummer>-pos<Positionsnummer>.pdf`) erleichtert das Auffinden der Anhänge.

## Konsequenzen
- Es wird ein gemeinsamer iCloud‑Ordner eingerichtet und mit beiden Macs synchronisiert.
- Die Applikation benötigt Zugriff auf das Dateisystem, um Anhänge zu verifizieren und einzubinden.
- Beim Wechsel auf einen anderen Cloud‑Speicher muss lediglich der Basisordner angepasst werden.
