# ------------------------------------------------------------
# export_manager.py | HSLU DC HS25 | Lucas Goetschi
# ------------------------------------------------------------
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def export_excel_and_plots(csv_path="results/raumlasten.csv"):
    """Exportiert Raumlastdaten als Excel-Datei."""
    if not os.path.exists(csv_path):
        print(f"Datei nicht gefunden: {csv_path}")
        return
    df = pd.read_csv(csv_path)

    excel_path = csv_path.replace(".csv", ".xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Excel-Datei erstellt: {excel_path}")


def plot_area_by_use(df):
    """
    Donut-Diagramm: Flächenverteilung nach Nutzung.
    - Grosse Schrift für bessere Lesbarkeit.
    - Legende unten rechts zur Vermeidung von Textkollisionen.
    - Speichert Bild für PDF-Export.
    """
    if df.empty:
        return None

    grouped = df.groupby("Nutzung")["Fläche [m²]"].sum().sort_values(ascending=False)
    total = grouped.sum()

    # Kleine Segmente (< 1.5 %) zusammenfassen
    threshold = 0.015
    small = grouped[grouped / total < threshold]
    grouped = grouped[grouped / total >= threshold]
    if not small.empty:
        grouped["Sonstige"] = small.sum()

    # Layout: Platz für Legende rechts schaffen
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # HSLU-nahe Farbpalette
    colors = ["#6CCECB", "#F2D479", "#A0B9E6", "#E9967A", "#B0E57C", "#C6C6C6"]

    wedges, texts, autotexts = ax.pie(
        grouped,
        labels=None,             # Labels nur in der Legende
        autopct='%1.1f%%',       # Prozentanzeige im Kreis
        startangle=90,
        colors=colors,
        pctdistance=0.75,
        wedgeprops=dict(width=0.5, edgecolor="white") # Donut-Style
    )

    # Schriftgrösse Prozentzahlen
    plt.setp(autotexts, size=14, weight="bold", color="#333333")

    ax.set_title(
        "Verteilung der Nutzflächen nach Kategorie",
        pad=25,
        fontsize=20,
        fontweight="bold"
    )

    # Legende unten rechts
    ax.legend(
        wedges, 
        grouped.index,
        title="Nutzungskategorien",
        title_fontsize=15,
        loc="lower right",
        bbox_to_anchor=(1.25, 0), 
        fontsize=14,
        frameon=True
    )

    ax.axis("equal")
    plt.tight_layout()
    
    # Speichern für PDF
    os.makedirs("results", exist_ok=True)
    fig.savefig("results/plot_area.png", dpi=300, bbox_inches='tight')
    
    return fig


def plot_loads_by_use(df):
    """Balkendiagramm: Gesamtlasten pro Nutzung mit grosser Schrift."""
    if df.empty:
        return None
        
    grouped = df.groupby("Nutzung")["Gesamtlast [kN]"].sum().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10, 7))

    bars = ax.barh(grouped.index, grouped.values, color="#5BA4CF", edgecolor="black", alpha=0.85)
    
    # Datenlabels
    ax.bar_label(bars, fmt="%.0f", padding=6, fontsize=14, fontweight="bold")

    ax.set_title("Gesamtlasten pro Nutzung", fontsize=20, pad=25, fontweight="bold")
    ax.set_xlabel("Gesamtlast [kN]", fontsize=16)
    
    # Achsenbeschriftungen vergrössern
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.grid(True, linestyle="--", alpha=0.4, axis="x")

    fig.tight_layout()
    return fig


def plot_loads_by_storey(df):
    """
    Balkendiagramm: Gesamtlasten pro Geschoss.
    - Grosse Schrift.
    - Speichert Bild für PDF-Export.
    """
    if df.empty:
        return None

    grouped = df.groupby("Geschoss")["Gesamtlast [kN]"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 7))

    bars = ax.bar(grouped.index, grouped.values, color="#84C28E", edgecolor="black", alpha=0.9)
    
    # Datenlabels
    ax.bar_label(bars, fmt="%.0f", padding=5, fontsize=14, fontweight="bold")

    ax.set_title("Gesamtlasten pro Geschoss", fontsize=20, pad=25, fontweight="bold")
    ax.set_xlabel("Geschoss", fontsize=16)
    ax.set_ylabel("Gesamtlast [kN]", fontsize=16)
    
    # Achsenbeschriftungen
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.grid(True, linestyle="--", alpha=0.4, axis="y")

    fig.tight_layout()
    
    # Speichern für PDF
    os.makedirs("results", exist_ok=True)
    fig.savefig("results/plot_storey.png", dpi=300, bbox_inches='tight')
    
    return fig