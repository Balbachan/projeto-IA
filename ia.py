import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Carregar o Excel gerado
def load_data(filepath):
    data = pd.read_excel(filepath)
    return data

# Função para extrair o ano da data
def extract_year(date):
    if pd.isnull(date):
        return None
    try:
        # Extrair ano do formato "YYYY" ou "MMM YYYY"
        return int(date.split()[-1]) if len(date.split()[-1]) == 4 else None
    except:
        return None

# Função para dividir valores separados por vírgulas
def split_values(value):
    if pd.isnull(value):
        return []
    return [v.strip() for v in value.split(",")]

# Pré-processar os dados
def preprocess_data(data):
    # Remover campos irrelevantes
    data = data.drop(columns=["id", "name", "category"])
    
    # Extrair ano de release_date
    data["release_year"] = data["release_date"].apply(extract_year)
    data = data.drop(columns=["release_date"])
    
    # Transformar campos categóricos em listas
    categorical_cols = ["genres", "game_modes", "platforms", "player_perspectives", "themes"]
    for col in categorical_cols:
        data[col] = data[col].apply(split_values)
    
    # Codificar campos categóricos com MultiLabelBinarizer
    mlb = MultiLabelBinarizer()
    encoded_data = pd.DataFrame(
        mlb.fit_transform(data[categorical_cols].values.flatten()),  # Corrigido para lidar com listas de listas
        columns=mlb.classes_
    )
    data = pd.concat([data.drop(columns=categorical_cols), encoded_data], axis=1)
    
    # Remover linhas com valores ausentes
    data = data.dropna()
    
    return data, mlb.classes_

# Analisar popularidade por gênero, modo, plataforma, perspectiva e tema
def analyze_popularity(data, categorical_classes):
    print("\nAnálise de Popularidade por Categoria:")
    for col in categorical_classes:
        if col in data.columns:
            mean_popularity = data[[col, "popularity"]].groupby(col)["popularity"].mean()
            print(f"\n{col}:\n{mean_popularity.sort_values(ascending=False)}")

# Realizar regressão linear múltipla
def perform_regression(data):
    # Separar variáveis independentes e dependentes
    X = data.drop(columns=["popularity"])
    y = data["popularity"]
    
    # Dividir os dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Treinar o modelo de regressão linear
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Fazer previsões no conjunto de teste
    y_pred = model.predict(X_test)
    
    # Avaliar o modelo
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print("\nResultados da Regressão Linear Múltipla:")
    print(f"MSE: {mse}")
    print(f"R²: {r2}")
    
    # Exibir os coeficientes do modelo
    coef_df = pd.DataFrame({
        "Feature": X.columns,
        "Coefficient": model.coef_
    }).sort_values(by="Coefficient", ascending=False)
    print("\nCoeficientes do Modelo:")
    print(coef_df)
    
    return model

# Função principal
def main():
    # Caminho do arquivo Excel gerado
    filepath = "games_data.xlsx"  # Atualize com o caminho correto
    
    # Carregar e processar os dados
    data = load_data(filepath)
    data, categorical_classes = preprocess_data(data)
    
    # Analisar popularidade
    analyze_popularity(data, categorical_classes)
    
    # Realizar regressão linear múltipla
    perform_regression(data)

if __name__ == "__main__":
    main()
