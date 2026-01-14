# Proyecto: Clasificación de Potabilidad del Agua

Este proyecto de Machine Learning utiliza un conjunto de datos de calidad del agua para predecir si el agua es potable o no para el consumo humano.

## 🚀 Logros del Proyecto

1.  **Análisis Exploratorio de Datos (EDA)**:
    *   Se identificó que las características tienen distribuciones normales pero con presencia de valores atípicos (outliers).
    *   Se detectaron bajas correlaciones lineales, lo que justificó el uso de modelos de árboles de decisión no lineales.
2.  **Preprocesamiento Inteligente**:
    *   **Imputación**: Se utilizó la mediana agrupada por la clase `Potabilidad` para rellenar valores nulos en `pH`, `Sulfate` y `Trihalomethanes`, evitando sesgos.
    *   **Escalado**: Se aplicó `StandardScaler` para equilibrar el peso de todas las variables.
3.  **Modelado y Optimización**:
    *   Se compararon `Random Forest`, `XGBoost` y `SVM`.
    *   `Random Forest` demostró ser el más robusto, alcanzando un rendimiento superior tras una optimización con `GridSearchCV`.

## 📊 Conclusiones y Selección de Modelos

El proyecto concluye con un análisis de tres enfoques de alto nivel, cada uno aportando un valor distinto:

### 1. El Ganador en Rendimiento: Random Forest Optimizado
*   **Accuracy**: **80.18%**.
*   **Contexto**: Se coronó como el modelo más preciso por un margen mínimo. Su capacidad de promediar múltiples árboles (Bagging) demostró ser la técnica más estable para este ruido químico persistente en los datos del agua.

### 2. El Contendiente de Alta Precisión: XGBoost
*   **Accuracy**: **79.88%**.
*   **Hito**: Casi igualó al Random Forest usando árboles mucho más simples (`max_depth=3`). 
*   **Dato Clave**: Logró una **Precisión de 0.83** para la clase Potable, lo que significa que cuando este modelo dice "el agua es potable", tiene una fiabilidad altísima.

### 3. El Especialista en Transparencia: Árbol Podado (CCP)
*   **Accuracy**: **78%**.
*   **Valor**: Único modelo explicable visualmente con solo 33 nodos. Ideal para presentaciones ejecutivas o auditorías donde es necesario "ver" la regla de decisión (ej. pH > 7.5).

---
*Este proyecto demuestra que no existe un "único mejor modelo", sino herramientas distintas para objetivos distintos: Precisión absoluta (RF), Robustez (XGBoost) o Explicabilidad (CCP Alpha).*
