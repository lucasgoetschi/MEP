import ifcopenshell
import pandas as pd

def get_storey_from_element(space):
    """Ermittelt das Geschoss eines IfcSpace robust über IFC-Struktur."""

    # 1) Standard Revit/Archicad Methode
    try:
        for rel in space.ContainedInStructure:
            if rel.is_a("IfcRelContainedInSpatialStructure"):
                storey = rel.RelatingStructure
                if storey.is_a("IfcBuildingStorey"):
                    return storey.Name
    except:
        pass

    # 2) Alternative Methode über Decomposes
    try:
        for rel in space.Decomposes:
            parent = rel.RelatingObject
            if parent.is_a("IfcBuildingStorey"):
                return parent.Name
    except:
        pass

    # 3) Weitere verschachtelte Struktur (oft ArchiCAD)
    try:
        container = ifcopenshell.util.element.get_container(space)
        if container and container.is_a("IfcBuildingStorey"):
            return container.Name
    except:
        pass

    # 4) Fallback
    return "Unbekannt"

def read_ifc_spaces(ifc_path, config):

    model = ifcopenshell.open(ifc_path)
    spaces = model.by_type("IfcSpace")

    allowed_psets = config["space_psets"]["allowed"]
    name_keys = config["space_psets"]["raumname"]
    num_keys = config["space_psets"]["raumnummer"]
    lvl_keys = config["space_psets"]["geschoss"]
    sia_keys = config["space_psets"]["sia416"]

    area_keys = config["quantities"]["flaeche"]
    vol_keys = config["quantities"]["volumen"]

    results = []

    for s in spaces:
        info = {
            "Raum-ID": s.GlobalId,
            "Raumname": None,
            "Raumnummer": None,
            "Geschoss" : get_storey_from_element(s),
            "Gebäude": None,
            "Fläche [m²]": None,
            "Volumen [m³]": None,
            "SIA 416 Kategorie": None
        }

        for rel in getattr(s, "IsDefinedBy", []):
            if not rel.is_a("IfcRelDefinesByProperties"):
                continue

            pdef = rel.RelatingPropertyDefinition

            # PropertySets
            if pdef.is_a("IfcPropertySet") and pdef.Name in allowed_psets:
                for p in pdef.HasProperties:
                    pname = p.Name

                    if pname in name_keys:
                        info["Raumname"] = str(p.NominalValue.wrappedValue)
                    if pname in num_keys:
                        info["Raumnummer"] = str(p.NominalValue.wrappedValue)
                    if pname in lvl_keys:
                        info["Geschoss"] = str(p.NominalValue.wrappedValue)
                    if pname in sia_keys:
                        info["SIA 416 Kategorie"] = str(p.NominalValue.wrappedValue)

            # Quantities
            elif pdef.is_a("IfcElementQuantity"):
                for q in pdef.Quantities:
                    if q.Name in area_keys and info["Fläche [m²]"] is None:
                        info["Fläche [m²]"] = float(q.AreaValue)
                    if q.Name in vol_keys and info["Volumen [m³]"] is None:
                        info["Volumen [m³]"] = float(q.VolumeValue)

        results.append(info)

    return pd.DataFrame(results)
