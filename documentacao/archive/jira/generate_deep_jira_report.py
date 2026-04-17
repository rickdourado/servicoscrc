import json
import os
from datetime import datetime

def format_date(date_str):
    if not date_str:
        return "N/A"
    try:
        # 2026-03-05T12:45:08.306-0300
        dt = datetime.strptime(date_str.split('.')[0], "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return date_str

def generate_report():
    input_file = '/home/ssdlinux/Documents/dev/servicoscrc/scratch/jira_deep_data.json'
    output_file = '/home/ssdlinux/Documents/dev/servicoscrc/documentacao/relatorio_profundo_jira.md'
    
    if not os.path.exists(input_file):
        print(f"Erro: {input_file} não encontrado.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    issues = data.get('issues', [])
    
    # Mapear questões por chave para fácil acesso e hierarquia
    issue_map = {issue['key']: issue for issue in issues}
    
    # Separar pais de subtarefas
    parents = []
    for issue in issues:
        parent = issue['fields'].get('parent')
        if not parent:
            parents.append(issue)

    # Iniciar Markdown
    md = "# 📋 Relatório Detalhado de Cards - Projeto CRM\n\n"
    md += f"**Data do Relatório:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    md += f"**Total de Cards Analisados:** {len(issues)}\n\n"
    md += "---\n\n"

    for parent in parents:
        md += render_issue(parent, issue_map, level=0)
        md += "\n---\n\n"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"Relatório detalhado gerado em: {output_file}")

def render_issue(issue, issue_map, level=0):
    key = issue['key']
    fields = issue['fields']
    summary = fields.get('summary', 'Sem título')
    status = fields.get('status', {}).get('name', 'N/A')
    assignee = fields.get('assignee', {}).get('displayName', 'Não atribuído') if fields.get('assignee') else 'Não atribuído'
    priority = fields.get('priority', {}).get('name', 'N/A')
    description = fields.get('description')
    
    indent = "  " * level
    h_prefix = "#" * (level + 2)
    
    content = f"{h_prefix} [{key}] {summary}\n\n"
    content += f"- **Status:** {status}\n"
    content += f"- **Responsável:** {assignee}\n"
    content += f"- **Prioridade:** {priority}\n"
    
    if description:
        # Tratar descrição se for objeto (Atlassian Document Format) ou string
        desc_text = ""
        if isinstance(description, dict):
            # Simplificação básica do ADF
            for block in description.get('content', []):
                for item in block.get('content', []):
                    desc_text += item.get('text', '')
                desc_text += "\n"
        else:
            desc_text = str(description)
        
        if desc_text.strip():
            content += f"\n> **Descrição:** {desc_text.strip()}\n"

    # Comentários
    comments = fields.get('comment', {}).get('comments', [])
    if comments:
        content += "\n#### 💬 Comentários\n"
        for c in comments:
            author = c.get('author', {}).get('displayName', 'Desconhecido')
            date = format_date(c.get('created'))
            body = ""
            # Tratar corpo do comentário (ADF)
            if isinstance(c.get('body'), dict):
                for block in c['body'].get('content', []):
                    for item in block.get('content', []):
                        body += item.get('text', '')
                    body += " "
            else:
                body = str(c.get('body'))
            
            content += f"- **{author}** ({date}): {body.strip()}\n"
    
    # Atividades (Changelog)
    histories = issue.get('changelog', {}).get('histories', [])
    if histories:
        content += "\n#### 🕒 Atividades Recentes\n"
        # Limitar a 5 últimas atividades para não poluir
        for h in histories[-5:]:
            author = h.get('author', {}).get('displayName', 'Desconhecido')
            date = format_date(h.get('created'))
            for item in h.get('items', []):
                field = item.get('field', 'campo').capitalize()
                fr = item.get('fromString') or 'vazio'
                to = item.get('toString') or 'vazio'
                content += f"- **{date}**: {author} alterou **{field}** de `{fr}` para `{to}`\n"

    # Subtarefas
    subtasks = fields.get('subtasks', [])
    if subtasks:
        content += "\n#### ↳ Subtarefas\n"
        for sub in subtasks:
            sub_key = sub['key']
            if sub_key in issue_map:
                content += render_issue(issue_map[sub_key], issue_map, level + 1)
            else:
                content += f"  - [{sub_key}] {sub['fields'].get('summary')} (Dados não extraídos)\n"

    return content

if __name__ == "__main__":
    generate_report()
