"""
Carga backend/.env antes de importar la app para que DATABASE_URL esté disponible.
Ejecutar desde la carpeta backend:  python -m pytest tests -v
"""

from pathlib import Path

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND_ROOT / ".env", encoding="utf-8")
