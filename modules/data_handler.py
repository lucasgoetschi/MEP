import pandas as pd
import os
from modules.auto_config_generator import classify_room_name

def calculate_loads(df, config):
    """Berechnet Lasten basierend auf der neuen heuristischen Klassifizierung."""
    categories = config["room_categories"]
    fallback_cat = config.get("fallback_category", "Allgemeine Flächen")
    fallback_qk = config.get("fallback_qk", 3.0)

    assigned_categories = []
    confidences = []

    # Jede Zeile mit der Heuristik-Funktion aus auto_config_generator verarbeiten
    for _, row in df.iterrows():
        cat, conf = classify_room_name(row["Raumname"], categories)
        
        if cat:
            assigned_categories.append(cat)
            confidences.append(conf)
        else:
            assigned_categories.append(fallback_cat)
            confidences.append(0.0)

    df["Nutzung"] = assigned_categories
    df["Confidence"] = confidences

    # Nutzlast qk zuweisen
    def get_qk(cat):
        return categories.get(cat, {}).get("qk", fallback_qk)

    df["Nutzlast [kN/m²]"] = df["Nutzung"].apply(get_qk)
    df["Gesamtlast [kN]"] = df["Fläche [m²]"] * df["Nutzlast [kN/m²]"]

    os.makedirs("results", exist_ok=True)
    df.to_csv("results/raumlasten.csv", index=False, encoding="utf-8-sig")
    
    return df