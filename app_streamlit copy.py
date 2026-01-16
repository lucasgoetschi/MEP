# ------------------------------------------------------------
# app_streamlit.py | HSLU DC HS25 | Lucas Goetschi
# StructView – Automatische IFC-Nutzlast- & Flächenanalyse
# ------------------------------------------------------------

import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Projektmodule
from modules.config_loader import load_config_for_ifc
from modules.ifc_reader import read_ifc_spaces
from modules.data_handler import calculate_loads
from modules.export_manager import (
    export_excel_and_plots,
    plot_area_by_use,
    plot_loads_by_use,
    plot_loads_by_storey,
)
from modules.statistics import compute_statistics, summarize_areas_by_category


# ------------------------------------------------------------
# Page Config & Styling
# ------------------------------------------------------------
st.set_page_config(
    page_title="StructView",
    layout="wide",
    page_icon="👷‍♂️",
)

st.markdown(
    """
    <style>
    html, body {
        font-size: 17px;
    }
    h1, h2, h3 {
        font-weight: 600;
    }
    .block-container {
        padding-top: 2rem;
    }
    .stMetricValue {
        font-size: 22px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("👷‍♂️ StructView")
st.caption(
    "Automatische Nutzlast- und Flächenanalyse aus IFC | "
    "HSLU Digital Construction | HS25 | Lucas Goetschi"
)

tabs = st.tabs(["🏠 Start", "📊 Ergebnisse & Diagramme", "📈 Dashboard"])


# ------------------------------------------------------------
# Helper
# ------------------------------------------------------------
def load_results_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df


# ------------------------------------------------------------
# 🏠 START
# ------------------------------------------------------------
with tabs[0]:
    st.subheader("Projektstart")

    with st.expander("📘 Anleitung & Hinweise", expanded=False):
        st.markdown("""
        **Zweck**  
        StructView dient zur **automatisierten Auswertung von Nutzflächen und Nutzlasten**
        aus IFC-Modellen gemäss **SIA 261**.

        Einsatz:
        - Vorstudien
        - Variantenvergleiche
        - Plausibilitätsprüfungen

        **Kein Ersatz für eine statische Bemessung.**

        **Ablauf**
        1. IFC-Datei hochladen  
        2. Analyse starten  
        3. IFC-Parsing → Nutzungserkennung → Nutzlastberechnung  
        4. Export von Tabellen und Diagrammen

        **Limitation**
        Ergebnisse sind normbasiert, vereinfacht und abhängig von der Modellqualität.
        """)

    st.divider()

    uploaded_ifc = st.file_uploader("IFC-Datei auswählen", type=["ifc"])

    if uploaded_ifc:
        with open("temp.ifc", "wb") as f:
            f.write(uploaded_ifc.getbuffer())

        st.success("IFC-Datei erfolgreich hochgeladen.")

        if st.button("▶ Analyse starten", use_container_width=True):
            with st.spinner("Analyse läuft …"):
                try:
                    CONFIG = load_config_for_ifc("temp.ifc")
                    st.session_state["config"] = CONFIG

                    df_rooms = read_ifc_spaces("temp.ifc", CONFIG)
                    if df_rooms.empty:
                        st.error("Keine Räume im IFC gefunden.")
                        st.stop()

                    os.makedirs("results", exist_ok=True)
                    df_rooms.to_csv("results/raumdaten.csv", index=False)

                    df_loads = calculate_loads(
                        raum_csv="results/raumdaten.csv",
                        sia_csv="data/sia261_nutzlasten.csv",
                        ifc_path="temp.ifc",
                        config=CONFIG,
                    )

                    if df_loads.empty:
                        st.error("Keine Nutzlasten berechnet.")
                        st.stop()

                    export_excel_and_plots("results/raumlasten.csv")

                    st.session_state["analyzed"] = True
                    st.success("Analyse abgeschlossen.")

                except Exception as e:
                    st.error(f"Fehler während der Analyse: {e}")

    else:
        st.info("Bitte IFC-Datei hochladen, um zu starten.")


# ------------------------------------------------------------
# 📊 ERGEBNISSE & DIAGRAMME
# ------------------------------------------------------------
with tabs[1]:
    st.subheader("Ergebnisse & Diagramme")

    if not st.session_state.get("analyzed"):
        st.info("Bitte zuerst im Start-Tab eine Analyse durchführen.")
        st.stop()

    df = load_results_csv("results/raumlasten.csv")
    if df.empty:
        st.warning("Keine Ergebnisse vorhanden.")
        st.stop()

    # Kennwerte
    stats = compute_statistics(df)
    if stats:
        c1, c2, c3 = st.columns(3)
        c1.metric("Gesamtfläche [m²]", f"{stats['Gesamtfläche [m²]']:,}")
        c2.metric("Gesamtlast [kN]", f"{stats['Gesamtlast [kN]']:,}")
        c3.metric("Ø Nutzlast [kN/m²]", f"{stats['Durchschnittliche Nutzlast [kN/m²]']}")

    st.divider()

    diagramm = st.radio(
        "Diagramm auswählen",
        [
            "Fläche nach Nutzung",
            "Gesamtlast nach Nutzung",
            "Gesamtlast nach Geschoss",
        ],
        horizontal=True,
    )

    st.divider()

    # ZENTRIERTES DIAGRAMM (links/rechts Leerraum)
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        if diagramm == "Fläche nach Nutzung":
            fig = plot_area_by_use(df)
            st.pyplot(fig)

        elif diagramm == "Gesamtlast nach Nutzung":
            fig = plot_loads_by_use(df)
            st.pyplot(fig)

        elif diagramm == "Gesamtlast nach Geschoss":
            fig = plot_loads_by_storey(df)
            st.pyplot(fig)


# ------------------------------------------------------------
# 📈 DASHBOARD
# ------------------------------------------------------------
with tabs[2]:
    st.subheader("Dashboard – Interaktive Auswertung")

    df = load_results_csv("results/raumlasten.csv")
    if df.empty:
        st.warning("Keine Daten verfügbar.")
        st.stop()

    c1, c2, c3 = st.columns(3)
    gebaeude = c1.selectbox("Gebäude", ["Alle"] + sorted(df["Gebäude"].dropna().unique()))
    nutzung = c2.selectbox("Nutzung", ["Alle"] + sorted(df["Nutzung"].dropna().unique()))
    sortierung = c3.selectbox(
        "Sortieren nach",
        ["Gesamtlast [kN]", "Fläche [m²]", "Nutzlast [kN/m²]"],
    )

    if gebaeude != "Alle":
        df = df[df["Gebäude"] == gebaeude]
    if nutzung != "Alle":
        df = df[df["Nutzung"] == nutzung]

    m1, m2, m3 = st.columns(3)
    m1.metric("Gesamtfläche [m²]", f"{df['Fläche [m²]'].sum():,.1f}")
    m2.metric("Gesamtlast [kN]", f"{df['Gesamtlast [kN]'].sum():,.1f}")
    m3.metric("Ø Nutzlast [kN/m²]", f"{df['Nutzlast [kN/m²]'].mean():,.2f}")

    st.divider()

    st.dataframe(
        df[
            ["Raumname", "Nutzung", "Geschoss",
             "Fläche [m²]", "Nutzlast [kN/m²]", "Gesamtlast [kN]"]
        ]
        .sort_values(sortierung, ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
    )

    # Top-10 Plot
    df_plot = df.sort_values(sortierung, ascending=False).head(10)
    if not df_plot.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.barh(df_plot["Raumname"], df_plot[sortierung])
        ax.bar_label(bars, fmt="%.1f")
        ax.set_xlabel(sortierung)
        ax.set_title(f"Top 10 Räume nach {sortierung}")
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)
