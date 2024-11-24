import requests
import openpyxl

# Client ID e Client Secret
CLIENT_ID = "urvgaeli6cz3qb7r2fodjd35kqxo9y"
CLIENT_SECRET = "ngg0n3oxfxhvgb6ko8kg5eltqs8fge"

# Função para autenticar e obter o token de acesso da API
def get_access_token(client_id, client_secret):
    auth_url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(auth_url, params=params)
    response.raise_for_status()
    return response.json()['access_token']

# Função para buscar dados de um endpoint
def fetch_data(endpoint, access_token, client_id, fields, limit=500, offset=0):
    url = f'https://api.igdb.com/v4/{endpoint}'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    query = f'fields {fields}; limit {limit}; offset {offset};'
    response = requests.post(url, headers=headers, data=query)
    response.raise_for_status()
    return response.json()

# Função para mapear o valor do enum de 'gender'
def map_gender(gender_value):
    gender_map = {
        0: "Male",
        1: "Female",
        2: "Other"
    }
    return gender_map.get(gender_value, "Unknown")  # Default to "Unknown" if not found

# Função para mapear o valor do enum de 'species'
def map_species(species_value):
    species_map = {
        1: "Human",
        2: "Alien",
        3: "Animal",
        4: "Android",
        5: "Unknown"
        # Adicione outros mapeamentos conforme necessário
    }
    return species_map.get(species_value, "Unknown")  # Default to "Unknown" if not found

# Função para processar e salvar dados no Excel
def save_endpoint_to_excel(data, endpoint):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = endpoint.capitalize()

    if not data:
        print(f"Nenhum dado encontrado para o endpoint {endpoint}.")
        return

    # Criar cabeçalho com todos os campos disponíveis
    headers = set()
    for item in data:
        headers.update(item.keys())
    headers = list(headers)  # Converte para lista para manter a ordem

    # Adiciona o cabeçalho ao Excel
    sheet.append(headers)

    # Adicionar os dados
    for item in data:
        row = []
        for header in headers:
            value = item.get(header)
            # Lidar com arrays de IDs como o campo 'games'
            if isinstance(value, list):
                if header == "games":  # Caso específico para 'games' ser um array de IDs
                    row.append(", ".join(map(str, value)))  # Converte os IDs para uma string
                else:
                    row.append(", ".join(map(str, value)))  # Para outros arrays
            elif isinstance(value, dict):
                row.append(", ".join(f"{k}: {v}" for k, v in value.items()))  # Combina dicionários em uma string
            elif header == "gender" and isinstance(value, int):
                # Se for o campo 'gender' e for um número, mapeia para o valor legível
                row.append(map_gender(value))
            elif header == "species" and isinstance(value, int):
                # Se for o campo 'species' e for um número, mapeia para o valor legível
                row.append(map_species(value))
            else:
                row.append(value)  # Valor simples
        sheet.append(row)

    # Salvar o arquivo
    filename = f"{endpoint}_data.xlsx"
    workbook.save(filename)
    print(f"Dados do endpoint {endpoint} salvos em {filename}")

# Função principal
def main():
    # Autentica e obtém o token de acesso
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    # Configuração dos endpoints e seus campos
    endpoints = {
        # "age_ratings": "category,checksum,content_descriptions,rating,rating_cover_url,synopsis",
        "characters": "name,gender,species,games",
        # "games": "name,rating,release_dates,platforms,genres"
        # Adicione outros endpoints aqui
    }

    # Processar cada endpoint
    for endpoint, fields in endpoints.items():
        print(f"Buscando dados do endpoint: {endpoint}...")
        all_data = []
        offset = 0

        # Paginação para coletar todos os dados
        while True:
            data_chunk = fetch_data(endpoint, access_token, CLIENT_ID, fields, limit=500, offset=offset)
            if not data_chunk:
                break
            all_data.extend(data_chunk)
            offset += 500

        # Salvar dados no Excel
        save_endpoint_to_excel(all_data, endpoint)

if __name__ == '__main__':
    main()
