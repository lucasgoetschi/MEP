# ------------------------------------------------------------
# config_loader.py | MANAGEMENT DER KONFIGURATION
# ------------------------------------------------------------

import os
import yaml
from modules.auto_config_generator import auto_generate_config

def load_config_for_ifc(ifc_path):
    file_id = os.path.splitext(os.path.basename(ifc_path))[0]
    cfg_path = f"config/{file_id}.yaml"

    if not os.path.exists(cfg_path):
        # Ruft die korrekte Funktion auf
        cfg_path = auto_generate_config(ifc_path)

    with open(cfg_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config