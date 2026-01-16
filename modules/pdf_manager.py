# modules/pdf_manager.py
from fpdf import FPDF
import datetime
import os

class StructuralReport(FPDF):
    def header(self):
        # Logo oben rechts platzieren
        logo_path = "hslu_logo.png"
        if os.path.exists(logo_path):
            self.image(logo_path, x=150, y=10, w=45)
        
        # Titel
        self.set_text_color(31, 119, 180) # HSLU-Blau
        self.set_font('Arial', 'B', 22)
        self.set_y(15)
        self.cell(0, 10, ' STRUCTVIEW REPORT', 0, 1, 'L')
        
        # Professionalisierter Untertitel
        self.set_font('Arial', '', 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, ' Automatisierte Lastzusammenstellung aus BIM-Modell (IFC)', 0, 1, 'L')
        self.cell(0, 6, ' Regelwerk: SIA 261 - Einwirkungen auf Tragwerke', 0, 1, 'L')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Lucas Goetschi | HSLU | Seite {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 16) # Grosse Kapitelüberschrift
        self.set_text_color(31, 119, 180)
        self.cell(0, 10, label, 0, 1, 'L')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

def create_pdf_report(df, stats):
    pdf = StructuralReport()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # --- 1. WICHTIGE HINWEISE (Ehemals Disclaimer) ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 13) # Schriftgrösse erhöht
    pdf.cell(0, 10, 'Wichtige Hinweise zur Lastzusammenstellung', 0, 1, 'L')
    
    pdf.set_font('Arial', '', 12) # Schriftgrösse erhöht
    hinweise = (
        "Die vorliegende Lastzusammenstellung wurde automatisiert auf Basis eines BIM-Modells erstellt. "
        "Die Ergebnisse dienen ausschliesslich der Vorbemessung und entbinden den verantwortlichen Tragwerksplaner "
        "nicht von der Pflicht zur manuellen Kontrolle gemäss SIA 261. Für aus der Nutzung dieser Daten entstehende "
        "Schäden wird jede Haftung abgelehnt."
    )
    pdf.multi_cell(0, 7, hinweise)
    pdf.ln(10)

    # --- 2. ZUSAMMENFASSUNG NACH NUTZUNG ---
    pdf.chapter_title('1. Lastzusammenfassung nach Nutzungskategorie')
    pdf.set_font('Arial', 'B', 11)
    pdf.set_fill_color(240, 240, 240)
    
    # Tabellenkopf Zusammenfassung
    pdf.cell(70, 10, ' Nutzungskategorie', 1, 0, 'L', True)
    pdf.cell(40, 10, ' Flaeche [m2]', 1, 0, 'C', True)
    pdf.cell(40, 10, ' Last qk [kN/m2]', 1, 0, 'C', True)
    pdf.cell(40, 10, ' Summe [kN]', 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 11)
    summary = df.groupby('Nutzung').agg({
        'Fläche [m²]': 'sum',
        'Nutzlast [kN/m²]': 'first',
        'Gesamtlast [kN]': 'sum'
    }).reset_index()

    for _, row in summary.iterrows():
        pdf.cell(70, 9, f" {row['Nutzung']}", 1)
        pdf.cell(40, 9, f"{row['Fläche [m²]']:,.2f}", 1, 0, 'R')
        pdf.cell(40, 9, f"{row['Nutzlast [kN/m²]']:.2f}", 1, 0, 'R')
        pdf.cell(40, 9, f"{row['Gesamtlast [kN]']:,.1f}", 1, 1, 'R')
    pdf.ln(10)

    # --- 3. DETAILLISTE ---
    pdf.chapter_title('2. Detaillierte Raumliste')
    
    pdf.set_fill_color(31, 119, 180)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 10)
    
    w = [25, 75, 30, 30, 30]
    cols = ["Raum-Nr", "Raumbezeichnung", "Nutzung", "Flaeche", "Last [kN]"]
    
    for i, col in enumerate(cols):
        pdf.cell(w[i], 10, col, 1, 0, 'C', True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 9)
    
    fill = False
    for _, row in df.iterrows():
        if pdf.get_y() > 265:
            pdf.add_page()
            # Kopfzeile auf neuer Seite wiederholen
            pdf.set_fill_color(31, 119, 180)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Arial', 'B', 10)
            for i, col in enumerate(cols):
                pdf.cell(w[i], 10, col, 1, 0, 'C', True)
            pdf.ln()
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 9)
        
        pdf.set_fill_color(245, 248, 252)
        pdf.cell(w[0], 8, str(row.get('Raumnummer', '-'))[:12], 1, 0, 'C', fill)
        pdf.cell(w[1], 8, f" {str(row.get('Raumname', ''))[:40]}", 1, 0, 'L', fill)
        pdf.cell(w[2], 8, f" {str(row.get('Nutzung', ''))[:15]}", 1, 0, 'L', fill)
        pdf.cell(w[3], 8, f"{row.get('Fläche [m²]', 0):.2f}", 1, 0, 'R', fill)
        pdf.cell(w[4], 8, f"{row.get('Gesamtlast [kN]', 0):.1f}", 1, 1, 'R', fill)
        fill = not fill

    return pdf.output(dest='S').encode('latin-1')