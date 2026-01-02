import yaml
import os
from .auto_config_generator import auto_generate_config

def load_config_for_ifc(ifc_path):
    name = os.path.splitext(os.path.basename(ifc_path))[0]
    cfg_path = f"config/{name}.yaml"

    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # Falls nicht vorhanden → automatisch erzeugen
    new_cfg = auto_generate_config(ifc_path)
    with open(new_cfg, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
