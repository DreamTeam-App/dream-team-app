# ml/predictor.py

import os
import joblib

# 1) Determina la ruta absoluta al directorio de este archivo
BASE_DIR = os.path.dirname(__file__)

# 2) Construye las rutas a los .pkl de los modelos entrenados
LR_MODEL_PATH = os.path.join(BASE_DIR, "modelo_lineal.pkl")
RF_MODEL_PATH = os.path.join(BASE_DIR, "modelo_rf_regresion.pkl")

# 3) Carga los modelos en memoria
try:
    modelo_lineal = joblib.load(LR_MODEL_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"No se encontró el modelo lineal en la ruta: {LR_MODEL_PATH}")

try:
    modelo_rf = joblib.load(RF_MODEL_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"No se encontró el modelo Random Forest en la ruta: {RF_MODEL_PATH}")

# Exportamos los dos modelos para que pipeline_utils.py pueda importarlos
__all__ = ["modelo_lineal", "modelo_rf"]
