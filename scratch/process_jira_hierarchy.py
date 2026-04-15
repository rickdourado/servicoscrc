import json
import os

def process_hierarchy():
    input_file = 'scratch/jira_full_data.json'
    output_dir = 'documentacao'
    
    if not os.path.exists(input_file):
        print("Erro: Arquivo JSON não encontrado.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    issues = data.get('issues', [])
    
    # Mapeamento e Agrupamento
    issue_map = {}
    parents = []
    subtasks_orphan = [] # Subtarefas cujo pai não está na lista (raro, mas possível)
    
    for issue in issues:
        key = issue.get('key')
        fields = issue.get('fields', {})
        issue_type = fields.get('issuetype', {})
        is_subtask = issue_type.get('subtask', False)
        
        item = {
            'key': key,
            'summary': fields.get('summary', 'Sem título'),
            'type': issue_type.get('name', 'N/A'),
            'status': fields.get('status', {}).get('name', 'N/A'),
            'category': fields.get('status', {}).get('statusCategory', {}).get('key', 'unknown'),
            'assignee': fields.get('assignee', {}).get('displayName', 'Não atribuído') if fields.get('assignee') else 'Não atribuído',
            'priority': fields.get('priority', {}).get('name', 'N/A'),
            'subtasks': []
        }
        
        issue_map[key] = item
        
        if not is_subtask:
            parents.append(item)
        else:
            # Tenta encontrar o pai no JSON
            parent_info = fields.get('parent')
            if parent_info:
                parent_key = parent_info.get('key')
                item['parent_key'] = parent_key
                subtasks_orphan.append(item)
            else:
                parents.append(item) # Tratar como item raiz se não tiver pai definido

    # Aninhamento das subtarefas
    final_tree = []
    for item in parents:
        final_tree.append(item)
        
    for sub in subtasks_orphan:
        parent_key = sub.get('parent_key')
        if parent_key in issue_map:
            issue_map[parent_key]['subtasks'].append(sub)
        else:
            # Se o pai não existir na lista, vira item raiz
            final_tree.append(sub)

    # Categorias
    categories = {
        'new': {'file': 'tarefas_pendentes.md', 'title': '📋 Tarefas Pendentes (A Fazer)', 'items': []},
        'indeterminate': {'file': 'tarefas_em_andamento.md', 'title': '🚧 Tarefas em Andamento', 'items': []},
        'done': {'file': 'tarefas_concluidas.md', 'title': '✅ Tarefas Concluídas', 'items': []}
    }

    for item in final_tree:
        cat_key = item.get('category')
        if cat_key in categories:
            categories[cat_key]['items'].append(item)
        else:
            # Fallback para Pendentes se categoria for desconhecida
            categories['new']['items'].append(item)

    # Geração dos arquivos Markdown
    for cat_key, config in categories.items():
        file_path = os.path.join(output_dir, config['file'])
        
        md_content = f"# {config['title']}\n\n"
        md_content += "| Chave | Tipo | Título / Subtarefas | Status | Responsável | Prioridade |\n"
        md_content += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        
        for item in config['items']:
            # Linha da tarefa principal
            md_content += f"| **{item['key']}** | {item['type']} | **{item['summary']}** | {item['status']} | {item['assignee']} | {item['priority']} |\n"
            
            # Linhas das subtarefas
            for sub in item['subtasks']:
                md_content += f"| ↳ {sub['key']} | _Subtarefa_ | &nbsp;&nbsp;&nbsp; {sub['summary']} | {sub['status']} | {sub['assignee']} | {sub['priority']} |\n"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"Gerado: {file_path}")

if __name__ == "__main__":
    process_hierarchy()
