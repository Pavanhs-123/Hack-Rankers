from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"

for folder in [INPUT_DIR, PROCESSED_DIR, OUTPUT_DIR, LOG_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

MAX_IMAGES = 40
MAX_SIZE = 1280
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
