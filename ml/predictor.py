# ml/predictor.py

import os
import joblib

# 1) Determina la ruta absoluta al directorio de este archivo
BASE_DIR = os.path.dirname(__file__)

# 2) Construye la ruta al .pkl del modelo entrenado
MODEL_PATH = os.path.join(BASE_DIR, "modelo_gb_regresion.pkl")

# 3) Carga el modelo en memoria (scikit-learn pipeline / GradientBoostingRegressor)
try:
    modelo = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"No se encontró el modelo en la ruta: {MODEL_PATH}")
