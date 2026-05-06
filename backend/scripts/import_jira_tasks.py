import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime

# Adiciona o diretório backend/scripts ao path para importar models
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "backend" / "scripts"))

from app import app, db
from models import User, Activity

def import_jira_tasks(file_path):
    print(f"Iniciando importação de {file_path}...")
    
    # Carrega a planilha pulando o cabeçalho decorativo
    df = pd.read_excel(file_path, skiprows=2)
    
    # Renomeia as colunas para facilitar o acesso
    # Colunas originais baseadas na análise: Chave, Título / Subtarefa, Status, Progresso, Responsável, Prioridade
    df.columns = ['key', 'title', 'status', 'progress', 'assignee', 'priority']
    
    with app.app_context():
        # Limpa atividades existentes para uma nova carga limpa (opcional, mas solicitado pelo contexto de "transferir")
        print("Limpando atividades existentes...")
        Activity.query.delete()
        db.session.commit()
        
        # Mapeamento de usuários (Nome -> ID e Username -> ID)
        users_by_name = {u.name: u.id for u in User.query.all()}
        users_by_username = {u.username: u.id for u in User.query.all()}
        print(f"Usuários encontrados: {len(users_by_name)}")
        
        last_parent_id = None
        count = 0
        
        for _, row in df.iterrows():
            title_raw = str(row['title']).strip()
            if not title_raw or title_raw == 'nan':
                continue
                
            # Detecta se é subtarefa (começa com ↳)
            is_subtask = title_raw.startswith('↳')
            title = title_raw.replace('↳', '').strip()
            
            # Mapeamento de Status
            status_map = {
                'Pendente': 'todo',
                'Em Progresso': 'in_progress',
                'Concluído': 'done',
                'Finalizado': 'done',
                'Bloqueado': 'blocked'
            }
            status = status_map.get(row['status'], 'todo')
            
            # Mapeamento de Prioridade
            priority_map = {
                'High': 'high',
                'Medium': 'medium',
                'Low': 'low',
                'Highest': 'high',
                'Lowest': 'low'
            }
            priority = priority_map.get(row['priority'], 'medium').lower()
            
            # Busca owner_id pelo nome ou username
            assignee_name = str(row['assignee']).strip()
            owner_id = users_by_name.get(assignee_name) or users_by_username.get(assignee_name)
            
            # Fallback para admin se não encontrar o usuário
            if not owner_id:
                admin = User.query.filter_by(username='admin').first()
                owner_id = admin.id if admin else 1
                print(f"Aviso: Usuário '{assignee_name}' não encontrado. Atribuindo ao Admin.")

            # Cria a atividade
            activity = Activity(
                title=title,
                description=f"Chave Jira: {row['key']}",
                status=status,
                priority=priority,
                owner_id=owner_id,
                parent_id=last_parent_id if is_subtask else None
            )
            
            db.session.add(activity)
            db.session.flush() # Para pegar o ID se for parent
            
            if not is_subtask:
                last_parent_id = activity.id
                
            count += 1
            
        db.session.commit()
        print(f"Sucesso! {count} tarefas/atividades importadas.")

if __name__ == "__main__":
    jira_file = BASE_DIR / "refs" / "CRM_Backup_Jira.xlsx"
    if jira_file.exists():
        import_jira_tasks(str(jira_file))
    else:
        print(f"Erro: Arquivo {jira_file} não encontrado.")
