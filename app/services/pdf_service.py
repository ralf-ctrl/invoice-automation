import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Ordner, in dem deine Templates liegen
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

def generate_invoice_pdf(invoice) -> str:
    """Erzeugt ein PDF für die gegebene Rechnung und gibt den Dateipfad zurück."""
    # Lade HTML-Template
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("invoice_template.html")

    # Daten für das Template vorbereiten
    html_content = template.render(invoice=invoice, positions=invoice.positions)

    # Zielordner nach Jahr/Monat
    output_dir = os.path.join("invoices", invoice.monat)
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{invoice.nummer}.pdf")

    # HTML → PDF rendern
    HTML(string=html_content).write_pdf(file_path)
    return file_path
