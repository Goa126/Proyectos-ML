# Predicción de Calidad en Proceso de Flotación Minera ⛏️🧪

Este proyecto utiliza técnicas avanzadas de Machine Learning para predecir la concentración de impurezas (% Sílice) en un proceso de flotación de mineral de hierro. El objetivo es proporcionar una herramienta de monitoreo predictivo que permita ajustar los parámetros del proceso en tiempo real para mantener la calidad del producto final.

## 📋 Resumen del Proyecto

En el procesamiento de mineral de hierro, el porcentaje de sílice en el concentrado final es un indicador crítico de calidad. Dado que las mediciones de laboratorio de sílice pueden tardar horas, este modelo ofrece una predicción inmediata basada en variables operacionales de la planta.

### Métricas Alcanzadas (XGBoost Optimizado)
- **Precisión ($R^2$):** 0.6451 (64.5% de la varianza explicada en datos nuevos).
- **Error Promedio (MAE):** ±0.54% de Sílice.
- **Robustez:** Validado mediante `TimeSeriesSplit` para asegurar el rendimiento en el tiempo.

---

## 🛠️ Metodología y Flujo de Trabajo

El proyecto se divide en etapas lógicas siguiendo las mejores prácticas:

1.  **Limpieza y Saneamiento:** Tratamiento de tipos de datos, validación de nulos y análisis de outliers por errores de sensores.
2.  **Análisis Exploratorio (EDA):** Estudio de distribuciones, correlaciones y comportamiento de la variable objetivo.
3.  **Ingeniería de Variables:**
    *   Creación de **Lags** (retrasos temporales) para capturar la inercia del proceso.
    *   **Rolling Statistics** (promedios móviles) para identificar tendencias.
    *   Eliminación de multicolinealidad.
4.  **Validación Temporal:** Uso de validación cruzada respetando la línea de tiempo de los datos para evitar el *data leakage*.
5.  **Optimización:** Ajuste fino de hiperparámetros de **XGBoost** mediante una búsqueda exhaustiva de 40 iteraciones.
6.  **Exportación:** Modelo, escalador y nombres de variables guardados para uso inmediato en producción.

---

## 📂 Estructura del Repositorio

- `notebooks/`: Contiene el análisis completo y el desarrollo del modelo (`cantidad_impurezas_presentes.ipynb`).
- `models/`: Archivos `.joblib` listos para ser cargados y realizar predicciones.
- `Data/`: Ubicación sugerida para el dataset original.

---

## 🚀 Requisitos e Instalación

Para ejecutar el notebook, se recomienda un entorno con Python 3.x y las siguientes librerías:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost joblib scipy
```

---

## ✅ Conclusiones Técnicas
El modelo final demuestra que es posible predecir con una confianza aceptable la calidad del mineral utilizando datos operacionales. La incorporación de variables temporales (Lags) fue el factor determinante para elevar el rendimiento del modelo sobre los baselines tradicionales.

---
**Autor:** Gogol Andrés 
**Fecha:** Febrero 2026
