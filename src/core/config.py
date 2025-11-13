import pathlib
import yaml
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    root = pathlib.Path(__file__).parent.parent.parent
    conf_path = root / "config.yaml"
    if not conf_path.exists():
        return {}
    with conf_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
