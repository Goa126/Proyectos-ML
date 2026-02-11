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
│   └── sistemas_de_recomendacion.ipynb   # (En desarrollo) Motores de recomendación
├── sql/                        # Scripts SQL para la base de datos
│   └── sql_braziliam.sql       # Schema, PKs, FKs y creación de Vistas Analíticas
├── src/                        # Código fuente modular (funciones auxiliares)
├── models/                     # Modelos entrenados serializados (pkl/joblib)
├── requirements.txt            # Dependencias del proyecto
└── .env                        # Variables de entorno (credenciales de BD)
```

## 🛠️ Tecnologías Utilizadas
*   **Lenguaje:** Python 3.12+
*   **Base de Datos:** PostgreSQL
*   **Librerías Principales:** `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `sqlalchemy`, `python-dotenv`.

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

4.  **Ejecutar Notebooks:**
    Iniciar Jupyter Lab o Notebook para explorar `notebooks/analisis_series_temporales.ipynb`.

## 📈 Próximos Pasos
*   Desarrollo de un **Sistema de Recomendación** híbrido (Collaborative Filtering + Content-Based) en `sistemas_de_recomendacion.ipynb`.
*   Despliegue del modelo predictivo como API.

---
*Autor: [Tu Nombre]*
