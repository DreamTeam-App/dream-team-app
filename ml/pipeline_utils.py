import os
import joblib
import pandas as pd

from ml.predictor import modelo
from ml.aggregators import mbti_agg, treo_agg, co_eval_agg, to_float_clean

# ─── 1) CARGA DE ARTIFACTS ────────────────────────────────────────────────
BASE        = os.path.dirname(__file__)
MODEL_PATH  = os.path.join(BASE, "modelo_gb_regresion.pkl")
SCALER_PATH = os.path.join(BASE, "scaler.pkl")

modelo = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# ─── 2) FUNCIÓN DE PREDICCIÓN ─────────────────────────────────────────────
def predecir_desempeno_equipo(df_equipo: pd.DataFrame) -> float:
    """
    Recibe el DataFrame de raw inputs del equipo, aplica limpieza,
    agregaciones, scaling y devuelve la predicción final.
    """
    # — 2.1) LIMPIEZA de columnas numéricas
    numeric_cols = [
        "Organizer","Doer","Challenger","Innovator","TeamBuilder","Connector",
        "Commitment","Communication","Motivation","GoalSetting",
        "DiversityPerception","EmotionalIntelligence","Trust",
        "WorkSatisfaction","Autonomy","ProcessIndicator",
        "prom_ponderado"
    ]
    df = df_equipo.copy()
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(to_float_clean)

    # — 2.2) AGREGACIONES a nivel equipo
    team_ser = pd.Series({
        **mbti_agg(df),
        **treo_agg(df),
        **co_eval_agg(df),
        "PromPond_equipo": df["prom_ponderado"].mean(),
        # si en tu pipeline tienes la nota de la actividad, sustitúyela aquí:
        "NotaActividad_equipo": df.get("nota_actividad", 0) if "nota_actividad" in df.columns else 0
    })

    # — 2.3) PROMEDIO global de coevaluación
    coeval_means = [c for c in team_ser.index if c.endswith("_mean") and c != "ProcessIndicator_mean"]
    team_ser["PromedioCoevaluacion"] = team_ser[coeval_means].mean()

    # — 2.4) PREPARAR X para el modelo
    df_team       = pd.DataFrame([team_ser])
    cols_modelo   = list(modelo.feature_names_in_)  # exactamente las columnas que el modelo vio al entrenar
    df_for_scaling = df_team[cols_modelo]

    # — 2.5) ESCALAR con el scaler ya entrenado
    X_scaled = scaler.transform(df_for_scaling)

    # — 2.6) PREDICCIÓN final
    return float(modelo.predict(X_scaled)[0])


# ─── 3) INSPECCIÓN DE ENTRADA AL MODELO ──────────────────────────────────
def inspeccionar_entrada_modelo(df_equipo: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Igual que predecir_desempeno_equipo, pero devuelve el DataFrame
    *antes* de la transformación del scaler, para que veas exactamente
    qué va a entrar al modelo.
    """
    # Repetimos limpieza y agregaciones (idénticas a la función de arriba)
    df = df_equipo.copy()
    for col in [
        "Organizer","Doer","Challenger","Innovator","TeamBuilder","Connector",
        "Commitment","Communication","Motivation","GoalSetting",
        "DiversityPerception","EmotionalIntelligence","Trust",
        "WorkSatisfaction","Autonomy","ProcessIndicator",
        "prom_ponderado"
    ]:
        if col in df.columns:
            df[col] = df[col].apply(to_float_clean)

    team_ser = pd.Series({
        **mbti_agg(df),
        **treo_agg(df),
        **co_eval_agg(df),
        "PromPond_equipo": df["prom_ponderado"].mean(),
        "NotaActividad_equipo": df.get("nota_actividad", 0)
    })
    coeval_means = [c for c in team_ser.index if c.endswith("_mean") and c != "ProcessIndicator_mean"]
    team_ser["PromedioCoevaluacion"] = team_ser[coeval_means].mean()

    df_team     = pd.DataFrame([team_ser])
    cols_modelo = list(modelo.feature_names_in_)
    df_for_model = df_team[cols_modelo]

    if verbose:
        print("\n––– DataFrame de entrada al modelo (antes de escalar) –––")
        print(df_for_model.to_string(index=False))
        print("––––––––––––––––––––––––––––––––––––––––––––––––––––––––––\n")

    return df_for_model


# ─── 4) INSPECCIÓN DEL SCALER ─────────────────────────────────────────────
def inspeccionar_scaler(verbose: bool = True) -> pd.DataFrame:
    """
    Te muestra a qué columnas y con qué min/max se aplicó el scaler.
    Devuelve también un DataFrame con esa info.
    """
    cols      = list(modelo.feature_names_in_)
    data_min  = scaler.data_min_
    data_max  = scaler.data_max_
    df_info   = pd.DataFrame({
        "feature": cols,
        "data_min": data_min,
        "data_max": data_max
    })
    if verbose:
        print("\n––––– Información del MinMaxScaler –––––")
        print(df_info.to_string(index=False))
        print("––––––––––––––––––––––––––––––––––––––––––––––––\n")
    return df_info
 