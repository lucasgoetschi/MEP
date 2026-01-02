# ------------------------------------------------------------
# statistics.py | Grundlegende Kennwerte aus Raum- und Lastdaten
# ------------------------------------------------------------
import pandas as pd

def compute_statistics(df: pd.DataFrame) -> dict:
    """
    Berechnet einfache Kennwerte aus der Raumlast-Tabelle.
    Rückgabe: Dictionary für Streamlit-Anzeige.
    """
    if df.empty:
        return {}

    try:
        stats = {
            "Anzahl Räume": len(df),
            "Gesamtfläche [m²]": round(df["Fläche [m²]"].sum(), 2),
            "Gesamtlast [kN]": round(df["Gesamtlast [kN]"].sum(), 2),
            "Durchschnittliche Nutzlast [kN/m²]": round(df["Nutzlast [kN/m²]"].mean(), 2),
            "Max. Einzelraumlast [kN]": round(df["Gesamtlast [kN]"].max(), 2)
        }
        return stats
    except Exception:
        return {}

def summarize_areas_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gibt eine tabellarische Übersicht aller Nutzflächen je Nutzungskategorie zurück.
    """
    if df.empty or "Nutzung" not in df.columns or "Fläche [m²]" not in df.columns:
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
    summary["Flächenanteil [%]"] = (summary["Fläche [m²]"] / summary["Fläche [m²]"].sum() * 100).round(1)

    return summary
