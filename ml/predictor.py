import joblib
import os
import pandas as pd

# Ruta absoluta al modelo
modelo_path = os.path.join(os.path.dirname(__file__), 'modelo_gb_regresion.pkl')
modelo = joblib.load(modelo_path)

def predecir_desempeno(datos_dict):
    """
    datos_dict: diccionario con los datos de entrada del formulario
    """
    df = pd.DataFrame([datos_dict])
    pred = modelo.predict(df)[0]
    return pred
