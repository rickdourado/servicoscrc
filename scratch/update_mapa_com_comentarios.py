import json
import os
from datetime import datetime

def format_date(date_str):
    if not date_str: return ""
    try:
        dt = datetime.strptime(date_str.split('.')[0], "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%d/%m/%Y %H:%M")
    except: return date_str

def parse_adf(content):
    if not content: return ""
    if isinstance(content, str): return content
    text = ""
    if isinstance(content, dict):
        if 'text' in content: text += content['text']
        if 'content' in content:
            for item in content['content']: text += parse_adf(item)
    return text

def get_status_icon(issue):
    status_cat = issue['fields'].get('status', {}).get('statusCategory', {}).get('key', '').lower()
    if status_cat == 'done': return '✅'
    if status_cat == 'indeterminate': return '🚧'
    return '📋'

def generate_map_v2():
    input_file = '/home/ssdlinux/Documents/dev/servicoscrc/scratch/jira_deep_data.json'
    output_file = '/home/ssdlinux/Documents/dev/servicoscrc/documentacao/mapa_hierarquico_v2_com_comentarios.md'
    
    if not os.path.exists(input_file):
        print(f"Erro: {input_file} não encontrado.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    issues = data.get('issues', [])
    issue_map = {issue['key']: issue for issue in issues}
    
    # Separar pais
    parents = []
    for issue in issues:
        if not issue['fields'].get('parent'):
            parents.append(issue)
    
    # Ordenar pais (mesma ordem do original se possível, ou por chave)
    # Vou ordenar por chave para consistência
    parents.sort(key=lambda x: int(x['key'].split('-')[1]) if '-' in x['key'] else 0)

    md = "# 🗺️ Mapa Hierárquico do Projeto V2 (Com Comentários)\n\n"
    md += "Este documento organiza as tarefas por Blocos de Entrega, incluindo os comentários extraídos do Jira.\n\n"
    md += "| Estrutura (Pai / ↳ Subtarefa) | Status | Progresso | Responsável | Prioridade | Comentários |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

    for p in parents:
        # Pai
        key = p['key']
        summary = p['fields'].get('summary', '')
        status = p['fields'].get('status', {}).get('name', 'N/A')
        assignee = p['fields'].get('assignee', {}).get('displayName', 'Não atribuído') if p['fields'].get('assignee') else 'Não atribuído'
        priority = p['fields'].get('priority', {}).get('name', 'N/A')
        
        # Calcular progresso
        subtasks_refs = p['fields'].get('subtasks', [])
        total = len(subtasks_refs)
        done = 0
        for s_ref in subtasks_refs:
            s_data = issue_map.get(s_ref['key'])
            if s_data and s_data['fields'].get('status', {}).get('statusCategory', {}).get('key') == 'done':
                done += 1
        
        if total > 0:
            progress = f"**`{done}/{total}`** ({int(done/total*100)}%)"
        else:
            is_done = p['fields'].get('status', {}).get('statusCategory', {}).get('key') == 'done'
            progress = "**100%**" if is_done else "**0%**"

        # Comentários do pai
        p_comments = []
        for c in p['fields'].get('comment', {}).get('comments', []):
            author = c.get('author', {}).get('displayName', '?')
            body = parse_adf(c.get('body')).strip().replace('|', '\\|').replace('\n', ' ')
            p_comments.append(f"**{author}**: {body[:100]}...") # Truncar para caber na tabela
        
        comments_str = "<br>".join(p_comments) if p_comments else "-"

        md += f"| **{key}**: {summary} | **{status}** | {progress} | {assignee} | {priority} | {comments_str} |\n"

        # Subtarefas
        for s_ref in subtasks_refs:
            s = issue_map.get(s_ref['key'])
            if not s: continue
            
            s_key = s['key']
            s_summary = s['fields'].get('summary', '')
            s_status = s['fields'].get('status', {}).get('name', 'N/A')
            s_assignee = s['fields'].get('assignee', {}).get('displayName', 'Não atribuído') if s['fields'].get('assignee') else 'Não atribuído'
            s_priority = s['fields'].get('priority', {}).get('name', 'N/A')
            s_icon = get_status_icon(s)
            
            # Comentários da subtarefa
            s_comments = []
            for c in s['fields'].get('comment', {}).get('comments', []):
                author = c.get('author', {}).get('displayName', '?')
                body = parse_adf(c.get('body')).strip().replace('|', '\\|').replace('\n', ' ')
                s_comments.append(f"**{author}**: {body[:100]}...")
            
            s_comments_str = "<br>".join(s_comments) if s_comments else "-"

            md += f"| &nbsp;&nbsp;&nbsp; ↳ {s_icon} {s_key}: {s_summary} | _{s_status}_ | - | {s_assignee} | {s_priority} | {s_comments_str} |\n"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"Mapa V2 gerado em: {output_file}")

if __name__ == "__main__":
    generate_map_v2()
