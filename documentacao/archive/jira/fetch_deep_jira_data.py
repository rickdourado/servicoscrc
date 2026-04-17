import requests
from requests.auth import HTTPBasicAuth
import json
import os

def fetch_deep_jira_data():
    base_url = "https://czrm.atlassian.net/rest/api/3/search/jql"
    email = "patrick.ribeiro@prefeitura.rio"
    api_token = "ATATT3xFfGF0g5tsRmxmL-8hnD62oFgktJs19SW_h86HLuqGVV7QLeiMMR1M99dQmB0LwCNWuzbeVbXADPQDjxOKT96DhxZmeaIq62KuqsPBVgPaw_WLw6o-gwPvJb3otKWnqOd3O9Ry4Q8v0FgjL9GSg0EE5eik-IzGiLfVkqCWQhld8IZzDIM=5CDE7DFF"
    output_file = "/home/ssdlinux/Documents/dev/servicoscrc/scratch/jira_deep_data.json"

    auth = HTTPBasicAuth(email, api_token)
    
    all_issues = []
    next_page_token = None
    max_results = 50
    
    print("Iniciando extração PROFUNDA e COMPLETA do Jira (v3 Token Based)...")
    
    while True:
        params = {
            'jql': 'project = CRM ORDER BY key ASC',
            'fields': 'summary,status,issuetype,parent,assignee,priority,comment,description',
            'expand': 'changelog',
            'maxResults': max_results
        }
        
        if next_page_token:
            params['nextPageToken'] = next_page_token
        
        headers = {
            "Accept": "application/json"
        }
        
        response = requests.get(base_url, auth=auth, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"Erro ao buscar dados: {response.status_code}")
            print(response.text)
            break
            
        data = response.json()
        issues = data.get('issues', [])
        all_issues.extend(issues)
        
        is_last = data.get('isLast', True)
        next_page_token = data.get('nextPageToken')
        
        print(f"Extraídos {len(all_issues)} cards... (isLast: {is_last})")
        
        if is_last or not next_page_token:
            break
            
    # Salvar dados totais
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'issues': all_issues, 'total': len(all_issues)}, f, ensure_ascii=False, indent=2)
        
    print(f"Extração concluída. Total de cards salvos: {len(all_issues)}")
    print(f"Arquivo: {output_file}")

if __name__ == "__main__":
    fetch_deep_jira_data()
