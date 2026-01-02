# ------------------------------------------------------------
# app_streamlit.py | HSLU DC HS25 | Lucas Goetschi
# Automatische IFC-Auswertung mit integriertem Export-Manager
# ------------------------------------------------------------
import streamlit as st
import pandas as pd
import os

# Module aus dem Projekt
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
# Streamlit Design
# ------------------------------------------------------------
st.set_page_config(page_title="StructView", layout="wide", page_icon="👷‍♂️")


st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    .stMetricLabel {font-size: 16px !important;}
    .stMetricValue {font-size: 22px !important;}
    h1, h2, h3 {font-weight: 600 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("👷‍♂️ StructView – Automatische Nutzlast- und Flächenanalyse")
st.caption("HSLU | Digital Construction | HS25 | Lucas Goetschi")

# Tabs
tabs = st.tabs([
    "🏠 Start",
    "📊 Ergebnisse & Diagramme",
    "📈 Dashboard"
])


# ------------------------------------------------------------
# Hilfsfunktion: CSV robust laden
# ------------------------------------------------------------
def load_results_csv(path: str):
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df


# ------------------------------------------------------------
# 🏠 STARTTAB
# ------------------------------------------------------------
with tabs[0]:
    st.subheader("🏠 Projektstart – IFC-Datei hochladen und starten")
    st.write("Lade deine IFC-Datei hoch. Danach wird automatisch eine passende Konfiguration erstellt und ausgewertet.")

    uploaded_ifc = st.file_uploader("IFC-Datei auswählen", type=["ifc"])

    if uploaded_ifc:
        # IFC lokal speichern
        with open("temp.ifc", "wb") as f:
            f.write(uploaded_ifc.getbuffer())
        st.success("IFC-Datei erfolgreich hochgeladen.")

        if st.button("Analyse starten"):
            with st.spinner("Analysiere IFC-Datei, generiere CONFIG, berechne Nutzlasten..."):
                try:
                    # CONFIG laden oder automatisch generieren
                    CONFIG = load_config_for_ifc("temp.ifc")
                    st.success("Konfiguration geladen / erstellt.")
                    st.session_state["config"] = CONFIG

                    # IFC auslesen KONFIG-BASIERT
                    df_rooms = read_ifc_spaces("temp.ifc", CONFIG)
                    if df_rooms.empty:
                        st.error("Keine Räume im IFC gefunden.")
                        st.stop()

                    os.makedirs("results", exist_ok=True)
                    df_rooms.to_csv("results/raumdaten.csv", index=False)

                    # Nutzlastberechnung KONFIG-BASIERT
                    df_loads = calculate_loads(
                        raum_csv="results/raumdaten.csv",
                        sia_csv="data/sia261_nutzlasten.csv",
                        ifc_path="temp.ifc",
                        config=CONFIG
                    )

                    if df_loads.empty:
                        st.error("Keine Nutzlasten berechnet.")
                        st.stop()

                    # Excel & Diagramme exportieren
                    export_excel_and_plots("results/raumlasten.csv")

                    st.session_state["analyzed"] = True
                    st.success("Analyse abgeschlossen!")

                except Exception as e:
                    st.error(f"Fehler während der Analyse: {e}")

    else:
        st.info("Bitte IFC-Datei hochladen, um zu starten.")


# ------------------------------------------------------------
# 📊 ERGEBNISSE & DIAGRAMME
# ------------------------------------------------------------
with tabs[1]:
    st.subheader("📊 Ergebnisse & Diagramme")

    if not st.session_state.get("analyzed"):
        st.info("Bitte zuerst auf der Startseite die IFC-Datei analysieren.")
    else:
        df = load_results_csv("results/raumlasten.csv")

        if df.empty:
            st.warning("Keine Daten gefunden. Bitte Analyse erneut starten.")
        else:
            # Kennwerte
            st.markdown("### Kennwerte")
            stats = compute_statistics(df)
            if stats:
                col1, col2, col3 = st.columns(3)
                col1.metric("Gesamtfläche [m²]", f"{stats['Gesamtfläche [m²]']:,}")
                col2.metric("Gesamtlast [kN]", f"{stats['Gesamtlast [kN]']:,}")
                col3.metric("Ø Nutzlast [kN/m²]", f"{stats['Durchschnittliche Nutzlast [kN/m²]']}")

            # Flächenübersicht
            st.divider()
            st.markdown("### Flächenübersicht nach Nutzungskategorie")
            summary = summarize_areas_by_category(df)
            if not summary.empty:
                st.dataframe(summary, use_container_width=True)

            # Diagramme
            st.divider()
            st.markdown("### Diagramme")
            figs = [
                plot_area_by_use(df),
                plot_loads_by_use(df),
                plot_loads_by_storey(df)
            ]
            for fig in figs:
                if fig:
                    st.pyplot(fig)


# ------------------------------------------------------------
# 📈 DASHBOARD
# ------------------------------------------------------------
with tabs[2]:
    st.header("📈 Dashboard – Gefilterte Auswertung")

    df = load_results_csv("results/raumlasten.csv")
    if df.empty:
        st.warning("Keine Daten verfügbar. Bitte zuerst die IFC-Datei analysieren.")
    else:
        col1, col2, col3 = st.columns(3)
        gebaeude = st.selectbox("Gebäude:", ["Alle"] + sorted(df["Gebäude"].dropna().unique().tolist()))
        nutzung = st.selectbox("Nutzung:", ["Alle"] + sorted(df["Nutzung"].dropna().unique().tolist()))
        sortierung = st.selectbox("Sortieren nach:", ["Gesamtlast [kN]", "Fläche [m²]", "Nutzlast [kN/m²]"])

        if gebaeude != "Alle":
            df = df[df["Gebäude"] == gebaeude]
        if nutzung != "Alle":
            df = df[df["Nutzung"] == nutzung]

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Gesamtfläche [m²]", f"{df['Fläche [m²]'].sum():,.2f}")
        col_b.metric("Gesamtlast [kN]", f"{df['Gesamtlast [kN]'].sum():,.2f}")
        col_c.metric("Ø Nutzlast [kN/m²]", f"{df['Nutzlast [kN/m²]'].mean():,.2f}")

        st.divider()
        st.dataframe(
            df[["Raumname", "Nutzung", "Geschoss", "Fläche [m²]", "Nutzlast [kN/m²]", "Gesamtlast [kN]"]]
            .sort_values(sortierung, ascending=False)
            .reset_index(drop=True),
            use_container_width=True,
        )

        # Diagramm (Top 10)
        import matplotlib.pyplot as plt
        df_plot = df.sort_values(sortierung, ascending=False).head(10)
        if not df_plot.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.barh(df_plot["Raumname"], df_plot[sortierung], color="#2E86C1")
            ax.bar_label(bars, fmt="%.1f", label_type="edge", fontsize=9)
            ax.set_xlabel(sortierung)
            ax.set_ylabel("Raumname")
            ax.set_title(f"Top 10 Räume nach {sortierung}", fontsize=14, pad=10, weight="bold")
            ax.invert_yaxis()
            plt.tight_layout()
            st.pyplot(fig)
