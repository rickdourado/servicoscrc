import os
import re

def update_tobe_titles():
    dir_wireframes = r"c:\Users\Patrick Ribeiro\Documents\dev\servicoscrc\frontend\wireframes"

    mapping = {
        "tobe_alvara_ocupacao.html": "wireframe_alvara_ocupacao.html",
        "tobe_atividades_economicas.html": "wireframe_atividades_economicas.html",
        "tobe_desabamento.html": "wireframe_desabamento.html",
        "tobe_estrutura_imovel.html": "wireframe_estrutura_imovel.html",
        "tobe_fiscalizacao_obras.html": "wireframe_fiscalizacao_obras.html",
        "tobe_irregular_veiculo.html": "irregular_veiculo.html",
        "tobe_meio_ambiente.html": "wireframe_meio_ambiente.html",
        "tobe_sossego.html": "wireframe_sossego.html",
        "tobe_wizard_base.html": "wireframe_veiculo_abandonado.html"
    }

    # Regex para capturar o valor do input tipo-subtipo
    # Ex: <input type="text" id="tipo-subtipo" value="Alvará >> Fiscalização..." />
    # Ou: value="Alvará >> Fiscalização..."
    input_value_regex = re.compile(r'id=["\']tipo-subtipo["\'][^>]*value=["\'](.*?)["\']', re.IGNORECASE | re.DOTALL)
    # Alternativa se o ID vier depois do value
    input_value_regex_alt = re.compile(r'value=["\'](.*?)["\'][^>]*id=["\']tipo-subtipo["\']', re.IGNORECASE | re.DOTALL)

    for tobe_file, source_file in mapping.items():
        path_tobe = os.path.join(dir_wireframes, tobe_file)
        path_source = os.path.join(dir_wireframes, source_file)

        if not os.path.exists(path_tobe) or not os.path.exists(path_source):
            print(f"Erro: Arquivo(s) não encontrado(s) para {tobe_file}. Pulando...")
            continue

        print(f"Processando {tobe_file}...")

        # 1. Extrair nome do serviço do arquivo AS-IS
        with open(path_source, 'r', encoding='utf-8') as f:
            source_content = f.read()

        match = input_value_regex.search(source_content)
        if not match:
            match = input_value_regex_alt.search(source_content)
        
        if not match:
            print(f" - [AVISO] Campo 'tipo-subtipo' não encontrado em {source_file}. Tentando buscar no <option selected>.")
            # Fallback: buscar em <option selected> dentro de select tipo-lista
            option_regex = re.compile(r'<option[^>]*selected[^>]*>(.*?)</option>', re.IGNORECASE)
            opt_match = option_regex.search(source_content)
            if opt_match:
                full_val = opt_match.group(1).replace('&gt;', '>').replace('&lt;', '<')
            else:
                print(f" - [ERRO] Não foi possível encontrar o nome do serviço em {source_file}.")
                continue
        else:
            full_val = match.group(1)

        # 2. Extrair parte após >>
        if ">>" in full_val:
            service_name = full_val.split(">>")[-1].strip()
        elif ">&gt;" in full_val:
            service_name = full_val.split(">&gt;")[-1].strip()
        elif "&gt;&gt;" in full_val:
            service_name = full_val.split("&gt;&gt;")[-1].strip()
        else:
            service_name = full_val.strip()
        
        # Limpar possíveis caracteres residuais (como pontos suspensivos ou espaços extras)
        service_name = service_name.rstrip('.').strip()

        print(f" - Nome do serviço extraído: '{service_name}'")

        # 3. Atualizar o arquivo TO BE
        with open(path_tobe, 'r', encoding='utf-8') as f:
            tobe_content = f.read()

        # Atualizar <title>
        # Ex: <title>Novo Chamado — TO BE Alvará de Ocupação Irregular</title>
        tobe_content = re.sub(r'<title>(.*?)</title>', f'<title>Novo Chamado — {service_name}</title>', tobe_content, count=1)

        # Atualizar <div class="service-title">
        # Ex: <div class="service-title">Alvará de Ocupação Irregular</div>
        tobe_content = re.sub(r'<div class="service-title">(.*?)</div>', f'<div class="service-title">{service_name}</div>', tobe_content, count=1, flags=re.IGNORECASE)

        with open(path_tobe, 'w', encoding='utf-8') as f:
            f.write(tobe_content)
        
        print(f" - Arquivo {tobe_file} atualizado.")

    print("\nTodos os títulos foram atualizados com sucesso.")

if __name__ == "__main__":
    update_tobe_titles()
