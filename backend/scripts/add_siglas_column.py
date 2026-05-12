"""
Add siglas column to prefrio_servicos.csv by matching organ names.
Handles name variations with fuzzy matching.
"""
import csv
from pathlib import Path
from difflib import SequenceMatcher

# Mapping from orgaos_organizado.md
ORGAOS_SIGLAS = {
    "Gabinete do Prefeito": "GBP",
    "Gabinete do Vice-Prefeito": "GVP",
    "Secretaria Municipal de Governo": "SMG",
    "Secretaria Municipal da Casa Civil": "CVL",
    "Secretaria Municipal de Coordenação Governamental": "SMCG",
    "Secretaria Municipal de Fazenda": "SMF",
    "Secretaria Municipal de Integridade, Transparência e Proteção de Dados": "SMIT",
    "Secretaria Municipal de Desenvolvimento Urbano e Licenciamento": "SMDU",
    "Secretaria Municipal de Desenvolvimento Econômico": "SMDE",
    "Secretaria Municipal de Infraestrutura": "SMI",
    "Secretaria Municipal de Transportes": "SMTR",
    "Secretaria Municipal de Conservação": "SECONSERVA",
    "Secretaria Municipal de Educação": "SME",
    "Secretaria Municipal de Assistência Social": "SMAS",
    "Secretaria Municipal de Saúde": "SMS",
    "Secretaria Municipal de Administração": "SMA",
    "Secretaria Municipal de Trabalho e Renda": "SMTE",
    "Secretaria Municipal de Cultura": "SMC",
    "Secretaria Municipal da Pessoa com Deficiência": "SMPD",
    "Secretaria Municipal do Ambiente e Clima": "SMAC",
    "Secretaria de Esportes": "SMEL",
    "Secretaria Municipal de Habitação": "SMH",
    "Secretaria Municipal de Ciência, Tecnologia e Inovação": "SMCT",
    "Secretaria Mun. do Envelhecimento Saudável e Qualidade de Vida": "SEMESQV",
    "Secretaria Municipal de Ordem Pública": "SEOP",
    "Secretaria Municipal de Proteção e Defesa dos Animais": "SMPDA",
    "Secretaria Municipal de Turismo": "SMTUR-RIO",
    "Secretaria Especial de Proteção e Defesa do Consumidor": "SEDECON",
    "Secretaria Especial de Políticas para Mulheres e Cuidados": "SPM-RIO",
    "Secretaria Especial da Juventude Carioca": "JUV-RIO",
    "Secretaria Especial de Ação Comunitária": "SEAC-RIO",
    "Secretaria Especial de Cidadania e Família": "SECID",
    "Secretaria Especial de Integração Metropolitana": "SEIM",
    "Secretaria Especial de Economia Solidária": "SES-RIO",
    "Secretaria Especial de Direitos Humanos e Igualdade Racial": "SEDHIR",
    "Secretaria Especial de Gestão de Grandes Projetos": "SEGP",
    "Secretaria Especial de Inclusão": "SINC-RIO",
    "Arquivo Geral da Cidade do Rio de Janeiro": "C/ARQ",
    "Controladoria Geral do Município": "CGM-RIO",
    "Procuradoria Geral do Município": "PGM",
    "Instituto de Previdência e Assistência": "PREVI-RIO",
    "Instituto Fundação João Goulart": "CVL/FJG",
    "Instituto Municipal de Urbanismo Pereira Passos": "IPP",
    "Instituto Municipal de Vigilância Sanitária, Vigilância de Zoonoses e de Inspeção Agropecuária": "S/IVISA-RIO",
    "Guarda Municipal do Rio de Janeiro": "GM-RIO",
    "Fundação Instituto de Geotécnica do Município do Rio de Janeiro": "GEO-RIO",
    "Fundação Instituto das Águas do Município do Rio de Janeiro": "RIO-ÁGUAS",
    "Fundação Parques e Jardins": "FPJ",
    "Fundação Planetário da Cidade do Rio de Janeiro": "PLANETÁRIO",
    "Fundação Jardim Zoológico da Cidade do Rio de Janeiro": "RIO-ZOO",
    "Fundação Cidade das Artes": "CIDADE DAS ARTES",
    "Empresa Municipal de Multimeios S.A.": "MULTIRIO",
    "Empresa Distribuidora de Filmes S.A.": "RIOFILME",
    "Empresa Municipal de Informática": "IPLANRIO",
    "Empresa Municipal de Artes Gráficas": "IMPRENSA DA CIDADE",
    "Companhia Carioca de Parcerias e Investimentos": "CCPAR",
    "Empresa Municipal de Urbanização": "RIO-URBE",
    "Empresa de Turismo do Município do Rio de Janeiro": "RIOTUR",
    "Empresa Pública de Saúde do Rio de Janeiro": "RIOSAÚDE",
    "Companhia Municipal de Energia e Iluminação": "RIOLUZ",
    "Companhia Municipal de Limpeza Urbana": "COMLURB",
    "Companhia de Engenharia de Tráfego do RJ": "CET-RIO",
    "Companhia Municipal de Transportes Coletivos": "CMTC-RIO",
    "Riocentro S.A. - Centro de Feiras, Exposições e Congressos do Rio de Janeiro": "RIOCENTRO",
    "Agência de Fomento do Município do Rio de Janeiro S.A.": "INVEST.RIO",
    "Empresa de Eventos do Município do Rio de Janeiro": "RIOEVENTOS",
    "Instituto Rio Patrimônio da Humanidade": "IRPH",
}

# Manual mappings for known variations
MANUAL_MAPPINGS = {
    "Coordenadoria de Licenciamento e Fiscalização": "SMDU",  # Part of SMDU
    "Secretaria Municipal de Conservação e Serviços Públicos": "SECONSERVA",
    "Procuradoria Geral do Município do Rio de Janeiro": "PGM",
    "Instituto de Previdência e Assistência do Município do Rio de Janeiro": "PREVI-RIO",
    "Controladoria Geral do Município do Rio de Janeiro": "CGM-RIO",
    "Distribuidora de Filmes S.A. - RIOFILME": "RIOFILME",
    # Subsecretarias and sub-units
    "Coordenadoria de Controle Urbano": "SMDU",  # Part of SMDU
    "Superintendência Executiva de Patrimônio Imobiliário": "SMF",  # Part of SMF
    "Subsecretaria de Proteção e Defesa Civil": "SEOP",  # Part of SEOP
    "Subsecretaria de Transformação Digital e Cidade Inteligente": "SMG",  # Part of SMG
    "Subsecretaria de Planejamento e Acompanhamento de Resultados": "SMG",  # Part of SMG
}


def similarity(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_sigla(nome_orgao: str) -> str:
    """Find sigla for organ name with fuzzy matching."""
    if not nome_orgao or nome_orgao.strip() == "":
        return ""

    nome_orgao = nome_orgao.strip()

    # Check manual mappings first
    if nome_orgao in MANUAL_MAPPINGS:
        return MANUAL_MAPPINGS[nome_orgao]

    # Check exact match
    if nome_orgao in ORGAOS_SIGLAS:
        return ORGAOS_SIGLAS[nome_orgao]

    # Fuzzy match - find best match above 0.8 threshold
    best_match = None
    best_ratio = 0.8

    for orgao_ref, sigla in ORGAOS_SIGLAS.items():
        ratio = similarity(nome_orgao, orgao_ref)
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = sigla

    if best_match:
        return best_match

    # No match found - return empty or flag for manual review
    print(f"⚠️  No match for: {nome_orgao}")
    return "REVISAR"


def add_siglas_column():
    """Add siglas column to CSV."""
    csv_path = Path(__file__).parent.parent / "data" / "prefrio_servicos.csv"

    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    # Add sigla_orgao column if not exists
    if 'sigla_orgao' not in fieldnames:
        fieldnames = list(fieldnames)
        # Insert after nome_orgao
        nome_orgao_idx = fieldnames.index('nome_orgao')
        fieldnames.insert(nome_orgao_idx + 1, 'sigla_orgao')

    # Process rows
    no_match_count = 0
    for row in rows:
        nome_orgao = row.get('nome_orgao', '')
        sigla = find_sigla(nome_orgao)
        row['sigla_orgao'] = sigla
        if sigla == "REVISAR":
            no_match_count += 1

    # Write updated CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Updated {len(rows)} rows")
    print(f"⚠️  {no_match_count} rows need manual review (sigla_orgao='REVISAR')")


if __name__ == "__main__":
    add_siglas_column()
