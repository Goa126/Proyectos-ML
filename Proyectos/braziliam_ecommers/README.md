# 🇧🇷 Análisis Integral de E-commerce Brasileño (Olist Dataset)

Este proyecto realiza un análisis exhaustivo de datos de comercio electrónico de Olist (2016-2018), abarcando desde la ingeniería de datos y estructuración en SQL, hasta el análisis exploratorio, clustering de clientes y modelos predictivos de Machine Learning.

## 🚀 Objetivo del Proyecto
Transformar datos crudos de transacciones, logística y reseñas en insights estratégicos para mejorar la experiencia del cliente y la eficiencia operativa. El análisis busca responder preguntas clave sobre **estacionalidad de ventas**, **causas de insatisfacción** y **segmentación de clientes**.

## 📂 Estructura del Proyecto

```bash
braziliam_ecommers/
├── data/                       # Dataset original (archivos CSV de Olist)
├── notebooks/                  # Jupyter Notebooks con el análisis y modelado
│   ├── analisis_series_temporales.ipynb  # EDA, Series Temporales, Clustering y ML Predictivo
│   └── sistemas_de_recomendacion.ipynb   # Motores de recomendación (Similitud y Cross-Selling)
├── sql/                        # Scripts SQL para la base de datos
│   └── sql_braziliam.sql       # Schema, PKs, FKs y creación de Vistas Analíticas
├── src/                        # Código fuente modular
│   ├── main.py                 # API REST con FastAPI
│   └── save_models.py          # Script de persistencia de modelos
├── models/                     # Artefactos de modelos (Archivos .pkl)
├── requirements.txt            # Dependencias del proyecto
└── .env                        # Variables de entorno (credenciales de BD)
```

## 🛠️ Tecnologías Utilizadas
*   **Lenguaje:** Python 3.12+
*   **Base de Datos:** PostgreSQL
*   **Librerías Principales:** `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `sqlalchemy`, `python-dotenv`, `fastapi`, `uvicorn`, `joblib`.

## 📊 Flujo de Trabajo y Metodología

### 1. Ingeniería de Datos (SQL & PostgreSQL)
*   **Modelado de Datos:** Se estructuró la base de datos relacional definiendo Llaves Primarias (PK) y Foráneas (FK) para garantizar la integridad referencial.
*   **Vistas Analíticas:** Creación de `vista_entrenamiento_ml` y tablas enriquecidas (`ds_enriquecido_ml`) para consolidar información dispersa (pedidos, clientes, productos, pagos y reseñas) en una única fuente de verdad para los modelos.

### 2. Análisis Exploratorio y Series Temporales
*   **Conexión Directa:** Integración de SQL con Python mediante `SQLAlchemy` para consultas eficientes.
*   **Tendencias Temporales:** Detección de patrones de crecimiento orgánico en 2017 y picos estacionales (Black Friday).
*   **Comportamiento del Usuario:** Identificación de horarios "Prime Time" de compra (días laborales 10:00 - 17:00) y caída de actividad en fines de semana.

### 3. Segmentación de Clientes (Clustering)
Uso de algoritmos no supervisados (**K-Means**) para clasificar la experiencia de entrega en 3 clusters:
*   **Cluster 0 (Problema de Producto):** Entregas rápidas pero baja calificación (problemas de calidad en Muebles/Telefonía).
*   **Cluster 1 (Riesgo Logístico):** Demoras extremas (>30 días) y pésima calificación.
*   **Cluster 2 (Estándar de Oro):** Entregas eficientes y satisfacción alta.

### 4. Machine Learning: Predicción de Insatisfacción
Entrenamiento de un modelo de **Random Forest Classifier** para predecir si un cliente tendrá una experiencia negativa (Review Score < 3).
*   **Desempeño:** Recall del 54% (detecta más de la mitad de las quejas potenciales).
*   **Hallazgos Clave:**
    *   **Días de Entrega Real:** El factor más crítico.
    *   **Costo del Flete:** Sorpresivamente, un flete caro genera más insatisfacción que un producto caro.
    *   **Dimensiones:** Productos voluminosos tienen mayor tasa de incidencia.

### 5. Motores de Recomendación
Se implementaron dos motores de recomendación para atacar diferentes objetivos de negocio:
*   **Modelo 1: Similitud de Productos (Content-Based):** 
    *   Utiliza *Cosine Similarity* para encontrar sustitutos directos basados en categoría, precio y calidad (`review_score`).
    *   Objetivo: Ayudar al usuario a comparar opciones similares.
*   **Modelo 2: Venta Cruzada (Cross-Selling / Association):** 
    *   Analiza la co-ocurrencia de productos en un mismo carrito de compras, filtrando conexiones entre categorías diferentes.
    *   Objetivo: Sugerir complementos lógicos y aumentar el valor del pedido (ej. *Home Comfort* -> *Bed Bath Table*).

### 6. Despliegue de API (FastAPI)
Se desarrolló una API REST para consumir las recomendaciones en tiempo real sin necesidad de recalcular los modelos.
*   **Persistencia:** Los modelos se pre-procesan y serializan mediante `joblib` para una carga instantánea.
*   **Endpoints:**
    *   `GET /recomendar/similares/{product_id}`: Retorna top N productos similares.
    *   `GET /recomendar/cruzada/{product_id}`: Retorna productos complementarios (cross-selling).
    *   `GET /docs`: Documentación interactiva de la API con Swagger UI.

## ⚙️ Instalación y Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd braziliam_ecommers
    ```

2.  **Crear entorno virtual e instalar dependencias:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configurar Variables de Entorno:**
    Crear un archivo `.env` en la raíz con las credenciales de PostgreSQL:
    ```env
    DB_USER=tu_usuario
    DB_PASSWORD=tu_contraseña
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=nombre_base_datos
    ```

4.  **Generar Artefactos de Modelos:**
    Para que la API funcione, primero debes generar los archivos `.pkl`:
    ```bash
    python src/save_models.py
    ```

5.  **Iniciar la API:**
    ```bash
    uvicorn src.main:app --reload
    ```
    Accede a la documentación en: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 📈 Próximos Pasos
*   Implementación de **Filtrado Colaborativo Profundo** (Deep Learning) para personalización avanzada.
*   Contenerización de la API mediante **Docker**.
*   Configuración de un pipeline de CI/CD para el despliegue automático.

---
*Autor: Gogol Andrés*
