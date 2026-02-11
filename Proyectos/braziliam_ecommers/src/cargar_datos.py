import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Cargar variables de entorno
load_dotenv()

# 2. Crear la URL de conexión para SQLAlchemy
# Formato: postgresql://usuario:password@host:port/database
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db_name}')

# 3. Ruta a tu carpeta de datos
ruta_data = 'D:\\Machine Learning\\Proyectos\\braziliam_ecommers\\data'

# 4. Bucle de carga masiva
if os.path.exists(ruta_data):
    archivos = [f for f in os.listdir(ruta_data) if f.endswith('.csv')]
    
    for archivo in archivos:
        nombre_tabla = archivo.replace('.csv', '').replace('_dataset', '')
        print(f"Subiendo {archivo} a la tabla '{nombre_tabla}'...")
        
        # Leemos el CSV
        df = pd.read_csv(os.path.join(ruta_data, archivo))
        
        # Cargamos a Postgres (crea la tabla automáticamente con los tipos de datos correctos)
        df.to_sql(nombre_tabla, con=engine, if_exists='replace', index=False)
        
    print("\n¡Todo cargado con éxito en PostgreSQL!")
else:
    print("No se encontró la carpeta 'data'.")