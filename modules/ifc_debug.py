# ifc_debug.py | IFC Property-Inspector

import ifcopenshell

def debug_ifc_properties(ifc_path="ARC_Modell_NEST_230328.ifc", limit=10):
    """Zeigt PropertySets und Properties der ersten Räume in einer IFC."""
    ifc = ifcopenshell.open(ifc_path)
    spaces = ifc.by_type("IfcSpace")
    print(f"Gefundene Räume: {len(spaces)}\n")

    for s in spaces[:limit]:
        print(f"🔹 Raum: {s.Name}")
        for rel in getattr(s, "IsDefinedBy", []):
            if rel.is_a("IfcRelDefinesByProperties"):
                pset = rel.RelatingPropertyDefinition
                print(f"  Pset: {pset.Name}")
                for p in getattr(pset, "HasProperties", []):
                    pname = p.Name
                    try:
                        val = p.NominalValue.wrappedValue
                    except Exception:
                        val = "-"
                    print(f"     - {pname}: {val}")
        print("----")

if __name__ == "__main__":
    debug_ifc_properties()
