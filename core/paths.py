# core/paths.py
from pathlib import Path

# core/paths.py -> core -> 项目根
PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENV_FILE = PROJECT_ROOT / ".env"
CONFIG_YAML = PROJECT_ROOT / "config.yaml"