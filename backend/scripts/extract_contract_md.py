"""
extract_contract_md.py
-----------------------
Extrai o texto de um PDF anonimizado e gera um arquivo Markdown estruturado,
preservando a hierarquia de cláusulas e seções.

Uso:
    python extract_contract_md.py                            # usa ContratoCZRM_ANONIMIZADO.pdf
    python extract_contract_md.py <caminho_do_pdf>
    python extract_contract_md.py <caminho_do_pdf> --out <destino.md>
"""

import re
import sys
import argparse
from pathlib import Path
import fitz  # PyMuPDF


# --------------------------------------------------------------------------- #
#  Heurísticas de formatação de seção                                         #
# --------------------------------------------------------------------------- #

CLAUSULA_RE = re.compile(
    r"^(CL[AÁ]USULA|CL\.\s*\d|ART(?:IGO)?\.?\s*\d|§\s*\d|PARÁGRAFO)",
    re.IGNORECASE,
)

SECAO_RE = re.compile(
    r"^(SEÇÃO|CAPÍTULO|TÍTULO|ANEXO|TABELA|QUADRO)",
    re.IGNORECASE,
)

ALL_CAPS_LINE_RE = re.compile(r"^[A-ZÁÀÃÂÉÊÍÓÔÕÚÇ\s\d\.\-\/]{8,}$")


def classify_line(line: str) -> str:
    """Retorna 'heading1', 'heading2', 'heading3', ou 'body' para uma linha."""
    stripped = line.strip()
    if not stripped:
        return "empty"
    if SECAO_RE.match(stripped):
        return "heading1"
    if CLAUSULA_RE.match(stripped):
        return "heading2"
    if ALL_CAPS_LINE_RE.match(stripped) and len(stripped.split()) <= 12:
        return "heading3"
    return "body"


# --------------------------------------------------------------------------- #
#  Extração                                                                    #
# --------------------------------------------------------------------------- #

def extract_pages(doc: fitz.Document) -> list[tuple[int, str]]:
    """Retorna lista de (num_pagina, texto) para cada página."""
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages.append((i + 1, text))
    return pages


def build_markdown(pages: list[tuple[int, str]], source_name: str) -> str:
    """Converte páginas extraídas em Markdown estruturado."""
    lines_md = []

    # Cabeçalho do documento
    lines_md.append(f"# {source_name}\n")
    lines_md.append(
        "> **Aviso**: Este documento é uma versão anonimizada gerada automaticamente. "
        "Dados pessoais, identificadores e imagens foram removidos para fins de análise por IA.\n"
    )

    for page_num, raw_text in pages:
        lines_md.append(f"\n---\n<!-- Página {page_num} -->\n")

        # Quebra em linhas e classifica
        raw_lines = raw_text.splitlines()
        prev_class = "empty"

        for raw_line in raw_lines:
            stripped = raw_line.strip()
            if not stripped:
                if prev_class != "empty":
                    lines_md.append("")
                prev_class = "empty"
                continue

            cls = classify_line(stripped)

            if cls == "heading1":
                lines_md.append(f"\n## {stripped}\n")
            elif cls == "heading2":
                lines_md.append(f"\n### {stripped}\n")
            elif cls == "heading3":
                lines_md.append(f"\n#### {stripped}\n")
            else:
                # Corpo: detecta continuação de parágrafo
                if prev_class == "body":
                    # Mesmo parágrafo: apenas adiciona espaço
                    last = lines_md[-1] if lines_md else ""
                    if last and not last.endswith("\n"):
                        lines_md[-1] = last + " " + stripped
                    else:
                        lines_md.append(stripped)
                else:
                    lines_md.append(stripped)

            prev_class = cls

    return "\n".join(lines_md)


# --------------------------------------------------------------------------- #
#  Função principal                                                            #
# --------------------------------------------------------------------------- #

def extract_contract_md(input_path: Path, output_path: Path | None = None) -> Path:
    """
    Extrai texto do PDF anonimizado e salva como Markdown.
    Retorna o caminho do arquivo .md gerado.
    """
    if output_path is None:
        output_path = input_path.with_suffix(".md")

    doc = fitz.open(str(input_path))
    source_name = input_path.stem.replace("_", " ").title()

    print(f"\n[EXTRACT] Fonte : {input_path.name}")
    print(f"          Paginas: {len(doc)}")
    print(f"          Saida  : {output_path}")

    pages = extract_pages(doc)
    doc.close()

    md_content = build_markdown(pages, source_name)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content, encoding="utf-8")

    size_kb = output_path.stat().st_size / 1024
    print(f"\n[OK] Markdown gerado: {output_path}")
    print(f"     Tamanho        : {size_kb:.1f} KB")
    print(f"     Linhas         : {md_content.count(chr(10))}")

    return output_path


# --------------------------------------------------------------------------- #
#  Entry point CLI                                                             #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extrai texto de PDF anonimizado para Markdown estruturado."
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        help="Caminho do PDF anonimizado. Padrao: refs/contratos/ContratoCZRM_ANONIMIZADO.pdf",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Caminho de saida do .md. Padrao: backend/prompts/czrm/<nome>.md",
    )
    args = parser.parse_args()

    # Resolve caminho do PDF
    if args.pdf:
        pdf_path = Path(args.pdf)
    else:
        pdf_path = (
            Path(__file__).parents[2]
            / "refs" / "contratos" / "ContratoCZRM_ANONIMIZADO.pdf"
        )

    if not pdf_path.exists():
        print(f"[ERRO] Arquivo nao encontrado: {pdf_path}")
        sys.exit(1)

    # Resolve caminho de saída
    if args.out:
        out_path = Path(args.out)
    else:
        # Padrão: backend/prompts/czrm/<nome_do_pdf>.md
        out_path = (
            Path(__file__).parents[2]
            / "backend" / "prompts" / "czrm"
            / pdf_path.with_suffix(".md").name
        )

    extract_contract_md(pdf_path, out_path)
