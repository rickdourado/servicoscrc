"""
anonymize_pdf.py
----------------
Anonimiza um PDF removendo dados sensiveis (PII):
  - CPF  (XXX.XXX.XXX-XX e variantes)
  - CNPJ (XX.XXX.XXX/XXXX-XX e variantes)
  - E-mails
  - Nomes proprios (Title Case: "Joao Silva da Costa")
  - Nomes institucionais em CAPS ("EMPRESA MUNICIPAL DE INFORMATICA SA - IPLANRIO")
  - Nomes de orgaos publicos com prefixo de secretaria/empresa/subprefeitura
  - Imagens embutidas (cobertas com retangulo cinza)

Saida: mesmo diretório do arquivo original, com sufixo _ANONIMIZADO.pdf

Uso:
    # PDF padrao do projeto (refs/contratos/)
    python anonymize_pdf.py

    # Qualquer PDF
    python anonymize_pdf.py <caminho_do_pdf>

    # Com sufixo customizado
    python anonymize_pdf.py <caminho_do_pdf> --suffix _REDATADO
"""

import re
import sys
import argparse
from pathlib import Path
import fitz  # PyMuPDF

# --------------------------------------------------------------------------- #
#  Padroes de PII                                                              #
# --------------------------------------------------------------------------- #

CPF_RE = re.compile(
    r"\b\d{3}[\.\s]?\d{3}[\.\s]?\d{3}[\-\.\s]?\d{2}\b"
)

CNPJ_RE = re.compile(
    r"\b\d{2}[\.\s]?\d{3}[\.\s]?\d{3}[\/\s]?\d{4}[\-\.\s]?\d{2}\b"
)

EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
)

# Nomes institucionais em CAPS:
# Ex: "EMPRESA MUNICIPAL DE INFORMATICA SA - IPLANRIO"
#     "SECRETARIA MUNICIPAL DA CASA CIVIL"
#     "SUBPREFEITURA DA BARRA DA TIJUCA"
#     "CAMARA MUNICIPAL DO RIO DE JANEIRO"
# Logica: 2+ palavras em MAIUSCULO (>=3 letras), possivelmente separadas
# por preposicoes (DE, DO, DA, DOS, DAS, E) ou hifen.
CAPS_INSTITUTION_RE = re.compile(
    r"\b("
    r"(?:SECRETARIA|SUBSECRETARIA|SUPERINTENDENCIA|COORDENADORIA|GERENCIA|"
    r"DEPARTAMENTO|DIVISAO|DIVISÃO|DIRETORIA|EMPRESA|COMPANHIA|AUTARQUIA|"
    r"FUNDACAO|FUNDAÇÃO|INSTITUTO|CAMARA|CÂMARA|SUBPREFEITURA|PREFEITURA|"
    r"MINISTERIO|MINISTÉRIO|TRIBUNAL|CONSELHO|COMISSAO|COMISSÃO|ORGAO|ÓRGÃO)"
    r"(?:\s+(?:[A-ZÁÀÃÂÉÊÍÓÔÕÚÇ]{2,}|DE|DO|DA|DOS|DAS|E|EM|PARA|COM)){1,12}"
    r"(?:\s*[-–]\s*[A-ZÁÀÃÂÉÊÍÓÔÕÚÇ][A-ZÁÀÃÂÉÊÍÓÔÕÚÇ0-9]*)?)"
    r"\b",
    re.UNICODE
)

# Nomes proprios Title Case precedidos de prefixo tipico de contratos
NAME_PREFIX_RE = re.compile(
    r"(?:"
    r"Sr\.?\s+|Sra\.?\s+|Dr\.?\s+|Dra\.?\s+|Eng\.?\s+|Engª\.?\s+|"
    r"representad[oa]?\s+por\s+|portador[a]?\s+d[oa]\s+|"
    r"nome[:\s]+|Nome[:\s]+|NOME[:\s]+|"
    r"servidor[a]?\s*[:\s]+|SERVIDOR[A]?\s*[:\s]+"
    r")"
    r"([A-ZÁÀÃÂÉÊÍÓÔÕÚÇ][a-záàãâéêíóôõúç]+(?:\s+(?:d[aeo]s?\s+)?[A-ZÁÀÃÂÉÊÍÓÔÕÚÇ][a-záàãâéêíóôõúç]+){1,5})",
    re.IGNORECASE
)

# Sequencias de palavras Title Case (nomes proprios de pessoas)
# Heuristica conservadora: 2-5 tokens capitalizados consecutivos
# Exclui stopwords comuns para nao apagar nomes de clausulas
TITLE_SEQ_STOPWORDS = {
    "Art", "Arts", "Parágrafo", "Seção", "Capítulo", "Título", "Anexo",
    "Lei", "Decreto", "Portaria", "Resolução", "Instrução", "Edital",
    "Contrato", "Termo", "Acordo", "Ajuste", "Convenio", "Convênio",
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo",
    "De", "Da", "Do", "Dos", "Das", "Em", "Na", "No", "Nos", "Nas",
    "Por", "Para", "Com", "Que", "Se", "O", "A", "Os", "As", "E",
    "Sr", "Sra", "Dr", "Dra",
    "Prefeitura", "Municipal", "Rio", "Janeiro", "Brasil", "Federal",
    "Estado", "Município", "Secretaria", "Subsecretaria", "Coordenadoria",
}

TITLE_SEQ_RE = re.compile(
    r"(?<!\w)([A-ZÁÀÃÂÉÊÍÓÔÕÚÇ][a-záàãâéêíóôõúç]{2,}"
    r"(?:\s+(?:d[aeo]s?\s+)?[A-ZÁÀÃÂÉÊÍÓÔÕÚÇ][a-záàãâéêíóôõúç]{2,}){1,4})(?!\w)"
)

# Cor de fundo das redacoes (cinza claro)
REDACT_FILL  = (0.82, 0.82, 0.82)
IMAGE_FILL   = (0.55, 0.55, 0.55)
REDACT_LABEL = "[REDATADO]"


# --------------------------------------------------------------------------- #
#  Coleta de spans PII no texto da pagina                                      #
# --------------------------------------------------------------------------- #

def collect_pii_spans(text: str) -> list[tuple[int, int]]:
    """Retorna lista de (start, end) para todos os matches de PII no texto."""
    spans: list[tuple[int, int]] = []

    # Padroes estruturados
    for pattern in [CPF_RE, CNPJ_RE, EMAIL_RE, CAPS_INSTITUTION_RE]:
        for m in pattern.finditer(text):
            spans.append((m.start(), m.end()))

    # Nomes com prefixo identificador
    for m in NAME_PREFIX_RE.finditer(text):
        spans.append((m.start(), m.end()))

    # Sequencias Title Case (pessoas)
    for m in TITLE_SEQ_RE.finditer(text):
        words = m.group(0).split()
        if len(words) < 2:
            continue
        # Ignora se TODAS as palavras sao stopwords (ex: "De Janeiro")
        meaningful = [w for w in words if w not in TITLE_SEQ_STOPWORDS]
        if not meaningful:
            continue
        spans.append((m.start(), m.end()))

    return spans


# --------------------------------------------------------------------------- #
#  Redacoes por pagina                                                         #
# --------------------------------------------------------------------------- #

def redact_text_in_page(page: fitz.Page) -> int:
    """
    Identifica e marca para redacao todos os spans de texto que contem PII.
    Retorna a contagem de redacoes adicionadas.
    """
    full_text = page.get_text("text")
    pii_spans = collect_pii_spans(full_text)
    if not pii_spans:
        return 0

    text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
    count = 0
    char_offset = 0

    for block in text_dict.get("blocks", []):
        if block.get("type") != 0:   # Apenas blocos de texto
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                span_text  = span.get("text", "")
                span_start = char_offset
                span_end   = char_offset + len(span_text)

                for (ps, pe) in pii_spans:
                    if span_start < pe and span_end > ps:
                        bbox = fitz.Rect(span["bbox"])
                        page.add_redact_annot(
                            bbox,
                            text=REDACT_LABEL,
                            fontsize=6,
                            fill=REDACT_FILL,
                        )
                        count += 1
                        break

                char_offset += len(span_text)
            char_offset += 1   # \n de quebra de linha
        char_offset += 1       # separador de bloco

    return count


def redact_images_in_page(page: fitz.Page) -> int:
    """Cobre todas as imagens embutidas com um retangulo cinza escuro."""
    count = 0
    for img_info in page.get_images(full=True):
        xref = img_info[0]
        for rect in page.get_image_rects(xref):
            page.add_redact_annot(
                rect,
                text="[IMAGEM REMOVIDA]",
                fontsize=7,
                fill=IMAGE_FILL,
            )
            count += 1
    return count


# --------------------------------------------------------------------------- #
#  Funcao principal de anonimizacao                                            #
# --------------------------------------------------------------------------- #

def anonymize_pdf(input_path: Path, output_suffix: str = "_ANONIMIZADO") -> Path:
    """
    Anonimiza o PDF em `input_path` e salva com `output_suffix` no nome.
    Retorna o caminho do arquivo gerado.
    """
    output_path = input_path.with_stem(input_path.stem + output_suffix)
    doc = fitz.open(str(input_path))

    total_text = 0
    total_imgs = 0

    print(f"\n[PDF] Processando : {input_path.name}")
    print(f"      Paginas      : {len(doc)}")
    print(f"      Saida        : {output_path.name}")
    print()

    for i, page in enumerate(doc):
        imgs  = redact_images_in_page(page)
        texts = redact_text_in_page(page)
        page.apply_redactions()

        total_text += texts
        total_imgs += imgs

        if texts + imgs > 0:
            print(f"      Pag {i+1:>3}: {texts:>4} redacoes de texto | {imgs:>2} imagens")

    doc.save(str(output_path), garbage=4, deflate=True)
    doc.close()

    print()
    print(f"[OK] Salvo em           : {output_path}")
    print(f"[STATS] Texto redatado  : {total_text}")
    print(f"[STATS] Imagens cobertas: {total_imgs}")

    return output_path


# --------------------------------------------------------------------------- #
#  Entry point CLI                                                             #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Anonimiza PDFs removendo CPF, CNPJ, nomes e imagens."
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        help="Caminho do PDF a anonimizar. "
             "Padrao: refs/contratos/ContratoCZRM.pdf",
    )
    parser.add_argument(
        "--suffix",
        default="_ANONIMIZADO",
        help="Sufixo do arquivo de saida (padrao: _ANONIMIZADO)",
    )
    args = parser.parse_args()

    if args.pdf:
        pdf_path = Path(args.pdf)
    else:
        pdf_path = (
            Path(__file__).parents[2] / "refs" / "contratos" / "ContratoCZRM.pdf"
        )

    if not pdf_path.exists():
        print(f"[ERRO] Arquivo nao encontrado: {pdf_path}")
        sys.exit(1)

    anonymize_pdf(pdf_path, output_suffix=args.suffix)
