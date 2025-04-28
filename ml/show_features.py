# ml/show_features.py

import joblib
from ml.predictor import modelo

print("🔥 Features que el modelo espera:")
print(modelo.feature_names_in_.tolist())

try:
    scaler = joblib.load("ml/scaler.pkl")
    data_min = scaler.data_min_
    data_max = scaler.data_max_
    print("\n🔥 El scaler fue ajustado sobre estas columnas (misma orden que arriba):")
    for name, mn, mx in zip(modelo.feature_names_in_, data_min, data_max):
        print(f"  • {name}: min={mn:.3f}, max={mx:.3f}")
except FileNotFoundError:
    print("\n⚠ No encontré 'ml/scaler.pkl'. Asegúrate de haberlo reconstruido sin la columna 'Desempenho'.")
