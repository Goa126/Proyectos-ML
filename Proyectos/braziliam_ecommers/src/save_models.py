import os
import pandas as pd
import joblib
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.preprocessing import MinMaxScaler
from itertools import combinations
from collections import Counter

load_dotenv()

# Conexión a BD
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
dbname = os.getenv('DB_NAME')
connection_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(connection_url)

def save_artifacts():
    print("Cargando datos desde Postgres...")
    df = pd.read_sql("SELECT * FROM v_recom_data", engine)
    
    # --- MODELO 1: Similitud ---
    df_productos = df.groupby('product_id').agg({
        'product_category_name_english': 'first',
        'price': 'mean',
        'review_score': 'mean'
    }).reset_index()
    
    df_features = pd.get_dummies(df_productos['product_category_name_english'], prefix='cat')
    scaler = MinMaxScaler()
    df_features[['price', 'review_score']] = scaler.fit_transform(df_productos[['price', 'review_score']])
    
    # --- MODELO 2: Venta Cruzada ---
    basket_data = df.groupby('order_id')['product_id'].apply(list)
    basket_data = basket_data[basket_data.apply(lambda x: len(set(x)) > 1)]
    
    pares_contador = Counter()
    for productos in basket_data:
        productos_unicos = sorted(list(set(productos)))
        for par in combinations(productos_unicos, 2):
            pares_contador[par] += 1
            
    df_conexiones = pd.DataFrame(pares_contador.items(), columns=['par', 'frecuencia'])
    df_conexiones[['prod_A', 'prod_B']] = pd.DataFrame(df_conexiones['par'].tolist(), index=df_conexiones.index)
    
    prod_a_cat = df_productos.set_index('product_id')['product_category_name_english'].to_dict()
    
    def es_cruzada(row):
        cat_A = prod_a_cat.get(row['prod_A'])
        cat_B = prod_a_cat.get(row['prod_B'])
        return cat_A != cat_B and cat_A is not None and cat_B is not None

    df_conexiones['es_venta_cruzada'] = df_conexiones.apply(es_cruzada, axis=1)
    df_venta_cruzada = df_conexiones[df_conexiones['es_venta_cruzada']].sort_values(by='frecuencia', ascending=False)

    # Guardar en la carpeta models/
    os.makedirs('models', exist_ok=True)
    joblib.dump(df_productos, 'models/df_productos.pkl')
    joblib.dump(df_features, 'models/df_features.pkl')
    joblib.dump(df_venta_cruzada, 'models/df_venta_cruzada.pkl')
    joblib.dump(prod_a_cat, 'models/prod_a_cat.pkl')
    
    print("¡Artefactos guardados con éxito en models/!")

if __name__ == "__main__":
    save_artifacts()