# ADR-007 – PDF-Erzeugung über HTML-Template (Jinja2) und WeasyPrint

## Status
Accepted

## Kontext
Die App soll Rechnungen als PDF erzeugen. Layout und Inhalte müssen einfach anpassbar sein (Logo, Anschrift, Positionstabelle, Summen) und wiederholbar reproduzierbar generiert werden.

Zusätzlich sollen optional Positions-Anlagen (PDFs) aus iCloud referenziert werden (siehe ADR-004). Im MVP reicht es, Anlagen als Liste auszugeben und als separate Dateien neben der Rechnung zu verwalten.

## Entscheidung
Wir erzeugen PDFs in zwei Schritten:

1) **HTML-Rendern**: Ein Jinja2-Template (`app/templates/invoice_template.html`) wird mit Rechnungs- und Positionsdaten gerendert.
2) **PDF-Rendern**: Das gerenderte HTML wird mit **WeasyPrint** in ein PDF konvertiert.

### Ablage
- Templates: `app/templates/`
- Generierte PDFs: `invoices/<YYYY-MM>/<invoice_number>.pdf` (relativ zum Projektroot)
  - Beispiel: `invoices/2026-01/00001.pdf`

## Begründung
- HTML/CSS ist für Layout einfacher als Low-Level-PDF-Libraries (z. B. ReportLab).
- Jinja2 ermöglicht klare Trennung von Daten und Darstellung.
- WeasyPrint liefert ein „drucknahes“ Rendering und ist für Rechnungen ausreichend.

## Alternativen
- ReportLab (verworfen: Layout/Styling deutlich aufwändiger)
- DOCX-Templates + Konvertierung (verworfen: zusätzliche Toolchain, Konvertierung oft OS-abhängig)
- LaTeX (verworfen: höhere Einstiegshürde, schwerer zu pflegen)

## Konsequenzen
- WeasyPrint benötigt Systemabhängigkeiten (z. B. cairo/pango). Diese müssen auf Dev-Maschinen installiert werden.
- Template-Änderungen sind nicht „typgesichert“ – daher sollten Template-Änderungen manuell geprüft werden (Preview/Smoke-Test).
- Im MVP werden Anlagen nicht in das Haupt-PDF „eingebettet“; die App kann Anlagen später als separate Downloads anbieten oder optional zusammenführen.
