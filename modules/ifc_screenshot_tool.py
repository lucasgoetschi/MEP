
# ifc_screenshot_tool.py 
#sollte seperate Webseite öffnen und Pläne pro Geschoss generieren. Leider unstabil, deshalb nicht benutzt

import sys
import os
import base64
import tempfile
import webbrowser
import http.server
import socketserver
import threading

if len(sys.argv) < 2:
    print("Verwendung: python ifc_screenshot_tool.py <ifc_datei>")
    sys.exit(1)

ifc_path = sys.argv[1]
if not os.path.exists(ifc_path):
    print(f"IFC-Datei nicht gefunden: {ifc_path}")
    sys.exit(1)

print(f"Starte IFC.js Screenshot-Tool für: {ifc_path}")

# IFC als Base64
with open(ifc_path, "rb") as f:
    ifc_base64 = base64.b64encode(f.read()).decode("utf-8")

# Temporäres HTML erzeugen
html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>IFC Screenshot Tool</title>
  <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/web-ifc-three@0.0.43/IFCLoader.js"></script>
</head>
<body style="margin:0; overflow:hidden; background:#f2f2f2;">
  <div id="info" style="position:absolute; top:10px; left:10px; z-index:10;">
    <button id="shotBtn" style="padding:8px 18px; font-weight:600; background:#2E86C1; color:white; border:none; border-radius:6px;">
      Screenshot erstellen
    </button>
  </div>
  <script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({{antialias:true}});
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(5,10,5);
    scene.add(light);

    const ambient = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambient);

    // IFC laden aus Base64
    const ifcLoader = new IFCLoader();
    ifcLoader.ifcManager.setWasmPath("https://cdn.jsdelivr.net/npm/web-ifc@latest/");
    const base64 = "{ifc_base64}";
    const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0));
    const blob = new Blob([bytes], {{type: "application/octet-stream"}});
    const url = URL.createObjectURL(blob);

    ifcLoader.load(url, (ifcModel) => {{
        scene.add(ifcModel);
        const box = new THREE.Box3().setFromObject(ifcModel);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        camera.position.set(center.x, center.y + maxDim * 1.2, center.z + maxDim * 1.2);
        camera.lookAt(center);
        animate();
    }});

    window.addEventListener('resize', () => {{
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }});

    function animate() {{
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
    }}

    // Screenshot-Funktion
    document.getElementById("shotBtn").onclick = () => {{
        const imgData = renderer.domElement.toDataURL("image/png");
        const link = document.createElement("a");
        link.download = "ifc_screenshot.png";
        link.href = imgData;
        link.click();
    }};
  </script>
</body>
</html>"""

# Temporären Ordner & Server
temp_dir = tempfile.mkdtemp()
html_path = os.path.join(temp_dir, "viewer.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

PORT = 8123
os.chdir(temp_dir)

def start_server():
    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        print(f"Server läuft auf http://localhost:{PORT}/viewer.html")
        httpd.serve_forever()

thread = threading.Thread(target=start_server, daemon=True)
thread.start()

webbrowser.open(f"http://localhost:{PORT}/viewer.html")
print("Öffne Browser für Screenshot...")
input("Drücke [Enter], um den Server zu beenden.\n")
