from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

app = FastAPI(
    title="Olist Recommendation API",
    description="API para recomendar productos similares y venta cruzada",
    version="1.0.0"
)

# Cargar artefactos al iniciar la API
try:
    df_productos = joblib.load('models/df_productos.pkl')
    df_features = joblib.load('models/df_features.pkl')
    df_venta_cruzada = joblib.load('models/df_venta_cruzada.pkl')
    prod_a_cat = joblib.load('models/prod_a_cat.pkl')
    print("Modelos cargados exitosamente.")
except Exception as e:
    print(f"Error al cargar los modelos: {e}")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Recomendaciones de Olist. Usa /docs para ver la documentación."}

@app.get("/recomendar/similares/{product_id}")
def recomendar_similares(product_id: str, n: int = 5):
    """
    Recomienda productos similares basados en categoría, precio y calidad (Modelo 1).
    """
    try:
        idx = df_productos[df_productos['product_id'] == product_id].index[0]
    except IndexError:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    product_vector = df_features.iloc[idx].values.reshape(1, -1)
    similitudes = cosine_similarity(product_vector, df_features)
    
    # Obtener los top N más similares (excluyendo el propio producto)
    indices_similares = similitudes[0].argsort()[-(n+1):-1][::-1]
    resultado = df_productos.iloc[indices_similares].to_dict(orient='records')
    
    return {
        "producto_origen": product_id,
        "recomendaciones": resultado
    }

@app.get("/recomendar/cruzada/{product_id}")
def recomendar_cruzada(product_id: str, n: int = 5):
    """
    Recomienda productos de otras categorías que otros usuarios compraron juntos (Modelo 2).
    """
    filtro = df_venta_cruzada[(df_venta_cruzada['prod_A'] == product_id) | (df_venta_cruzada['prod_B'] == product_id)]
    
    if filtro.empty:
        return {"message": "No hay suficientes datos de venta cruzada para este producto.", "recomendaciones": []}
    
    ids_recomendados = []
    for _, row in filtro.iterrows():
        rec_id = row['prod_B'] if row['prod_A'] == product_id else row['prod_A']
        ids_recomendados.append(rec_id)
    
    resultado = df_productos[df_productos['product_id'].isin(ids_recomendados)].head(n).to_dict(orient='records')
    
    return {
        "producto_origen": product_id,
        "categoria_origen": prod_a_cat.get(product_id),
        "recomendaciones": resultado
    }
