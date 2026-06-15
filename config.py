import os
import unicodedata
from dotenv import load_dotenv

load_dotenv()

CLICKUP_TOKEN = os.getenv("CLICKUP_TOKEN")
CLICKUP_FOLDER_ID = os.getenv("CLICKUP_FOLDER_ID")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

APROBADO_STATUSES = ["aprobado", "approved"]


def _normalize(text):
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFD", text)
    no_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    return no_accents.strip().lower()


def is_aprobado(status_name):
    return _normalize(status_name) in APROBADO_STATUSES


def validate_config():
    missing = []
    if not CLICKUP_TOKEN:
        missing.append("CLICKUP_TOKEN")
    if not CLICKUP_FOLDER_ID:
        missing.append("CLICKUP_FOLDER_ID")
    if not SLACK_WEBHOOK_URL:
        missing.append("SLACK_WEBHOOK_URL")

    if missing:
        raise EnvironmentError(
            f"Faltan variables de entorno: {', '.join(missing)}"
        )

    print(f"Config OK - Folder ID: {CLICKUP_FOLDER_ID}")
