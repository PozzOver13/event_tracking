from pathlib import Path

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]

PATH_TOKEN = PROJ_ROOT / "token.json"
PATH_CREDENTIALS = PROJ_ROOT / "credentials.json"

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"