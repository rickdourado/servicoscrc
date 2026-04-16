import requests
from requests.auth import HTTPBasicAuth
import json
import os

def test_jira_connection():
    url = "https://czrm.atlassian.net/rest/api/3/issue/CRM-80"
    email = "patrick.ribeiro@prefeitura.rio"
    api_token = "ATATT3xFfGF0g5tsRmxmL-8hnD62oFgktJs19SW_h86HLuqGVV7QLeiMMR1M99dQmB0LwCNWuzbeVbXADPQDjxOKT96DhxZmeaIq62KuqsPBVgPaw_WLw6o-gwPvJb3otKWnqOd3O9Ry4Q8v0FgjL9GSg0EE5eik-IzGiLfVkqCWQhld8IZzDIM=5CDE7DFF"
    
    auth = HTTPBasicAuth(email, api_token)
    
    headers = {
        "Accept": "application/json"
    }
    
    try:
        response = requests.request(
            "GET",
            url,
            headers=headers,
            auth=auth
        )
        
        if response.status_code == 200:
            print("Conexão com Jira bem-sucedida!")
            data = response.json()
            print(f"Resumo da tarefa CRM-80: {data['fields']['summary']}")
            # Verificar se tem comentários
            issue_id = data['id']
            comment_url = f"https://czrm.atlassian.net/rest/api/3/issue/{issue_id}/comment"
            comment_resp = requests.request("GET", comment_url, headers=headers, auth=auth)
            if comment_resp.status_code == 200:
                comments = comment_resp.json()
                print(f"Total de comentários: {comments['total']}")
        else:
            print(f"Erro na conexão: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    test_jira_connection()
