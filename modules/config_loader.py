# ------------------------------------------------------------
# config_loader.py | MANAGEMENT DER KONFIGURATION
# ------------------------------------------------------------
import os
import yaml
# Hier importieren wir den Generator – das ist OK, solange der Generator NICHT zurück importiert.
from modules.auto_config_generator import auto_generate_config

def load_config_for_ifc(ifc_path):
    """Lädt bestehende Config oder triggert die automatische Erstellung."""
    ifc_name = os.path.basename(ifc_path)
    config_name = f"{os.path.splitext(ifc_name)[0]}.yaml"
    config_path = os.path.join("config", config_name)

    # Falls Config nicht existiert -> Neu generieren
    if not os.path.exists(config_path):
        print(f"[LOADER] Keine Config gefunden. Starte Generator...")
        config_path = auto_generate_config(ifc_path)

    # Config einlesen
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config