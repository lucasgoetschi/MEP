# ------------------------------------------------------------
# auto_config_generator.py | HEURISTISCHER CATEGORY-BUILDER
# ------------------------------------------------------------
import ifcopenshell
import yaml
import os
import re

def classify_room_name(name, categories, min_score=0.8):
    """Heuristische Klassifizierung basierend auf Scoring."""
    if not name:
        return None, 0.0

    name_lower = str(name).lower()
    scores = {}

    for cat_name, data in categories.items():
        score = 0.0
        for kw in data["keywords"]:
            if kw in name_lower:
                # Bonus für exakte Treffer
                score += (data["weight"] * 1.5) if kw == name_lower else data["weight"]
        scores[cat_name] = score

    best_cat = max(scores, key=scores.get)
    best_score = scores[best_cat]

    if best_score < min_score:
        return None, 0.0

    total_score = sum(scores.values())
    confidence = (best_score / total_score) if total_score > 0 else 0
    return best_cat, round(confidence, 2)

def auto_generate_config(ifc_path):
    """Erstellt eine neue Konfigurationsdatei basierend auf Modell-Analyse."""
    print(f"[CONFIG] Generiere Heuristik für → {ifc_path}")
    
    try:
        model = ifcopenshell.open(ifc_path)
    except Exception as e:
        print(f"Fehler beim Öffnen der IFC: {e}")
        return None

    # Wissensbasis (Knowledge Base)
    kb = {
        "Büroflächen": {"keywords": ["büro", "office", "work"], "qk": 3.0, "weight": 1.2},
        "Wohnräume": {"keywords": ["zimmer", "wohnen", "schlafen", "bad", "wc", "küche"], "qk": 2.0, "weight": 1.0},
        "Lagerräume": {"keywords": ["lager", "archiv", "storage", "depot"], "qk": 5.0, "weight": 1.1},
        "Verkaufsräume": {"keywords": ["verkauf", "laden", "shop", "retail"], "qk": 4.0, "weight": 1.3},
        "Flure / Erschliessung": {"keywords": ["gang", "korr", "treppe", "lift", "entree"], "qk": 2.0, "weight": 0.9},
        "Technische Räume": {"keywords": ["technik", "elektro", "heizung", "server", "hls"], "qk": 3.0, "weight": 1.2}
    }

    config = {
        "ifc_file": os.path.basename(ifc_path),
        "room_categories": kb,
        "fallback_category": "Allgemeine Flächen",
        "fallback_qk": 3.0,
        "space_psets": {
            "raumname": ["Name", "Raumname", "LongName"],
            "raumnummer": ["Raumnummer", "Nummer"],
            "geschoss": ["Geschoss", "Storey", "Level"]
        },
        "quantities": {
            "flaeche": ["Area", "NetFloorArea", "Nettofläche"],
            "volumen": ["Volume", "NetVolume"]
        }
    }

    os.makedirs("config", exist_ok=True)
    cfg_path = f"config/{os.path.splitext(config['ifc_file'])[0]}.yaml"

    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    return cfg_path