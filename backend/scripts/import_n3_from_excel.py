"""
Script: import_n3_from_excel.py
Objetivo: Substituir os N3 do servicos.json pelos serviços PUBLICADOS do ServicosN3.xlsx,
          mantendo a estrutura N1/N2 original. Usa categoria/sub_categoria do Excel para
          mapear para o N2 correto via similaridade. Descrições vindas do servicosconsolidados.csv.
"""

import openpyxl
import re
import json
import csv
import uuid
import shutil
from pathlib import Path
from collections import defaultdict

# ── Caminhos ────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
XLSX = Path("/home/ssdlinux/Documents/dev/servicoscrc/refs/planilhas/ServicosN3.xlsx")
JSON_PATH  = BASE / "data" / "servicos.json"
CSV_PATH   = BASE / "data" / "servicosconsolidados.csv"
BACKUP     = BASE / "data" / "servicos_pre_import_n3.json"

# ── Helpers ──────────────────────────────────────────────────────────────────
def extract_value(cell_val):
    """Extrai o valor real de células com fórmula IFERROR do Google Sheets."""
    if cell_val is None:
        return None
    s = str(cell_val)
    m = re.search(r',\"(.+)\"\)$', s)
    if m:
        return m.group(1).strip()
    return s.strip()

def norm(s: str) -> str:
    """Normaliza string para comparação: minúsculas, sem acentos básicos, sem pontuação extra."""
    import unicodedata
    s = s.lower().strip()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def token_overlap(a: str, b: str) -> float:
    """Retorna fração de tokens de 'a' presentes em 'b'."""
    ta = set(norm(a).split())
    tb = set(norm(b).split())
    if not ta:
        return 0.0
    return len(ta & tb) / len(ta)

def best_match(query: str, candidates: list[str], threshold: float = 0.4) -> str | None:
    """Retorna o candidato com maior sobreposição de tokens, acima do threshold."""
    best, best_score = None, 0.0
    for c in candidates:
        score = max(token_overlap(query, c), token_overlap(c, query))
        if score > best_score:
            best_score, best = score, c
    return best if best_score >= threshold else None

def make_id() -> str:
    return uuid.uuid4().hex[:8]

# ── 1. Carregar publicados do Excel ──────────────────────────────────────────
print("📄 Lendo ServicosN3.xlsx...")
wb = openpyxl.load_workbook(XLSX, read_only=True)
ws = wb['Serviços']

publicados = []
for row in ws.iter_rows(min_row=2, values_only=True):
    titulo    = extract_value(row[0])
    categoria = extract_value(row[2])
    sub_cat   = extract_value(row[3])
    status    = extract_value(row[4])
    if titulo and titulo != 'titulo_servico' and status and 'publicado' in status.lower():
        publicados.append({
            'titulo': titulo,
            'categoria': categoria or '',
            'sub_cat': sub_cat or ''
        })

print(f"   {len(publicados)} serviços publicados encontrados.")

# ── 2. Carregar descrições do CSV ────────────────────────────────────────────
print("📄 Lendo servicosconsolidados.csv...")
desc_map: dict[str, str] = {}
with open(CSV_PATH, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        titulo = row.get('titulo_servico', '').strip()
        desc   = row.get('descricao_completa', '').strip()
        if titulo:
            desc_map[norm(titulo)] = desc

print(f"   {len(desc_map)} descrições disponíveis.")

# ── 3. Carregar servicos.json ────────────────────────────────────────────────
print("📄 Lendo servicos.json...")
with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

# ── 4. Montar índice N1->N2 para lookup ─────────────────────────────────────
# Estrutura: subtheme_index[n1_name][n2_name] = ref ao objeto subtheme
subtheme_index: dict[str, dict[str, dict]] = {}
for tema in data['items']:
    subtheme_index[tema['name']] = {}
    for sub in tema.get('subthemes', []):
        subtheme_index[tema['name']][sub['name']] = sub

# Listas planas de nomes para fuzzy matching
n1_names = [t['name'] for t in data['items']]
n2_flat  = [(t['name'], s['name']) for t in data['items'] for s in t.get('subthemes', [])]

# ── 5. Mapeamento manual Excel-categoria -> N1 ───────────────────────────────
# Garante mapeamento correto para categorias cujos nomes divergem bastante
CATEGORIA_TO_N1 = {
    'animais':                               'Animais',
    'cidadania':                             'Cidadania',
    'cidade':                                'Serviços urbanos',
    'cultura':                               'Cultura, Esporte e Lazer',
    'educacao':                              'Educação',
    'lei geral de protecao de dados lgpd':   'Transparência',
    'lei de acesso a informacao lai':        'Transparência',
    'licencas':                              'Licenças, Alvarás e Permissões',
    'meio ambiente':                         'Meio Ambiente',
    'obras':                                 'Licenças, Alvarás e Permissões',
    'ordem publica':                         'Ordem pública',
    'ouvidoria':                             'Ouvidoria',
    'saude':                                 'Saúde',
    'servidor':                              'Administração pública',
    'trabalho':                              'Trabalho',
    'transporte':                            'Transporte',
    'tributos':                              'Tributos',
    'transito':                              'Trânsito',
    'central anticorrupcao':                 'Transparência',
}

# Mapeamento manual Excel sub_categoria -> N2 para casos ambíguos
SUBCAT_TO_N2 = {
    ('Animais', 'animais domesticos'):     'Saúde animal',
    ('Animais', 'animais silvestres'):     'Proteção aos animais',
    ('Animais', 'atendimento clinico'):    'Saúde animal',
    ('Animais', 'campanhas'):              'Proteção aos animais',
    ('Cidadania', 'assistencia social'):   'Assistência social',
    ('Cidadania', 'acessibilidade'):       'Acessibilidade',
    ('Cidadania', 'intolerancia religiosa e racial'): 'Direitos Humanos',
    ('Cidadania', 'mulher carioca'):       'Mulher carioca',
    ('Cidadania', 'procon carioca'):       'PROCON carioca',
    ('Cidadania', 'suporte tecnico e teleatendimento'): 'Participação social',
    ('Serviços urbanos', 'conservacao'):   'Conservação',
    ('Serviços urbanos', 'fiscalizacao'):  'Conservação',
    ('Serviços urbanos', 'iluminacao publica'): 'Iluminação pública',
    ('Serviços urbanos', 'imoveis'):       'Conservação',
    ('Serviços urbanos', 'limpeza urbana'): 'Limpeza',
    ('Serviços urbanos', 'pracas e parques'): 'Conservação',
    ('Serviços urbanos', 'servico funerario'): 'Serviços funerários',
    ('Cultura, Esporte e Lazer', 'audiovisual'):      'Audiovisual',
    ('Cultura, Esporte e Lazer', 'carnaval'):         'Espaços culturais',
    ('Cultura, Esporte e Lazer', 'equipamentos culturais'): 'Espaços culturais',
    ('Cultura, Esporte e Lazer', 'esportes e lazer'): 'Atividade física',
    ('Cultura, Esporte e Lazer', 'incentivo cultural'): 'Incentivo cultural',
    ('Cultura, Esporte e Lazer', 'turismo'):          'Espaços culturais',
    ('Educação', 'bibliotecas'):           'Bibliotecas',
    ('Educação', 'cursos'):                'Cursos',
    ('Educação', 'educacao fundamental'):  'Ensino Fundamental e Médio',
    ('Educação', 'educacao especial'):     'Educação Especial',
    ('Educação', 'educacao infantil'):     'Educação Infantil',
    ('Educação', 'matricula'):             'Matrícula escolar',
    ('Educação', 'multirrio'):             'MultiRio',
    ('Educação', 'vida escolar'):          'Vida escolar',
    ('Transparência', 'informacoes'):      'Proteção de dados (LGPD)',
    ('Transparência', 'transparencia'):    'Acesso à Informação (LAI)',
    ('Transparência', 'denuncia'):         'Anticorrupção',
    ('Licenças, Alvarás e Permissões', 'alvara'):      'Atividade econômica',
    ('Licenças, Alvarás e Permissões', 'certidoes'):   'Atividade econômica',
    ('Licenças, Alvarás e Permissões', 'licencas'):    'Ambientais',
    ('Licenças, Alvarás e Permissões', 'licitacao e pregao'): 'Atividade econômica',
    ('Licenças, Alvarás e Permissões', 'licenciamento'): 'Urbanísticas',
    ('Meio Ambiente', 'poluicao da agua'): 'Poluição urbana',
    ('Meio Ambiente', 'poluicao do ar'):   'Poluição urbana',
    ('Meio Ambiente', 'protecao'):         'Parques',
    ('Meio Ambiente', 'arvores'):          'Arborização',
    ('Ordem pública', 'perturbacao do sossego'): 'Perturbação do sossego',
    ('Ordem pública', 'comercio'):         'Comércio ambulante',
    ('Ordem pública', 'estacionamento irregular'): 'Estacionamento irregular',
    ('Ordem pública', 'feiras'):           'Feiras',
    ('Ouvidoria', 'reclamacao'):           'Reclamação',
    ('Saúde', 'atendimento ambulatorial'): 'Atendimento ambulatorial / Consultas e exames / Clínicas da Família e Postos de Saúde',
    ('Saúde', 'atendimento medico'):       'Emergência / UPAs e Centros de Emergência',
    ('Saúde', 'auxilios'):                 'Auxílios em saúde',
    ('Saúde', 'cegonha carioca'):          'Gestação e Primeira infância',
    ('Saúde', 'consultas e exames'):       'Atendimento ambulatorial / Consultas e exames / Clínicas da Família e Postos de Saúde',
    ('Saúde', 'dengue'):                   'Dengue',
    ('Saúde', 'medicamentos'):             'Medicamentos',
    ('Saúde', 'pronto atendimento'):       'Emergência / UPAs e Centros de Emergência',
    ('Saúde', 'vacinacao'):                'Vacinação',
    ('Saúde', 'vigilancia sanitaria'):     'Vigilância Sanitária',
    ('Administração pública', 'beneficios'):    'Benefícios',
    ('Administração pública', 'pagamentos'):    'Solicitações do servidor',
    ('Administração pública', 'saude do servidor'): 'Saúde do servidor',
    ('Trabalho', 'emprego e estagio'):     'Emprego formal',
    ('Transporte', 'brt'):                 'BRT',
    ('Transporte', 'bicicletas'):          'Bicicletas',
    ('Transporte', 'estacionamento'):      'Tarifas',
    ('Transporte', 'gratuidade'):          'Gratuidade',
    ('Transporte', 'jae'):                 'Jaé',
    ('Transporte', 'mobilidade urbana'):   'Ônibus',
    ('Transporte', 'processos'):           'Táxi',
    ('Transporte', 'transporte complementar'): 'Vans e kombis',
    ('Transporte', 'transporte escolar'):  'Transporte escolar',
    ('Transporte', 'taxi e mototaxi'):     'Táxi',
    ('Transporte', 'vlt'):                 'VLT',
    ('Transporte', 'veiculos'):            'Táxi',
    ('Transporte', 'onibus'):              'Ônibus',
    ('Tributos', 'certidoes'):             'ISS',
    ('Tributos', 'divida ativa'):          'Dívida Ativa',
    ('Tributos', 'iptu'):                  'ISS',
    ('Tributos', 'iss'):                   'ISS',
    ('Tributos', 'itbi'):                  'ISS',
    ('Tributos', 'imposto'):               'ISS',
    ('Tributos', 'nota carioca'):          'Nota Carioca',
    ('Trânsito', 'estacionamento'):        'Estacionamento',
    ('Trânsito', 'multas'):                'Multas',
    ('Trânsito', 'sinalizacao grafica'):   'Placas e sinal de trânsito',
}

# ── 6. Limpar N3 de todos os N2 ──────────────────────────────────────────────
print("🧹 Limpando N3 existentes...")
for tema in data['items']:
    for sub in tema.get('subthemes', []):
        sub['services'] = []

# ── 7. Mapear e inserir publicados ───────────────────────────────────────────
print("🔀 Mapeando e inserindo publicados...")
unmapped = []
mapped_count = 0

for srv in publicados:
    titulo    = srv['titulo']
    categoria = srv['categoria']
    sub_cat   = srv['sub_cat']

    # --- Encontrar N1 ---
    n1_name = CATEGORIA_TO_N1.get(norm(categoria))
    if not n1_name:
        # Fuzzy fallback
        n1_name = best_match(categoria, n1_names, threshold=0.35)

    if not n1_name or n1_name not in subtheme_index:
        unmapped.append({'titulo': titulo, 'motivo': f'N1 não encontrado para categoria={categoria!r}'})
        continue

    # --- Encontrar N2 ---
    key = (n1_name, norm(sub_cat))
    n2_name = SUBCAT_TO_N2.get(key)

    if not n2_name:
        # Fuzzy dentro do N1
        n2_candidates = list(subtheme_index[n1_name].keys())
        combined_query = f"{categoria} {sub_cat}"
        n2_name = best_match(combined_query, n2_candidates, threshold=0.3)
        if not n2_name:
            n2_name = best_match(sub_cat, n2_candidates, threshold=0.25)

    if not n2_name or n2_name not in subtheme_index[n1_name]:
        # Último recurso: primeiro N2 do N1
        n2_candidates = list(subtheme_index[n1_name].keys())
        if n2_candidates:
            n2_name = n2_candidates[0]
        else:
            unmapped.append({'titulo': titulo, 'motivo': f'N2 não encontrado para sub_cat={sub_cat!r} em N1={n1_name!r}'})
            continue

    # --- Buscar descrição ---
    descricao = desc_map.get(norm(titulo), '')
    if not descricao:
        # Fuzzy no CSV
        best_desc_key = best_match(titulo, list(desc_map.keys()), threshold=0.5)
        if best_desc_key:
            descricao = desc_map[best_desc_key]

    # --- Inserir N3 ---
    subtheme_index[n1_name][n2_name]['services'].append({
        'id': make_id(),
        'name': titulo,
        'description': descricao
    })
    mapped_count += 1

print(f"   ✅ Mapeados: {mapped_count}")
print(f"   ⚠️  Não mapeados: {len(unmapped)}")
if unmapped:
    for u in unmapped:
        print(f"      - {u['titulo'][:60]} | {u['motivo']}")

# ── 8. Estatísticas por N2 ───────────────────────────────────────────────────
print("\n📊 Serviços por N1/N2 após importação:")
total_n3 = 0
for tema in data['items']:
    subs_com_srv = [(s['name'], len(s['services'])) for s in tema.get('subthemes', []) if s['services']]
    if subs_com_srv:
        print(f"  [{tema['name']}]")
        for n2, cnt in subs_com_srv:
            print(f"    {n2}: {cnt}")
            total_n3 += cnt

print(f"\n  Total N3 inseridos: {total_n3}")

# ── 9. Backup + salvar ───────────────────────────────────────────────────────
print(f"\n💾 Backup em {BACKUP.name}...")
shutil.copy(JSON_PATH, BACKUP)

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ servicos.json atualizado com {total_n3} serviços N3 publicados.")
