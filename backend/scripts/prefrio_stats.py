"""
Módulo para análise de estatísticas dos serviços PrefRio.
Lê dados do CSV pré-processado (mais leve que Excel).
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List
import os

# Resolve base dir robustly for both local and PythonAnywhere
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Allow override via env var for production (PythonAnywhere)
if os.environ.get("BASE_DIR"):
    BASE_DIR = Path(os.environ.get("BASE_DIR"))

CSV_PATH = BASE_DIR / "backend" / "data" / "prefrio_servicos.csv"

print(f"[DEBUG] prefrio_stats.py - BASE_DIR: {BASE_DIR}")
print(f"[DEBUG] prefrio_stats.py - CSV_PATH: {CSV_PATH}")
print(f"[DEBUG] prefrio_stats.py - CSV exists: {CSV_PATH.exists()}")


def load_data() -> pd.DataFrame:
    """Carrega dados do CSV."""
    if not CSV_PATH.exists():
        # Debug info for troubleshooting
        cwd = Path.cwd()
        raise FileNotFoundError(
            f"CSV não encontrado: {CSV_PATH}\n"
            f"Working dir: {cwd}\n"
            f"BASE_DIR: {BASE_DIR}\n"
            f"Conteúdo de backend/data/: {list((BASE_DIR / 'backend' / 'data').glob('*')) if (BASE_DIR / 'backend' / 'data').exists() else 'diretório não existe'}\n"
            "Execute: python backend/scripts/export_prefrio_csv.py"
        )

    return pd.read_csv(CSV_PATH, encoding='utf-8-sig')


def get_orgaos_stats() -> List[Dict]:
    """
    Retorna estatísticas de serviços por órgão.

    Returns:
        Lista de dicts com: nome_orgao, total_servicos
    """
    df = load_data()

    # Conta serviços únicos por órgão
    stats = (
        df.groupby('nome_orgao')['titulo_servico']
        .nunique()
        .reset_index()
        .rename(columns={'titulo_servico': 'total_servicos'})
        .sort_values('total_servicos', ascending=False)
    )

    return stats.to_dict('records')


def get_summary() -> Dict:
    """
    Retorna resumo geral dos dados.

    Returns:
        Dict com: total_registros, total_orgaos, total_servicos
    """
    df = load_data()

    return {
        'total_registros': len(df),
        'total_orgaos': df['nome_orgao'].nunique(),
        'total_servicos': df['titulo_servico'].nunique(),
    }


def search_services(orgao_filter: str = None, relevancia_filter: str = None) -> List[Dict]:
    """
    Busca serviços com filtros opcionais.

    Args:
        orgao_filter: Nome do órgão para filtrar (None retorna todos)
        relevancia_filter: Filtro de análise de relevância (None retorna todos)

    Returns:
        Lista de dicts com: titulo_servico, nome_orgao, categoria, status_do_servico, analise_relevancia
    """
    df = load_data()

    if orgao_filter:
        df = df[df['nome_orgao'] == orgao_filter]

    if relevancia_filter:
        df = df[df['analise_relevancia'] == relevancia_filter]

    # Seleciona colunas relevantes
    result = df[['titulo_servico', 'nome_orgao', 'categoria', 'status_do_servico', 'analise_relevancia']].copy()

    # Converte NaN para string vazia (evita NaN no JSON)
    result = result.fillna('')

    return result.to_dict('records')


def get_relevancia_options() -> List[str]:
    """
    Retorna opções únicas de análise de relevância.

    Returns:
        Lista de valores únicos (ordenados)
    """
    df = load_data()
    options = df['analise_relevancia'].dropna().unique().tolist()
    return sorted(options)
