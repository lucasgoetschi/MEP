import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Import deiner Module
from modules.config_loader import load_config_for_ifc
from modules.ifc_reader import read_ifc_spaces
from modules.data_handler import calculate_loads
from modules.statistics import compute_statistics
from modules.pdf_manager import create_pdf_report 
from modules.export_manager import plot_area_by_use, plot_loads_by_storey

# ------------------------------------------------------------
# 🎨 DESIGN & SCHRIFTGRÖSSE
# ------------------------------------------------------------
st.set_page_config(page_title="StructView | HSLU", layout="wide", page_icon="🏗️")

st.markdown("""
    <style>
        html, body, [class*="st-at"] { font-size: 1.05rem !important; }
        [data-testid="stMetricValue"] { font-size: 2.2rem !important; color: #1f77b4 !important; }
        button[data-baseweb="tab"] { font-size: 1.15rem !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

def load_results_csv(path):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

# ------------------------------------------------------------
# 📁 SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("# 🏗️ StructView")
    st.markdown("### HSLU Digital Construction")
    st.divider()
    uploaded_ifc = st.file_uploader("IFC Modell hochladen", type=["ifc"])
    
    if uploaded_ifc and st.button("🚀 Analyse starten", use_container_width=True):
        with st.spinner("Extrahiere BIM-Daten..."):
            temp_path = "temp.ifc"
            with open(temp_path, "wb") as f: 
                f.write(uploaded_ifc.getbuffer())
            config = load_config_for_ifc(temp_path)
            df_rooms = read_ifc_spaces(temp_path, config)
            calculate_loads(df_rooms, config)
            st.success("Analyse abgeschlossen!")
            st.rerun()

# ------------------------------------------------------------
# 🏛️ HEADER (Titel links, Logo rechts oben)
# ------------------------------------------------------------
df = load_results_csv("results/raumlasten.csv")

head_col1, head_col2 = st.columns([4, 2])
with head_col1:
    st.title("👷‍♂️ StructView")
with head_col2:
    if os.path.exists("hslu_logo.png"):
        st.image("hslu_logo.png", use_container_width=True)

tabs = st.tabs(["📊 Projekt-Übersicht", "📈 Dashboard", "📘 Methodik & Anleitung"])

# --- TAB 1: ÜBERSICHT ---
with tabs[0]:
    if not df.empty:
        stats = compute_statistics(df)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Gesamtlast", f"{stats.get('total_load_kn', 0):,.0f} kN")
        m2.metric("Gesamtfläche", f"{stats.get('total_area_m2', 0):,.1f} m²")
        m3.metric("Ø Nutzlast", f"{stats.get('avg_load_knm2', 0):,.2f} kN/m²")
        if "Confidence" in df.columns:
            m4.metric("Ø BIM-Sicherheit", f"{df['Confidence'].mean()*100:.1f} %")
        
        st.divider()
        c_a, c_b = st.columns(2)
        with c_a: 
            fig_area = plot_area_by_use(df)
            if fig_area: st.pyplot(fig_area)
        with c_b: 
            fig_storey = plot_loads_by_storey(df)
            if fig_storey: st.pyplot(fig_storey)
    else:
        st.info("Bitte IFC-Modell hochladen.")

# --- TAB 2: DASHBOARD ---
with tabs[1]:
    if not df.empty:
        st.subheader("Filter für Nutzungsvereinbarung")
        f1, f2, f3 = st.columns(3)
        s_geb = f1.selectbox("Gebäude", ["Alle"] + sorted(df["Gebäude"].dropna().unique().tolist()))
        s_nutz = f2.selectbox("Nutzung", ["Alle"] + sorted(df["Nutzung"].dropna().unique().tolist()))
        s_sto = f3.selectbox("Geschoss", ["Alle"] + sorted(df["Geschoss"].dropna().unique().tolist()))
        
        dff = df.copy()
        if s_geb != "Alle": dff = dff[dff["Gebäude"] == s_geb]
        if s_nutz != "Alle": dff = dff[dff["Nutzung"] == s_nutz]
        if s_sto != "Alle": dff = dff[dff["Geschoss"] == s_sto]

        e1, e2 = st.columns(2)
        with e1:
            csv_data = dff.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Gefilterte CSV laden", data=csv_data, file_name='Export_Filter.csv', use_container_width=True)
        with e2:
            f_stats = compute_statistics(dff)
            try:
                pdf_data = create_pdf_report(dff, f_stats)
                st.download_button("📄 Gefiltertes PDF laden", data=pdf_data, file_name='Bericht_Filter.pdf', use_container_width=True)
            except Exception as e:
                st.error(f"Fehler beim PDF-Export: {e}")

        st.divider()
        cols_nv = ["Raumnummer", "Raumname", "Geschoss", "Nutzung", "Fläche [m²]", "Nutzlast [kN/m²]"]
        st.dataframe(dff[[c for c in cols_nv if c in dff.columns]], use_container_width=True, height=350)
    else:
        st.info("Keine Daten vorhanden.")

# --- TAB 3: METHODIK & ANLEITUNG ---
with tabs[2]:
    st.header("Anleitung & Technische Dokumentation")
    
    st.subheader("Wichtige Hinweise zur Lastzusammenstellung")
    st.warning("""
        Die vorliegende Lastzusammenstellung wurde automatisiert auf Basis eines BIM-Modells erstellt. 
        Die Ergebnisse dienen ausschliesslich der Vorbemessung und entbinden den verantwortlichen Tragwerksplaner 
        nicht von der Pflicht zur manuellen Kontrolle gemäss SIA 261. Für aus der Nutzung dieser Daten entstehende 
        Schäden wird jede Haftung abgelehnt.
    """)

    st.subheader("Was macht dieses Skript?")
    st.markdown("""
    Dieses Tool wurde entwickelt, um den Prozess der statischen Vorbemessung zu digitalisieren:
    * **IFC-Datenextraktion:** Das Skript liest Raumobjekte (`IfcSpace`), Flächen und Metadaten direkt aus dem Architekturmodell aus.
    * **Heuristische Klassifizierung:** Da Raumbeschreibungen oft ungenau sind, nutzt das Skript ein Weighted-Keyword-Scoring, um Räume automatisch Nutzungskategorien nach SIA zuzuweisen.
    * **Lastzuweisung:** Basierend auf der identifizierten Nutzung werden die entsprechenden Nutzlasten $q_k$ gemäss SIA 261 zugewiesen und die Gesamteinwirkungen pro Raum berechnet.
    * **Validierung:** Ein Confidence-Score gibt an, wie sicher die automatische Zuweisung erfolgt ist, um kritische Stellen im Modell schnell zu identifizieren.
    """)
    
    if not df.empty:
        st.subheader("BIM-Daten Qualitätscheck")
        
        # Erstellen einer helleren Farbskala für die Tabelle (Rot zu Grün)
        cm = mcolors.LinearSegmentedColormap.from_list("custom_rdylgn", ["#ff9999", "#ffff99", "#99ff99"])
        
        st.dataframe(
            df[["Raumname", "Nutzung", "Confidence"]].style.background_gradient(
                subset=['Confidence'], 
                cmap=cm, 
                low=0, 
                high=1
            ).format({'Confidence': '{:.1%}'}), 
            use_container_width=True
        )
    
    st.divider()
    st.markdown(f"**Entwickler:** Lucas Goetschi | **Modul:** DT Programmieren | **HSLU**")