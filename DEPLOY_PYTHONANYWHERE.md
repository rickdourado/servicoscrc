# Deploy PythonAnywhere - Instruções Completas

## Passo 1: Clone/Pull do Repositório

```bash
cd ~
git clone https://github.com/SEU_USUARIO/servicoscrc.git
# OU se já existe:
cd ~/servicoscrc
git pull origin main
```

## Passo 2: Configure WSGI

No PythonAnywhere:
1. Vá em **Web → WSGI configuration file**
2. **DELETE todo conteúdo** do arquivo
3. **Copie e cole** o conteúdo de [`pythonanywhere_wsgi.py`](./pythonanywhere_wsgi.py)
4. Salve (Ctrl+S)

**Importante:** Arquivo já auto-detecta paths. Sem edições manuais necessárias.

## Passo 3: Configure .env

Crie `.env` na raiz do projeto:

```bash
cd ~/servicoscrc
nano .env
```

Conteúdo mínimo:

```env
GEMINI_API_KEY=sua-chave-aqui
SECRET_KEY=chave-secreta-aleatoria
ADMIN_PASSWORD=senha-admin-segura
IS_PRODUCTION=true
```

## Passo 4: Instale Dependências

```bash
pip install -r requirements.txt --user
```

## Passo 5: Reload App

No dashboard Web do PythonAnywhere:
- Clique em **Reload**

## Passo 6: Teste

```bash
curl https://SEU_USERNAME.pythonanywhere.com/api/prefrio-stats/summary
```

Deve retornar JSON com `total_registros`, `total_orgaos`, `total_servicos`.

---

## Troubleshooting

### Verificar Estrutura de Arquivos

Garanta que estrutura no servidor seja:

```
~/servicoscrc/
  backend/
    data/
      prefrio_servicos.csv  <-- DEVE EXISTIR
      app.db
    scripts/
      app.py
      prefrio_stats.py
  frontend/
    index.html
  pythonanywhere_wsgi.py
  .env
```

### Script Diagnóstico

No console PythonAnywhere (Bash):

```bash
cd ~/servicoscrc
python backend/scripts/check_paths.py
```

Output mostra:
- Paths calculados vs esperados
- Arquivos críticos existem ou não
- Env vars configuradas
- Teste de importação e carregamento CSV

### Logs de Erro

Acesse error log (`Files → /var/log/username.pythonanywhere.com.error.log`):
- Busque `[WSGI]` - mostra config inicial
- Busque `[DEBUG] prefrio_stats.py` - mostra path resolution
- Busque `FileNotFoundError` - indica arquivo missing

### Checklist Completo

- [ ] Repo clonado/pulled com sucesso
- [ ] WSGI file copiado de `pythonanywhere_wsgi.py`
- [ ] `.env` criado com todas variáveis necessárias
- [ ] Dependências instaladas (`pip install -r requirements.txt --user`)
- [ ] CSV `prefrio_servicos.csv` existe em `backend/data/`
- [ ] App reloaded no dashboard Web
- [ ] Endpoint `/api/prefrio-stats/summary` retorna JSON (não erro 500)
- [ ] Dashboard PrefRio carrega dados sem erros

### Problemas Comuns

**Erro: `ModuleNotFoundError: No module named 'flask'`**
- Solução: `pip install -r requirements.txt --user`

**Erro: `FileNotFoundError: CSV não encontrado`**
- Rode: `python backend/scripts/check_paths.py`
- Verifique se CSV existe no path mostrado
- Confirme WSGI set `BASE_DIR` corretamente (veja logs)

**Erro 500 genérico**
- Check error log (`/var/log/username.pythonanywhere.com.error.log`)
- Busque stack trace completo
- Verifique se `.env` tem todas variáveis obrigatórias
