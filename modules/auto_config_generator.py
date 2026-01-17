import yaml
import os

def auto_generate_config(ifc_path):
    """
    Erstellt eine optimierte Konfigurationsdatei mit erweiterten Keywords 
    für eine maximale Trefferrate bei NEST, EFH und Schulungsprojekten.
    """
    print(f"[PROCESS] Generiere High-Performance Config für: {os.path.basename(ifc_path)}")
    
    # Massive Keyword-Datenbank für Schweizer Standardprojekte (SIA 261)
    kb = {
        "Büroflächen": {
            "keywords": ["büro", "office", "work", "arbeiten", "atelier", "sitzung", "besprechung", 
                         "meeting", "telefon", "kopierer", "print", "empfang", "rezeption"], 
            "qk": 3.0, "weight": 1.2
        },
        "Wohnräume": {
            "keywords": ["zimmer", "wohnen", "schlafen", "bad", "wc", "küche", "dusche", "entree", 
                         "flur", "korridor", "ankleide", "esszimmer", "wohnzimmer", "kind", "gast", 
                         "essen", "kochen", "loggia", "balkon"], 
            "qk": 2.0, "weight": 1.0
        },
        "Lagerräume": {
            "keywords": ["lager", "archiv", "storage", "depot", "abstell", "keller", "reduit", 
                         "vorrat", "magazin", "material", "entsorgung", "container", "entsorgung"], 
            "qk": 5.0, "weight": 1.1
        },
        "Verkaufsräume": {
            "keywords": ["verkauf", "laden", "shop", "retail", "ausstellung", "markt", "kasse", "showroom"], 
            "qk": 4.0, "weight": 1.3
        },
        "Erschliessung / Treppen": {
            "keywords": ["treppe", "lift", "aufzug", "podest", "rampe", "treppenhaus", "th", "gang", 
                         "galerie", "lobby", "vorplatz", "korridor", "durchgang"], 
            "qk": 3.0, "weight": 1.4
        },
        "Technische Räume": {
            "keywords": ["technik", "elektro", "heizung", "server", "hls", "lüftung", "zentrale", 
                         "kälte", "warmwasser", "maschinen", "trafo", "sprinkler", "it", "elektra"], 
            "qk": 3.0, "weight": 1.2
        },
        "Parkflächen": {
            "keywords": ["parken", "garage", "tiefgarage", "pw", "abstellplatz", "einstellhalle", 
                         "carport", "parkplatz", "einstellplatz"], 
            "qk": 2.5, "weight": 1.5
        },
        "Schulung / Unterricht": {
            "keywords": ["schule", "unterricht", "klasse", "zimmer", "aula", "labor", "seminar", "kurs"],
            "qk": 3.0, "weight": 1.1
        }
    }

    # Definition der Pset-Strukturen (optimiert für ArchiCAD/Revit Exports)
    config = {
        "ifc_file": os.path.basename(ifc_path),
        "room_categories": kb,
        "fallback_category": "Allgemeine Nutzfläche",
        "fallback_qk": 3.0,
        "space_psets": {
            "raumname": ["Name", "Raumname", "LongName", "Label", "Raumbezeichnung"],
            "raumnummer": ["Raumnummer", "Nummer", "Number", "Tag"],
            "geschoss": ["Geschoss", "Storey", "Level", "Reference"],
            "sia416": ["SIA 416", "Category", "Nutzungsart"]
        },
        "quantities": {
            "flaeche": ["Area", "NetFloorArea", "Nettofläche", "NetArea", "Fläche"],
            "volumen": ["Volume", "NetVolume", "Bruttovolumen"]
        }
    }

    # Pfad-Handling
    os.makedirs("config", exist_ok=True)
    file_id = os.path.splitext(os.path.basename(ifc_path))[0]
    cfg_path = f"config/{file_id}.yaml"
    
    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    return cfg_path