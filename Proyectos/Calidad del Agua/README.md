# 💧 Predicción de Potabilidad del Agua con Machine Learning

Este proyecto utiliza técnicas avanzadas de Ciencia de Datos y Machine Learning para clasificar la potabilidad del agua basándose en métricas fisicoquímicas. El objetivo principal es encontrar el equilibrio óptimo entre la precisión predictiva y la interpretabilidad del modelo.

## 📊 Resumen de Resultados

Tras un proceso exhaustivo de exploración, preprocesamiento y optimización, se evaluaron tres enfoques principales:

| Modelo | Accuracy | Fortalezas |
| :--- | :--- | :--- |
| **Random Forest (Optimizado)** | **80.18%** | Máxima precisión y estabilidad (Bagging). |
| **XGBoost (Optimizado)** | **79.88%** | Alta precisión de clase Potable (0.83). Muy eficiente. |
| **Árbol de Decisión (Poda CCP)** | **78.00%** | Máxima transparencia (solo 33 nodos). |

## 🚀 Logros Clave

1.  **Análisis Exploratorio (EDA)**: Identificación de distribuciones normales y manejo de outliers.
2.  **Imputación Inteligente**: Relleno de nulos (pH, Sulfatos) mediante la mediana segmentada por clase para evitar sesgos.
3.  **Optimización de Hiperparámetros**: Uso de `GridSearchCV` para tunear Random Forest y XGBoost.
4.  **Regularización Avanzada**: Implementación de **Cost Complexity Pruning (CCP)** para reducir el sobreajuste y simplificar la estructura del modelo.

## 🛠️ Tecnologías Utilizadas

- **Python** (Pandas, NumPy, Scikit-learn)
- **XGBoost**
- **Matplotlib & Seaborn** para visualización avanzada.
- **Jupyter Notebook**

## � Contenido del Repositorio

- `water_potability.ipynb`: Notebook principal con el flujo completo de trabajo.
- `walkthrough.md`: Documento detallado con los hallazgos técnicos.

> [!NOTE]
> **Fuente de Datos**: El conjunto de datos original puede descargarse desde [Kaggle](https://www.kaggle.com/code/imakash3011/water-quality-prediction-7-model/input). Se recomienda descargarlo para ejecutar el notebook localmente.

## ⚙️ Cómo ejecutar

1. Clona este repositorio.
2. Descarga el archivo `water_potability.csv` desde la fuente citada arriba y colócalo en la carpeta raíz.
3. Instala las dependencias: `pip install pandas scikit-learn xgboost matplotlib seaborn`.
4. Abre y ejecuta `water_potability.ipynb` en Jupyter o VS Code.

---
*Este proyecto demuestra un entendimiento profundo del balance entre sesgo y varianza, priorizando modelos robustos y generalizables.*
