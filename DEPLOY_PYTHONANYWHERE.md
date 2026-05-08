# Deploy PythonAnywhere - Instruções

## Problema: CSV não carrega

### Causa
Path relativo falha se working dir differs ou app está em subpasta.

### Solução: Configurar WSGI corretamente

**Use o template:** [`wsgi_pythonanywhere_template.py`](./wsgi_pythonanywhere_template.py)

1. Copie conteúdo do template
2. Edite WSGI config no PythonAnywhere (`Web → WSGI configuration file`)
3. Substitua `USERNAME` pelo seu username
4. Salve e reload app

### Solução 2: Verificar Estrutura

Garanta que estrutura no servidor seja:

```
/home/username/servicoscrc/
  backend/
    data/
      prefrio_servicos.csv  <-- DEVE EXISTIR
      app.db
    scripts/
      app.py
      prefrio_stats.py
  frontend/
    index.html
    ...
```

### Debug no Servidor

**Método 1: Script diagnóstico**

No console PythonAnywhere (Bash):

```bash
cd ~/servicoscrc
python backend/scripts/check_paths.py
```

Script mostra:
- Paths calculados vs esperados
- Arquivos críticos existem ou não
- Env vars configuradas
- Teste de importação e carregamento CSV

**Método 2: Logs do servidor**

Acesse logs de erro (`Files → /var/log/username.pythonanywhere.com.error.log`):
- Busque linhas `[DEBUG] prefrio_stats.py`
- Verifique paths impressos
- Confira se CSV existe no caminho mostrado

### Checklist

- [ ] CSV `prefrio_servicos.csv` foi uploaded para `backend/data/`
- [ ] WSGI file define `os.environ['BASE_DIR']` corretamente
- [ ] Working directory no WSGI aponta para raiz do projeto
- [ ] Logs mostram paths corretos
- [ ] Endpoint `/api/prefrio-stats/summary` retorna dados (não erro 500)

### Test Endpoint

```bash
curl https://username.pythonanywhere.com/api/prefrio-stats/summary
```

Deve retornar JSON com `total_registros`, `total_orgaos`, `total_servicos`.
