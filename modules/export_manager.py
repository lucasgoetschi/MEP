
# export_manager.py 

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


#Excel-Export

def export_excel_and_plots(csv_path="results/raumlasten.csv"):
    """Exportiert Raumlastdaten als Excel-Datei."""
    if not os.path.exists(csv_path):
        print(f"Datei nicht gefunden: {csv_path}")
        return
    df = pd.read_csv(csv_path)

    excel_path = csv_path.replace(".csv", ".xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Excel-Datei erstellt: {excel_path}")



#Diagramm 1 – Kreisdiagramm mit smarten Labels

def plot_area_by_use(df):
    """Kreisdiagramm – Flächenverteilung nach Nutzung (mit Kollisionsvermeidung & Gruppierung)."""
    grouped = df.groupby("Nutzung")["Fläche [m²]"].sum().sort_values(ascending=False)
    total = grouped.sum()

    # Kleine Segmente (< 2 %) zusammenfassen
    small = grouped[grouped / total < 0.02]
    grouped = grouped[grouped / total >= 0.02]
    if not small.empty:
        grouped["Sonstige"] = small.sum()

    fig, ax = plt.subplots(figsize=(8, 7))
    colors = [
        "#6CCECB", "#F2D479", "#A0B9E6", "#E9967A", "#B0E57C",
        "#F7A072", "#C49BBB", "#A3D977", "#C6C6C6", "#9DC6D8"
    ][:len(grouped)]

    wedges, _ = ax.pie(
        grouped,
        startangle=90,
        colors=colors,
        wedgeprops=dict(width=0.6, edgecolor="white")
    )

    ax.set_title(
        "Verteilung der Nutzflächen nach Kategorie",
        pad=30,
        fontsize=14,
        fontweight="bold"
    )

    label_radius = 1.25
    connector_radius = 1.05
    label_positions = []

    for i, (p, label) in enumerate(zip(wedges, grouped.index)):
        ang = (p.theta2 + p.theta1) / 2
        x = np.cos(np.deg2rad(ang))
        y = np.sin(np.deg2rad(ang))

        percent = grouped.values[i] / total * 100
        label_text = f"{label}\n{percent:.1f}%"

        # Leichter Wechsel in der Vertikalposition (abwechselnd oben/unten)
        offset_y = (i % 2) * 0.1 * np.sign(y)

        # Kollisionsvermeidung – überprüfe vorherige Labels
        for lx, ly in label_positions:
            if abs(ly - (y + offset_y)) < 0.1 and np.sign(ly) == np.sign(y):
                offset_y += 0.15 * np.sign(y)
        label_positions.append((x, y + offset_y))

        # Text zeichnen
        ax.text(
            x * label_radius,
            (y + offset_y) * label_radius,
            label_text,
            ha="center",
            va="center",
            fontsize=10,
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", boxstyle="round,pad=0.3"),
        )

        # Verbindungslinie
        ax.plot(
            [x * connector_radius, x * label_radius * 0.9],
            [y * connector_radius, (y + offset_y) * label_radius * 0.9],
            color="gray",
            lw=0.8,
        )

    ax.axis("equal")
    fig.tight_layout()
    return fig



# Diagramm 2 – Gesamtlasten pro Nutzung

def plot_loads_by_use(df):
    """Balkendiagramm – Gesamtlasten pro Nutzung."""
    grouped = df.groupby("Nutzung")["Gesamtlast [kN]"].sum().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.barh(grouped.index, grouped.values, color="#5BA4CF", edgecolor="black", alpha=0.85)
    ax.bar_label(bars, fmt="%.0f", padding=4, fontsize=10)

    ax.set_title("Gesamtlasten pro Nutzung", fontsize=14, pad=20, fontweight="bold")
    ax.set_xlabel("Gesamtlast [kN]", fontsize=12)
    ax.set_ylabel("")
    ax.grid(True, linestyle="--", alpha=0.4, axis="x")

    fig.tight_layout()
    return fig



# Diagramm 3 – Gesamtlasten pro Geschoss

def plot_loads_by_storey(df):
    """Balkendiagramm – Gesamtlasten pro Geschoss."""
    grouped = df.groupby("Geschoss")["Gesamtlast [kN]"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(grouped.index, grouped.values, color="#84C28E", edgecolor="black", alpha=0.9)
    ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=10, rotation=0)

    ax.set_title("Gesamtlasten pro Geschoss", fontsize=14, pad=20, fontweight="bold")
    ax.set_xlabel("Geschoss", fontsize=12)
    ax.set_ylabel("Gesamtlast [kN]", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.4, axis="y")

    fig.tight_layout()
    return fig
