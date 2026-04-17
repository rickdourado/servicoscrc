import os
from fpdf import FPDF
from pathlib import Path
import re

class ReportPDF(FPDF):
    def header(self):
        # Logo placeholder (Blue rectangle)
        self.set_fill_color(30, 58, 138) # Navy Blue
        self.rect(0, 0, 210, 30, 'F')
        
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'SmartContract Auditor - Relatório de Solução', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()} | CRC - Coordenadoria de Relacionamento com o Cidadão', 0, 0, 'C')

def clean_text(text):
    # Remove emojis and special unicode characters that break standard PDF fonts
    return text.encode('ascii', 'ignore').decode('ascii')

def generate_pdf(md_path, output_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Process content
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue
            
        # Clean line for FPDF
        display_line = clean_text(line)
        if not display_line and line: # If cleaning removed everything but there was content
             continue

        # Headers
        if line.startswith('# '):
            pdf.set_font('helvetica', 'B', 22)
            pdf.set_text_color(30, 58, 138)
            pdf.cell(0, 15, clean_text(line[2:]), new_x="LMARGIN", new_y="NEXT", align='L')
            pdf.set_draw_color(0, 209, 178) # Teal
            pdf.set_line_width(1)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 50, pdf.get_y())
            pdf.ln(5)
        elif line.startswith('## '):
            pdf.set_font('helvetica', 'B', 16)
            pdf.set_text_color(30, 58, 138)
            pdf.ln(5)
            pdf.cell(0, 10, clean_text(line[3:]), new_x="LMARGIN", new_y="NEXT", align='L')
        elif line.startswith('### '):
            pdf.set_font('helvetica', 'B', 12)
            pdf.set_text_color(0, 209, 178) # Teal
            pdf.cell(0, 10, clean_text(line[4:]), new_x="LMARGIN", new_y="NEXT", align='L')
            
        # Lists
        elif line.startswith('- '):
            pdf.set_font('helvetica', '', 11)
            pdf.set_text_color(51, 65, 85)
            pdf.set_x(15)
            pdf.multi_cell(0, 7, f'- {clean_text(line[2:])}')
        elif re.match(r'^\d+\.', line):
            pdf.set_font('helvetica', '', 11)
            pdf.set_text_color(51, 65, 85)
            pdf.set_x(15)
            pdf.multi_cell(0, 7, clean_text(line))
            
        # Tables (Very basic handling)
        elif '|' in line:
            if '---' in line: continue
            items = [clean_text(i.strip()) for i in line.split('|') if i.strip()]
            if not items: continue
            
            pdf.set_font('helvetica', 'B', 9) if 'Componente' in line else pdf.set_font('helvetica', '', 9)
            pdf.set_fill_color(241, 245, 249)
            
            col_width = 60
            for item in items:
                pdf.cell(col_width, 10, item, border=1, align='C', fill=('Componente' in line))
            pdf.ln(10)
            
        # Horizontal rule
        elif '---' in line:
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            
        # Alerts
        elif line.startswith('> [!'):
            pdf.set_fill_color(240, 253, 250)
            pdf.set_font('helvetica', 'B', 10)
            pdf.set_text_color(13, 148, 136)
            pdf.cell(0, 10, 'NOTA IMPORTANTE:', new_x="LMARGIN", new_y="NEXT", align='L', fill=True)
            pdf.set_font('helvetica', 'I', 10)
            
        # Direct text
        else:
            pdf.set_font('helvetica', '', 11)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(0, 7, display_line)

    pdf.output(output_path)

if __name__ == "__main__":
    report_md = Path(r"C:\Users\Patrick Ribeiro\.gemini\antigravity\brain\713860ad-4ad2-4e4b-b166-c3bf9e44fa58\contract_analysis_product_report.md")
    report_pdf = Path(r"C:\Users\Patrick Ribeiro\.gemini\antigravity\brain\713860ad-4ad2-4e4b-b166-c3bf9e44fa58\SmartContract_Auditor_Report.pdf")
    
    generate_pdf(report_md, report_pdf)
    print(f"PDF gerado em: {report_pdf}")
