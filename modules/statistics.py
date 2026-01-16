# ------------------------------------------------------------
# statistics.py | HSLU DC HS25 | Optimiert für Dashboard-Anzeige
# ------------------------------------------------------------
import pandas as pd

def compute_statistics(df: pd.DataFrame) -> dict:
    """
    Berechnet Kennwerte für die Streamlit-Metriken.
    Die Keys sind auf die app_streamlit.py abgestimmt (total_load_kn etc.).
    """
    if df.empty:
        return {
            "total_load_kn": 0,
            "total_area_m2": 0,
            "avg_load_knm2": 0,
            "Anzahl Räume": 0
        }

    try:
        # Sicherstellen, dass die benötigten Spalten existieren
        stats = {
            "total_load_kn": round(df["Gesamtlast [kN]"].sum(), 2),
            "total_area_m2": round(df["Fläche [m²]"].sum(), 2),
            "avg_load_knm2": round(df["Nutzlast [kN/m²]"].mean(), 2),
            "Anzahl Räume": len(df),
            "Max. Einzelraumlast [kN]": round(df["Gesamtlast [kN]"].max(), 2)
        }
        return stats
    except KeyError as e:
        print(f"[ERROR] Spalte fehlt in DataFrame: {e}")
        return {
            "total_load_kn": 0, 
            "total_area_m2": 0, 
            "avg_load_knm2": 0, 
            "Anzahl Räume": 0
        }

def summarize_areas_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gibt eine tabellarische Übersicht aller Nutzflächen je Nutzungskategorie zurück.
    Optimiert für interaktive Diagramme.
    """
    needed_cols = ["Nutzung", "Fläche [m²]", "Gesamtlast [kN]"]
    if df.empty or not all(col in df.columns for col in needed_cols):
        return pd.DataFrame()

    summary = (
        df.groupby("Nutzung", as_index=False)
        .agg({
            "Fläche [m²]": "sum",
            "Gesamtlast [kN]": "sum"
        })
        .sort_values("Fläche [m²]", ascending=False)
    )
    
    summary["Fläche [m²]"] = summary["Fläche [m²]"].round(2)
    summary["Gesamtlast [kN]"] = summary["Gesamtlast [kN]"].round(2)
    
    # Flächenanteil für die prozentuale Analyse
    total_area = summary["Fläche [m²]"].sum()
    summary["Flächenanteil [%]"] = (summary["Fläche [m²]"] / total_area * 100).round(1) if total_area > 0 else 0

    return summary