# ------------------------------------------------------------
# auto_config_generator.py AUTOMATISCHER CATEGORY-BUILDER
# ------------------------------------------------------------
import ifcopenshell
import yaml
import os
import re


def auto_generate_config(ifc_path):
    print(f"[CONFIG] Erstelle automatische Konfiguration für → {ifc_path}")

    model = ifcopenshell.open(ifc_path)
    spaces = model.by_type("IfcSpace")

    # Sammle Raumbezeichnungen
    room_names = []
    for s in spaces:
        name = str(s.Name or "").lower()
        room_names.append(name)

    # ------------------------------------------------------------
    # 1) Automatisch Kategorien aus Raumname ableiten
    # ------------------------------------------------------------

    auto_categories = {}

    def add_auto_category(title, keywords, qk):
        auto_categories[title] = {
            "keywords": keywords,
            "qk": qk
        }

    # Standardkategorien, die IMMER gelten (SIA-Logik)
    add_auto_category("Büroflächen", ["büro", "office"], 3.0)
    add_auto_category("Wohnräume", ["zimmer", "anteil", "wohnen", "bad", "wc"], 2.0)
    add_auto_category("Lagerräume", ["lager", "storage"], 5.0)
    add_auto_category("Verkaufsräume", ["verkauf", "shop"], 4.0)
    add_auto_category("Versammlungsräume", ["saal", "versamml"], 5.0)
    add_auto_category("Flure / Erschliessung", ["gang", "korr", "erschliess"], 2.0)

    # ------------------------------------------------------------
    # 2) Automatische Kategorien aus jedem Raumname erzeugen
    # ------------------------------------------------------------
    for rn in room_names:

        if not rn.strip():
            continue

        # Extrahiere mögliche Keywords
        words = re.split(r"[\s,_-]+", rn)

        for w in words:
            if len(w) < 3:
                continue

            # Technik? Küche? Reinigung? etc.
            if "techn" in w:
                add_auto_category("Technische Räume", ["techn", "server", "haustechnik"], 3.0)

            if "küch" in w or "cater" in w:
                add_auto_category("Küche / Catering", ["küch", "cater"], 4.0)

            if "reinig" in w:
                add_auto_category("Reinigung", ["reinig"], 2.0)

            if "lager" in w:
                add_auto_category("Lagerräume", ["lager"], 5.0)

            if "werk" in w:
                add_auto_category("Werkstatt", ["werk"], 5.0)

            if "technik" in w:
                add_auto_category("Technische Räume", ["technik"], 3.0)

            if "sanit" in w:
                add_auto_category("Sanitär", ["sanit"], 2.0)

            if "küche" in w:
                add_auto_category("Küche / Catering", ["küche"], 4.0)

    # ------------------------------------------------------------
    # 3) Fallback-Kategorie (wird garantiert nie genutzt außer absolut notwendig)
    # ------------------------------------------------------------
    fallback_category = "Sonstige Räume"
    fallback_qk = 3.0

    auto_categories[fallback_category] = {
        "keywords": [],
        "qk": fallback_qk
    }

    # ------------------------------------------------------------
    # 4) Schreib vollständige CONFIG
    # ------------------------------------------------------------
    
    config = {
        "ifc_file": os.path.basename(ifc_path),
        "output_folder": "results",

        "room_categories": auto_categories,
        "fallback_category": fallback_category,
        "fallback_qk": fallback_qk,

        "space_psets": {
            "allowed": [],
            "raumname": ["Name", "Raumname"],
            "raumnummer": ["Raumnummer", "Nummer"],
            "geschoss": ["Geschoss", "Storey", "Level"],
            "sia416": ["SIA 416", "Category"]
        },

        "quantities": {
            "flaeche": ["Area", "NetFloorArea", "GrossFloorArea"],
            "volumen": ["Volume", "NetVolume", "GrossVolume"]
        }
    }

    os.makedirs("config", exist_ok=True)
    cfg_path = f"config/{os.path.splitext(config['ifc_file'])[0]}.yaml"

    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    print(f"[CONFIG] Auto-Config gespeichert → {cfg_path}")
    return cfg_path
