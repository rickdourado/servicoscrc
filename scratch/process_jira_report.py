import json
import os

def generate_report():
    raw_file = 'scratch/jira_cards_full.json'
    output_file = 'scratch/relatorio_cards_jira.md'
    
    if not os.path.exists(raw_file):
        print(f"Erro: {raw_file} não encontrado.")
        return

    with open(raw_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    issues = data.get('issues', [])
    
    report = "# Relatório de Cards - Projeto CRM (czrm.atlassian.net)\n\n"
    report += f"**Total de cards extraídos:** {len(issues)}\n\n"
    report += "| Chave | Resumo | Status | Prioridade | Responsável |\n"
    report += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    for issue in issues:
        key = issue.get('key', 'N/A')
        fields = issue.get('fields', {})
        summary = fields.get('summary', 'N/A').replace('|', '-')
        status = fields.get('status', {}).get('name', 'N/A')
        priority = fields.get('priority', {}).get('name', 'N/A')
        assignee = fields.get('assignee', {})
        assignee_name = assignee.get('displayName') if assignee else 'Não atribuído'
        
        report += f"| {key} | {summary} | {status} | {priority} | {assignee_name} |\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Relatório gerado em: {output_file}")

if __name__ == "__main__":
    generate_report()
