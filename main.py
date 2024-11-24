import requests
import openpyxl

# Configuração global
NUM_JOGOS = 10 

# Client ID e Client Secret
CLIENT_ID = "urvgaeli6cz3qb7r2fodjd35kqxo9y"
CLIENT_SECRET = "ngg0n3oxfxhvgb6ko8kg5eltqs8fge"

# Enums para Platform Category
PLATFORM_CATEGORY_ENUM = {
    1: "console",
    2: "arcade",
    3: "platform",
    4: "operating_system",
    5: "portable_console",
    6: "computer"
}

# Função para mapear platform category
def map_platform_category(category_value):
    return PLATFORM_CATEGORY_ENUM.get(category_value, "Unknown")

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
def fetch_data(endpoint, access_token, client_id, query):
    url = f'https://api.igdb.com/v4/{endpoint}'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post(url, headers=headers, data=query)
    response.raise_for_status()
    return response.json()

# Função para buscar genres
def get_genres_info(genre_ids, access_token):
    if not genre_ids:
        return "None"
    
    ids_query = ", ".join(map(str, genre_ids))
    query = f"fields name; where id = ({ids_query});"
    genres_data = fetch_data("genres", access_token, CLIENT_ID, query)

    genre_names = [genre.get("name") for genre in genres_data]
    return ", ".join(genre_names) if genre_names else "None"

# Função para buscar game_modes
def get_game_modes_info(game_mode_ids, access_token):
    if not game_mode_ids:
        return "None"
    
    ids_query = ", ".join(map(str, game_mode_ids))
    query = f"fields name; where id = ({ids_query});"
    game_modes_data = fetch_data("game_modes", access_token, CLIENT_ID, query)

    game_mode_names = [mode.get("name") for mode in game_modes_data]
    return ", ".join(game_mode_names) if game_mode_names else "None"

# Função para buscar platforms
def get_platforms_info(platform_ids, access_token):
    if not platform_ids:
        return "None"
    
    ids_query = ", ".join(map(str, platform_ids))
    query = f"fields category; where id = ({ids_query});"
    platforms_data = fetch_data("platforms", access_token, CLIENT_ID, query)

    platform_categories = [map_platform_category(platform.get("category")) for platform in platforms_data]
    return ", ".join(platform_categories) if platform_categories else "None"

# Função para buscar player perspectives
def get_player_perspectives_info(perspective_ids, access_token):
    if not perspective_ids:
        return "None"
    
    ids_query = ", ".join(map(str, perspective_ids))
    query = f"fields name; where id = ({ids_query});"
    perspectives_data = fetch_data("player_perspectives", access_token, CLIENT_ID, query)

    perspective_names = [perspective.get("name") for perspective in perspectives_data]
    return ", ".join(perspective_names) if perspective_names else "None"

# Função para buscar themes
def get_themes_info(theme_ids, access_token):
    if not theme_ids:
        return "None"
    
    ids_query = ", ".join(map(str, theme_ids))
    query = f"fields name; where id = ({ids_query});"
    themes_data = fetch_data("themes", access_token, CLIENT_ID, query)

    theme_names = [theme.get("name") for theme in themes_data]
    return ", ".join(theme_names) if theme_names else "None"

# Função para buscar release dates
def get_release_date(release_date_ids, access_token):
    if not release_date_ids:
        return "None"
    
    ids_query = ", ".join(map(str, release_date_ids))
    query = f"fields human; where id = ({ids_query});"
    release_dates_data = fetch_data("release_dates", access_token, CLIENT_ID, query)

    if release_dates_data:
        return release_dates_data[0].get("human", "None")  # Retorna o campo "human" do primeiro lançamento
    return "None"

# Função para processar e salvar dados no Excel
def save_to_excel(workbook, data, sheet_name, headers):
    sheet = workbook.active
    if sheet.title == "Sheet":
        sheet.title = sheet_name.capitalize()

    if sheet.max_row == 1:
        sheet.append(headers)

    for row in data:
        sanitized_row = [str(cell) if not isinstance(cell, (int, float, str, type(None))) else cell for cell in row]
        sheet.append(sanitized_row)

# Função principal
def main():
    # Autentica e obtém o token de acesso
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    # Configuração dos campos
    games_fields = "id,name,total_rating,total_rating_count,category,genres,game_modes,platforms,player_perspectives,themes,release_dates"

    # Definir a quantidade de jogos com base na variável global
    total_games = NUM_JOGOS
    limit = 100
    offset = 0

    # Criar workbook para salvar resultados
    workbook = openpyxl.Workbook()

    # Cabeçalhos para o Excel
    headers = [
        "id", "name", "total_rating", "total_rating_count", "category", "genres", "game_modes", "platforms", "player_perspectives", "themes", "release_date"
    ]

    all_rows = []

    # Paginação para coletar todos os jogos
    while total_games > 0:
        batch_size = min(total_games, limit)
        print(f"Buscando {batch_size} jogos...")
        games_data = fetch_data("games", access_token, CLIENT_ID, f"fields {games_fields}; limit {batch_size}; offset {offset};")

        # Processar cada jogo para buscar informações adicionais
        for game in games_data:
            genres = get_genres_info(game.get("genres", []), access_token)
            game_modes = get_game_modes_info(game.get("game_modes", []), access_token)
            platforms = get_platforms_info(game.get("platforms", []), access_token)
            player_perspectives = get_player_perspectives_info(game.get("player_perspectives", []), access_token)
            themes = get_themes_info(game.get("themes", []), access_token)
            release_date = get_release_date(game.get("release_dates", []), access_token)

            row = [
                game.get("id"),
                game.get("name"),
                game.get("total_rating"),
                game.get("total_rating_count"),
                map_platform_category(game.get("category")),
                genres,
                game_modes,
                platforms,
                player_perspectives,
                themes,
                release_date
            ]
            all_rows.append(row)

        save_to_excel(workbook, all_rows, "games", headers)
        all_rows.clear()

        offset += batch_size
        total_games -= batch_size

    filename = "games_data.xlsx"
    workbook.save(filename)
    print(f"Dados salvos em {filename}")

if __name__ == '__main__':
    main()
