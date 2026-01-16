# ------------------------------------------------------------
# ifc_reader.py | HSLU DC HS25 | StructView
# Extraktion von Raumdaten aus IFC-Modellen
# ------------------------------------------------------------
import ifcopenshell
import ifcopenshell.util.element
import pandas as pd
import os

def get_storey_from_element(space):
    """Ermittelt das Geschoss eines IfcSpace robust über verschiedene IFC-Strukturen."""
    # 1) Standard Methode (ContainedInStructure)
    try:
        for rel in space.ContainedInStructure:
            if rel.is_a("IfcRelContainedInSpatialStructure"):
                storey = rel.RelatingStructure
                if storey.is_a("IfcBuildingStorey"):
                    return storey.Name
    except:
        pass

    # 2) Alternative Methode über Decomposes (Aggregationsstruktur)
    try:
        for rel in space.Decomposes:
            parent = rel.RelatingObject
            if parent.is_a("IfcBuildingStorey"):
                return parent.Name
    except:
        pass

    # 3) Fallback über Utility-Funktion
    try:
        container = ifcopenshell.util.element.get_container(space)
        if container and container.is_a("IfcBuildingStorey"):
            return container.Name
    except:
        pass

    return "Unbekannt"

def read_ifc_spaces(ifc_path, config):
    """Liest Räume und deren Eigenschaften basierend auf der Konfiguration ein."""
    print(f"[READER] Lese Modell: {os.path.basename(ifc_path)}")
    
    model = ifcopenshell.open(ifc_path)
    spaces = model.by_type("IfcSpace")

    # Keys aus der Config laden (mit Fallbacks falls Config-Felder fehlen)
    psets_cfg = config.get("space_psets", {})
    allowed_psets = psets_cfg.get("allowed", [])
    
    name_keys = psets_cfg.get("raumname", ["Name", "Raumname"])
    num_keys = psets_cfg.get("raumnummer", ["Number", "Nummer"])
    sia_keys = psets_cfg.get("sia416", ["SIA 416", "Category"])
    
    q_cfg = config.get("quantities", {})
    area_keys = q_cfg.get("flaeche", ["Area", "NetFloorArea"])
    vol_keys = q_cfg.get("volumen", ["Volume", "NetVolume"])

    results = []

    for s in spaces:
        # Standard-Informationen direkt vom Objekt
        info = {
            "Raumname": str(s.Name) if s.Name else "Unbekannter Raum",
            "Raumnummer": str(s.LongName) if s.LongName else "-",
            "Geschoss": get_storey_from_element(s),
            "Gebäude": "Hauptgebäude", # Optional erweiterbar
            "Fläche [m²]": 0.0,
            "Volumen [m³]": 0.0,
            "SIA 416 Kategorie": "Nutzfläche"
        }

        # Eigenschaften (PropertySets) durchsuchen
        for rel in getattr(s, "IsDefinedBy", []):
            if not rel.is_a("IfcRelDefinesByProperties"):
                continue

            pdef = rel.RelatingPropertyDefinition

            # Nur definierte PropertySets prüfen
            if pdef.is_a("IfcPropertySet"):
                # Falls allowed_psets leer ist, prüfen wir alle Psets (flexibler für Heuristik)
                if not allowed_psets or pdef.Name in allowed_psets:
                    for p in getattr(pdef, "HasProperties", []):
                        if not hasattr(p, "NominalValue") or p.NominalValue is None:
                            continue
                        
                        pname = p.Name
                        val = p.NominalValue.wrappedValue

                        if pname in name_keys: info["Raumname"] = str(val)
                        if pname in num_keys: info["Raumnummer"] = str(val)
                        if pname in sia_keys: info["SIA 416 Kategorie"] = str(val)

            # Mengen (Quantities) wie Fläche/Volumen prüfen
            elif pdef.is_a("IfcElementQuantity"):
                for q in getattr(pdef, "Quantities", []):
                    if q.is_a("IfcQuantityArea") and q.Name in area_keys:
                        info["Fläche [m²]"] = float(q.AreaValue)
                    if q.is_a("IfcQuantityVolume") and q.Name in vol_keys:
                        info["Volumen [m³]"] = float(q.VolumeValue)

        results.append(info)

    df = pd.DataFrame(results)
    
    # Letzte Bereinigung: Falls Fläche 0 ist, Raum ignorieren oder warnen
    df = df[df["Fläche [m²]"] > 0].copy()
    
    # Speichern der Rohdaten
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/raumdaten.csv", index=False, encoding="utf-8-sig")
    
    print(f"[READER] {len(df)} Räume erfolgreich eingelesen.")
    return df