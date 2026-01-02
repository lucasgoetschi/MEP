# ------------------------------------------------------------
# test_pipeline.py | HSLU DC HS25 | Lucas Goetschi
# End-to-End Test der gesamten IFC-Auswertungs-Pipeline
# ------------------------------------------------------------

import os
import traceback

from modules.config_loader import load_config_for_ifc
from modules.ifc_reader import read_ifc_spaces
from modules.data_handler import calculate_loads
from modules.export_manager import export_excel_and_plots
from modules.statistics import compute_statistics


IFC_PATH = "temp.ifc"
ROOM_CSV = "results/raumdaten.csv"
LOAD_CSV = "results/raumlasten.csv"


# ------------------------------------------------------------
# Hilfsfunktion: Testreport Ausgabe
# ------------------------------------------------------------
def test_status(name, success, error_msg=None):
    print(f"\n--- Test: {name} ---")
    if success:
        print("STATUS: OK ✅")
    else:
        print("STATUS: FEHLER ❌")
        if error_msg:
            print("DETAIL:", error_msg)


# ------------------------------------------------------------
# 1) IFC Datei prüfen
# ------------------------------------------------------------
def test_ifc_exists():
    if not os.path.exists(IFC_PATH):
        return False, "IFC-Datei temp.ifc nicht gefunden."
    return True, None


# ------------------------------------------------------------
# 2) CONFIG Laden / Generieren
# ------------------------------------------------------------
def test_config():
    try:
        config = load_config_for_ifc(IFC_PATH)
        if not isinstance(config, dict):
            return False, "Config konnte nicht geladen werden."
        return True, None
    except Exception as e:
        return False, str(e)


# ------------------------------------------------------------
# 3) Räume auslesen
# ------------------------------------------------------------
def test_ifc_reader(config):
    try:
        df = read_ifc_spaces(IFC_PATH, config)
        if df.empty or len(df) == 0:
            return False, "Keine Räume aus IFC ausgelesen."
        if "Fläche [m²]" not in df.columns:
            return False, "Spalte 'Fläche [m²]' fehlt."
        return True, None
    except Exception as e:
        return False, str(e)


# ------------------------------------------------------------
# 4) Nutzlastberechnung
# ------------------------------------------------------------
def test_load_calc(config):
    try:
        # Sicherstellen, dass Basisdaten existieren
        if not os.path.exists(ROOM_CSV):
            return False, "raumdaten.csv fehlt. Vorher ifc_reader testen."

        df = calculate_loads(
            raum_csv=ROOM_CSV,
            sia_csv="data/sia261_nutzlasten.csv",
            ifc_path=IFC_PATH,
            config=config
        )

        if df.empty:
            return False, "Keine Lasten berechnet."
        if "Gesamtlast [kN]" not in df.columns:
            return False, "Spalte 'Gesamtlast [kN]' fehlt."
        return True, None

    except Exception as e:
        return False, str(e)


# ------------------------------------------------------------
# 5) Export & Diagramme
# ------------------------------------------------------------
def test_export():
    try:
        export_excel_and_plots(LOAD_CSV)
        if not os.path.exists("results/raumlasten.xlsx"):
            return False, "Excel wurde nicht erstellt."
        if not os.path.exists("results/raumlasten_plot.png"):
            return False, "Diagramm wurde nicht erstellt."
        return True, None
    except Exception as e:
        return False, str(e)


# ------------------------------------------------------------
# 6) Statistiken prüfen
# ------------------------------------------------------------
def test_statistics():
    try:
        if not os.path.exists(LOAD_CSV):
            return False, "raumlasten.csv fehlt."

        import pandas as pd
        df = pd.read_csv(LOAD_CSV)
        stats = compute_statistics(df)

        if "Gesamtfläche [m²]" not in stats:
            return False, "Statistik Schlüssel fehlen."
        return True, None
    except Exception as e:
        return False, str(e)


# ------------------------------------------------------------
# MAIN TEST-LAUF
# ------------------------------------------------------------
if __name__ == "__main__":
    print("\n======================================")
    print("🔍 PIPELINE-TEST: IFC → Config → Räume → Lasten → Export")
    print("======================================\n")

    # 1 IFC prüfen
    ok, err = test_ifc_exists()
    test_status("IFC Datei vorhanden", ok, err)
    if not ok:
        exit()

    # 2 CONFIG
    ok, err = test_config()
    test_status("CONFIG laden/generieren", ok, err)
    if not ok:
        exit()

    from modules.config_loader import load_config_for_ifc
    CONFIG = load_config_for_ifc(IFC_PATH)

    # 3 IFC Reader
    ok, err = test_ifc_reader(CONFIG)
    test_status("Räume auslesen (ifc_reader)", ok, err)

    # 4 Nutzlasten berechnen
    ok, err = test_load_calc(CONFIG)
    test_status("Nutzlastberechnung (data_handler)", ok, err)

    # 5 Exporte
    ok, err = test_export()
    test_status("Excel & Diagramme exportieren", ok, err)

    # 6 Statistik
    ok, err = test_statistics()
    test_status("Statistische Auswertung", ok, err)

    print("\n======================================")
    print("🏁 TESTLAUF ABGESCHLOSSEN")
    print("======================================\n")
