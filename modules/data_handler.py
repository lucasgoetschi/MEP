import os
import pandas as pd

def calculate_loads(df, config):
    """
    Berechnet die Lasten basierend auf der Config. 
    Die Zuordnungslogik ist hier integriert, um Import-Fehler zu vermeiden.
    """
    categories = config.get("room_categories", {})
    fallback_qk = config.get("fallback_qk", 3.0)
    fallback_cat = config.get("fallback_category", "Allgemeine Nutzfläche")
    
    results_nutzung = []
    results_qk = []
    results_confidence = []

    for idx, row in df.iterrows():
        # Raumname säubern für besseres Matching
        raumname = str(row.get("Raumname", "")).lower().strip()
        found_cat = None
        max_score = 0

        # Weighted Keyword Matching Logik
        for cat_name, data in categories.items():
            keywords = data.get("keywords", [])
            # Zähle Treffer pro Kategorie
            score = sum(1 for kw in keywords if kw.lower() in raumname)
            
            if score > max_score:
                max_score = score
                found_cat = cat_name

        # Zuweisung basierend auf dem besten Treffer
        if found_cat and max_score > 0:
            cat_data = categories.get(found_cat, {})
            qk = cat_data.get("qk", fallback_qk)
            weight = cat_data.get("weight", 1.0)
            
            results_nutzung.append(found_cat)
            results_qk.append(qk)
            # Confidence Score: Kombination aus Trefferanzahl und Kategorie-Gewichtung
            conf = min(1.0, (max_score * weight) / 2.0)
            results_confidence.append(conf)
        else:
            # Fallback falls gar nichts passt
            results_nutzung.append(fallback_cat)
            results_qk.append(fallback_qk)
            results_confidence.append(0.1)

    # DataFrame aktualisieren
    df["Nutzung"] = results_nutzung
    df["Nutzlast [kN/m²]"] = results_qk
    df["Confidence"] = results_confidence
    df["Gesamtlast [kN]"] = df["Fläche [m²]"] * df["Nutzlast [kN/m²]"]
    
    # Ergebnisse speichern für Streamlit
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/raumlasten.csv", index=False)
    
    return df