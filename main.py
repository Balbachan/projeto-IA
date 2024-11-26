import requests
import openpyxl

# Configuração global
NUM_JOGOS = 500 

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

# Função para buscar a popularidade dos jogos
def get_popularity_info(game_ids, access_token):
    if not game_ids:
        return {}
    
    ids_query = ", ".join(map(str, game_ids))
    query = f"fields game_id, value; where game_id = ({ids_query});"
    popularity_data = fetch_data("popularity_primitives", access_token, CLIENT_ID, query)

    # Mapeia o valor de popularidade (campo `value`) para cada game_id
    popularity_map = {item["game_id"]: item.get("value", None) for item in popularity_data}
    return popularity_map

# Funções auxiliares para buscar informações adicionais
def get_genres_info(genre_ids, access_token):
    if not genre_ids:
        return "None"
    
    ids_query = ", ".join(map(str, genre_ids))
    query = f"fields name; where id = ({ids_query});"
    genres_data = fetch_data("genres", access_token, CLIENT_ID, query)

    genre_names = [genre.get("name") for genre in genres_data]
    return ", ".join(genre_names) if genre_names else "None"

def get_game_modes_info(game_mode_ids, access_token):
    if not game_mode_ids:
        return "None"
    
    ids_query = ", ".join(map(str, game_mode_ids))
    query = f"fields name; where id = ({ids_query});"
    game_modes_data = fetch_data("game_modes", access_token, CLIENT_ID, query)

    game_mode_names = [mode.get("name") for mode in game_modes_data]
    return ", ".join(game_mode_names) if game_mode_names else "None"

def get_platforms_info(platform_ids, access_token):
    if not platform_ids:
        return "None"
    
    ids_query = ", ".join(map(str, platform_ids))
    query = f"fields category; where id = ({ids_query});"
    platforms_data = fetch_data("platforms", access_token, CLIENT_ID, query)

    platform_categories = [map_platform_category(platform.get("category")) for platform in platforms_data]
    return ", ".join(platform_categories) if platform_categories else "None"

def get_player_perspectives_info(perspective_ids, access_token):
    if not perspective_ids:
        return "None"
    
    ids_query = ", ".join(map(str, perspective_ids))
    query = f"fields name; where id = ({ids_query});"
    perspectives_data = fetch_data("player_perspectives", access_token, CLIENT_ID, query)

    perspective_names = [perspective.get("name") for perspective in perspectives_data]
    return ", ".join(perspective_names) if perspective_names else "None"

def get_themes_info(theme_ids, access_token):
    if not theme_ids:
        return "None"
    
    ids_query = ", ".join(map(str, theme_ids))
    query = f"fields name; where id = ({ids_query});"
    themes_data = fetch_data("themes", access_token, CLIENT_ID, query)

    theme_names = [theme.get("name") for theme in themes_data]
    return ", ".join(theme_names) if theme_names else "None"

def get_release_date(release_date_ids, access_token):
    if not release_date_ids:
        return "None"
    
    ids_query = ", ".join(map(str, release_date_ids))
    query = f"fields human; where id = ({ids_query});"
    release_dates_data = fetch_data("release_dates", access_token, CLIENT_ID, query)

    if release_dates_data:
        return release_dates_data[0].get("human", "None")
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
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    # Configuração dos campos
    games_fields = "id,name,total_rating,total_rating_count,category,genres,game_modes,platforms,player_perspectives,themes,release_dates"

    total_games = NUM_JOGOS
    limit = 500
    offset = 6500
    selected_games = 0

    workbook = openpyxl.Workbook()

    # Cabeçalhos para o Excel
    headers = [
        "id", "name", "total_rating", "total_rating_count", "category", "genres", 
        "game_modes", "platforms", "player_perspectives", "themes", "release_date", "popularity"
    ]

    all_rows = []

    # Loop até atingir o número de jogos necessário
    while selected_games < NUM_JOGOS:
        print(f"Buscando mais jogos (offset: {offset}, selecionados: {selected_games}/{NUM_JOGOS})...")
        games_data = fetch_data("games", access_token, CLIENT_ID, f"fields {games_fields}; limit {limit}; offset {offset};")

        # Buscar IDs dos jogos
        game_ids = [game["id"] for game in games_data]
        popularity_map = get_popularity_info(game_ids, access_token)

        for game in games_data:
            popularity = popularity_map.get(game["id"], None)

            # Ignorar jogos sem popularidade
            if popularity is None:
                continue

            # Processar jogo
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
                release_date,
                popularity
            ]
            all_rows.append(row)
            selected_games += 1

            # Verificar se já atingiu o número necessário
            if selected_games >= NUM_JOGOS:
                break

        offset += limit

    save_to_excel(workbook, all_rows, "games", headers)

    filename = "games_data.xlsx"
    workbook.save(filename)
    print(f"Dados salvos em {filename}")

if __name__ == '__main__':
    main()
