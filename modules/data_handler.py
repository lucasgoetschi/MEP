import pandas as pd
import os

def calculate_loads(raum_csv, sia_csv, ifc_path, config):

    df = pd.read_csv(raum_csv)

    categories = config["room_categories"]
    default_qk = config.get("default_qk", 2.0)
    fallback_cat = config.get("fallback_category", "Sonstige Räume")
    fallback_qk = config.get("fallback_qk", default_qk)

    def assign_category(name):
        lower = str(name).lower()
        for cat, data in categories.items():
            if any(k in lower for k in data["keywords"]):
                return cat
        return fallback_cat   # ← niemals "Unbekannt"

    def assign_qk(cat):
        if cat in categories:
            return categories[cat]["qk"]
        return fallback_qk  # ← definierter Sicherheitswert

    df["Nutzung"] = df["Raumname"].apply(assign_category)
    df["Nutzlast [kN/m²]"] = df["Nutzung"].apply(assign_qk)
    df["Gesamtlast [kN]"] = df["Fläche [m²]"] * df["Nutzlast [kN/m²]"]

    df.to_csv("results/raumlasten.csv", index=False, encoding="utf-8-sig")
    return df
