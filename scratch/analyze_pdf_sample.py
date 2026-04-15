from pypdf import PdfReader
import sys

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

if __name__ == "__main__":
    pdf_path = "/home/ssdlinux/Documents/dev/servicoscrc/refs/Relatório – 002_2026 150426  .pdf"
    content = extract_text(pdf_path)
    # Print only near the Anexo I section to see formatting
    idx = content.find("ANEXO I")
    if idx != -1:
        print(content[idx:idx+2000])
    else:
        print("ANEXO I não encontrado. Primeiros 2000 caracteres:")
        print(content[:2000])
