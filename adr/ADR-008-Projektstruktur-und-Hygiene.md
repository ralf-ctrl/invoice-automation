# ADR-008 – Projektstruktur, Startmechanik und Repository-Hygiene

## Status
Proposed

## Kontext
Die Streamlit-App wird als Skript `app/main.py` gestartet. Streamlit setzt den Importpfad so, dass die Script-Directory (`app/`) im Vordergrund steht. Dadurch kann `import app...` je nach Startkommando fehlschlagen.

Zusätzlich entstehen lokal Entwicklungsartefakte wie `.venv/`, `.idea/`, `__pycache__/` sowie generierte PDFs (`invoices/`). Diese dürfen nicht ins Git-Repository gelangen.

## Entscheidung
1) **Python-Paketstruktur**: `app/` wird als Package geführt (mit `__init__.py` in `app/`, `app/db/`, `app/services/`).
2) **Startmechanik (MVP)**: Wir starten Streamlit aus dem Projektroot mit gesetztem `PYTHONPATH`:
   - `export PYTHONPATH=$(pwd)`
   - `streamlit run app/main.py`
   Optional kann später ein Root-Entrypoint (`run.py`) ergänzt werden.
3) **Repo-Hygiene**: Wir erweitern `.gitignore` mindestens um:
   - `.venv/`
   - `.idea/`
   - `invoices/`
   - `*.pdf`
   - `.streamlit/` (falls Konfiguration genutzt wird)

## Begründung
- Minimiert Import-Probleme ohne sofortiges Packaging/Poetry.
- Verhindert große/unnötige Commits (venv/IDE/Outputs).
- Erleichtert Zusammenarbeit über GitHub.

## Konsequenzen
- In README muss ein klarer Start-Befehl dokumentiert werden.
- Für produktives Deployment (später) kann ein Container oder ein installierbares Paket sinnvoll werden.
