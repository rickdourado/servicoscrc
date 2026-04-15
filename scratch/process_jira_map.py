import json
import os

def generate_hierarchical_map():
    input_file = 'scratch/jira_hierarchical_data.json'
    output_file = 'documentacao/mapa_hierarquico.md'
    
    if not os.path.exists(input_file):
        print("Erro: Arquivo JSON de hierarquia não encontrado.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    issues = data.get('issues', [])
    
    issue_map = {}
    parents = []
    
    # 1. Mapeamento primário
    for issue in issues:
        key = issue.get('key')
        fields = issue.get('fields', {})
        issue_type = fields.get('issuetype', {})
        
        item = {
            'key': key,
            'summary': fields.get('summary', 'Sem título'),
            'type': issue_type.get('name', 'N/A'),
            'status': fields.get('status', {}).get('name', 'N/A'),
            'status_category': fields.get('status', {}).get('statusCategory', {}).get('key', 'new'),
            'assignee': fields.get('assignee', {}).get('displayName', 'Não atribuído') if fields.get('assignee') else 'Não atribuído',
            'priority': fields.get('priority', {}).get('name', 'N/A'),
            'subtasks': [],
            'parent_key': fields.get('parent', {}).get('key') if fields.get('parent') else None
        }
        issue_map[key] = item

    # 2. Construção da Árvore
    for key, item in issue_map.items():
        if item['parent_key'] and item['parent_key'] in issue_map:
            issue_map[item['parent_key']]['subtasks'].append(item)
        elif not item['parent_key']:
            parents.append(item)
        else:
            # Subtarefa órfã (Pai não está no JSON)
            parents.append(item)

    # 3. Geração do Markdown
    report = "# 🗺️ Mapa Hierárquico do Projeto (Entrega por Subtarefas)\n\n"
    report += "Este documento organiza as tarefas por Blocos de Entrega, mostrando como cada subtarefa contribui para o objetivo maior.\n\n"
    
    report += "| Estrutura (Pai / ↳ Subtarefa) | Status | Progresso | Responsável | Prioridade |\n"
    report += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    for p in parents:
        # Calcular progresso do bloco
        total_subs = len(p['subtasks'])
        done_subs = len([s for s in p['subtasks'] if s['status_category'] == 'done'])
        
        progress_str = "N/A"
        if total_subs > 0:
            percent = int((done_subs / total_subs) * 100)
            progress_str = f"`{done_subs}/{total_subs}` ({percent}%)"
        elif p['status_category'] == 'done':
            progress_str = "100%"
        else:
            progress_str = "0%"

        # Linha da tarefa principal
        report += f"| **{p['key']}**: {p['summary']} | **{p['status']}** | **{progress_str}** | {p['assignee']} | {p['priority']} |\n"
        
        # Linhas das subtarefas
        for s in p['subtasks']:
            icon = "✅" if s['status_category'] == 'done' else "🚧" if s['status_category'] == 'indeterminate' else "📋"
            report += f"| &nbsp;&nbsp;&nbsp; ↳ {icon} {s['key']}: {s['summary']} | _{s['status']}_ | - | {s['assignee']} | {s['priority']} |\n"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Mapa hierárquico gerado em: {output_file}")

if __name__ == "__main__":
    generate_hierarchical_map()
