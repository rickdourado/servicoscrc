import json
import os

def process_smart_hierarchy():
    input_file = 'scratch/jira_hierarchical_data.json'
    output_dir = 'documentacao'
    
    if not os.path.exists(input_file):
        print("Erro: Arquivo JSON não encontrado.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    issues = data.get('issues', [])
    
    # 1. Mapeamento Global
    all_items = {}
    for issue in issues:
        key = issue.get('key')
        fields = issue.get('fields', {})
        it = fields.get('issuetype', {})
        
        item = {
            'key': key,
            'summary': fields.get('summary', 'Sem título'),
            'type': it.get('name', 'N/A'),
            'is_subtask': it.get('subtask', False),
            'status': fields.get('status', {}).get('name', 'N/A'),
            'status_cat': fields.get('status', {}).get('statusCategory', {}).get('key', 'new'),
            'assignee': fields.get('assignee', {}).get('displayName', 'Não atribuído') if fields.get('assignee') else 'Não atribuído',
            'priority': fields.get('priority', {}).get('name', 'N/A'),
            'parent_key': fields.get('parent', {}).get('key') if fields.get('parent') else None,
            'subtasks': []
        }
        all_items[key] = item

    # 2. Vincular Subtarefas aos Pais
    for key, item in all_items.items():
        if item['is_subtask'] and item['parent_key'] in all_items:
            all_items[item['parent_key']]['subtasks'].append(item)

    # 3. Definição de Arquivos por Categoria de Status
    categories = {
        'new': {'file': 'tarefas_pendentes.md', 'title': '📋 Tarefas Pendentes (A Fazer)'},
        'indeterminate': {'file': 'tarefas_em_andamento.md', 'title': '🚧 Tarefas em Andamento'},
        'done': {'file': 'tarefas_concluidas.md', 'title': '✅ Tarefas Concluídas'}
    }

    for cat_key, config in categories.items():
        # Encontrar quais itens devem aparecer neste arquivo
        # Regra: Um PAI aparece se ele MESMO tem a categoria OU se QUALQUER filho tem a categoria.
        # Um FILHO aparece se ele MESMO tem a categoria.
        
        relevant_parents = {}
        
        for key, item in all_items.items():
            if item['is_subtask']:
                if item['status_cat'] == cat_key:
                    pk = item['parent_key']
                    if pk and pk in all_items:
                        if pk not in relevant_parents:
                            # Adiciona o pai para contexto
                            relevant_parents[pk] = all_items[pk].copy()
                            relevant_parents[pk]['subtasks_to_show'] = []
                        relevant_parents[pk]['subtasks_to_show'].append(item)
                    else:
                        # Subtarefa órfã com status correto
                        if key not in relevant_parents:
                            relevant_parents[key] = item.copy()
                            relevant_parents[key]['subtasks_to_show'] = []
            else:
                if item['status_cat'] == cat_key:
                    if key not in relevant_parents:
                        relevant_parents[key] = item.copy()
                        relevant_parents[key]['subtasks_to_show'] = []
                # Se o pai não tem a categoria, mas algum filho tem, ele já foi adicionado acima.

        # Geração do arquivo Markdown
        file_path = os.path.join(output_dir, config['file'])
        md_content = f"# {config['title']}\n\n"
        md_content += "Este relatório mostra as tarefas do status atual mantendo a hierarquia com seus respectivos pais para contexto.\n\n"
        md_content += "| Chave | Título / Contexto | Status Original | Responsável | Prioridade |\n"
        md_content += "| :--- | :--- | :--- | :--- | :--- |\n"
        
        # Ordenar por chave para consistência
        sorted_keys = sorted(relevant_parents.keys(), key=lambda x: int(x.split('-')[1]) if '-' in x else 0, reverse=True)
        
        for pk in sorted_keys:
            p = relevant_parents[pk]
            
            # Formatação da linha do Pai
            p_status_display = f"**{p['status']}**" if p['status_cat'] == cat_key else f"_{p['status']}_ (contexto)"
            md_content += f"| **{p['key']}** | **{p['summary']}** | {p_status_display} | {p['assignee']} | {p['priority']} |\n"
            
            # Se o pai foi incluído porque ele mesmo tem o status, podemos mostrar as subtarefas dele que também tem o status
            # Se o pai foi incluído apenas por causa de um filho, mostramos apenas os filhos relevantes.
            
            # Decidimos: Mostrar apenas as subtarefas que possuem o status deste arquivo para manter o foco.
            # Mas se o pai tem o status e não tem subtarefas relevantes, a linha do pai basta.
            
            subs_to_render = []
            if p['status_cat'] == cat_key:
                # Se o pai é do status, mostra todos os filhos que TAMBÉM são desse status
                subs_to_render = [s for s in all_items[pk]['subtasks'] if s['status_cat'] == cat_key]
            else:
                # Se o pai NÃO é do status, mostra apenas os filhos que justificaram a presença dele
                subs_to_render = p['subtasks_to_show']
            
            # Remover duplicatas se houver
            seen_subs = set()
            for s in subs_to_render:
                if s['key'] not in seen_subs:
                    md_content += f"| ↳ {s['key']} | &nbsp;&nbsp;&nbsp; {s['summary']} | **{s['status']}** | {s['assignee']} | {s['priority']} |\n"
                    seen_subs.add(s['key'])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"Gerado: {file_path}")

if __name__ == "__main__":
    process_smart_hierarchy()
