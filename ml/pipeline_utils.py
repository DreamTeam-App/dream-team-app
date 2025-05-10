import os
import joblib
import pandas as pd
import statistics

from ml.predictor import modelo_lineal, modelo_rf
from ml.aggregators import mbti_agg, treo_agg, co_eval_agg, to_float_clean

# ─── 1) CARGA DE ARTIFACTS ────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
SCALER_PATH   = os.path.join(BASE, "scaler.pkl")
LR_MODEL_PATH = os.path.join(BASE, "modelo_lineal.pkl")
RF_MODEL_PATH = os.path.join(BASE, "modelo_rf_regresion.pkl")

scaler   = joblib.load(SCALER_PATH)
model_lr = modelo_lineal
model_rf = modelo_rf

# ─── Conjunto de features para Regresión Lineal ──────────────────────────
FEATURES_LR = [
    'IGC',
    'Motiv_x_Comm',
    'Std_Doer_norm',
    'Std_Organizer_norm',
    'team_size',
    '#TiposUnicosMBTI',
    '#High_Doer',
    'StdPromPond_equipo'
]

# ─── 2) FUNCIÓN DE PREDICCIÓN ─────────────────────────────────────────────
def predecir_desempeno_equipo(df_equipo: pd.DataFrame) -> float:
    """
    Recibe el DataFrame de raw inputs del equipo, aplica limpieza,
    agregaciones, cálculo de IGC, scaling y devuelve el promedio
    de predicciones de Linear y Random Forest.
    """
    # 2.1) Limpieza de columnas numéricas
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

    # 2.2) Agregaciones a nivel equipo
    team_ser = pd.Series({
        **mbti_agg(df),
        **treo_agg(df),
        **co_eval_agg(df),
        "PromPond_equipo": df.get("prom_ponderado", pd.Series()).mean(),
        "StdPromPond_equipo": df.get("prom_ponderado", pd.Series()).std(ddof=0),
        "NotaActividad_equipo": df.get("nota_actividad", 0)
    })

    # Quick-fix: llenar la columna 'Equipo' con placeholder
    team_ser["Equipo"] = 0

    # Debug: claves generadas
    print(">>> team_ser keys:", list(team_ser.index))

    # Flags de high performers
    team_ser["clima_alto"]    = int(team_ser.get("Communication_mean", 0) >= 4)
    team_ser["has_high_doer"] = int(team_ser.get("#High_Doer", 0) >= 1)
    team_ser["has_high_tb"]   = int(team_ser.get("#High_TB", 0) >= 1)
    team_ser["has_high_org"]  = int(team_ser.get("#High_Organizer", 0) >= 1)

    # Normalización de Std_* por tamaño de equipo
    std_keys = [k for k in team_ser.index if k.startswith("Std_")]
    for key in std_keys:
        team_ser[f"{key}_norm"] = team_ser[key] / team_ser["team_size"]

    # Heterogeneidad ajustada por tamaño
    team_ser["Comm_x_TeamSize"] = team_ser.get("Communication_mean", 0) * team_ser["team_size"]

    # Interacciones
    team_ser["Motiv_x_Comm"]         = (
        team_ser.get("Motivation_mean", 0) *
        team_ser.get("Communication_mean", 0)
    )
    team_ser["Std_Doer_norm_x_Comm"] = (
        team_ser.get("Std_Doer_norm", 0) *
        team_ser.get("Communication_mean", 0)
    )
    team_ser["Std_Doer_norm_mod"]    = team_ser["Std_Doer_norm_x_Comm"]
    # Alias para compatibilidad con scaler
    team_ser["StdDoerNorm_x_Comm"]   = team_ser.get("Std_Doer_norm_x_Comm", 0)

    # Promedio global de coevaluación
    coeval_means = [c for c in team_ser.index if c.endswith("_mean") and c != "ProcessIndicator_mean"]
    team_ser["PromedioCoevaluacion"] = team_ser[coeval_means].mean()

    # Cálculo manual de IGC
    clima_cols = [
        "Communication_mean", "Trust_mean", "Motivation_mean",
        "Commitment_mean", "WorkSatisfaction_mean",
        "DiversityPerception_mean", "EmotionalIntelligence_mean",
        "Autonomy_mean"
    ]
    vals      = [team_ser.get(c, 0) for c in clima_cols]
    mean_vals = statistics.mean(vals)
    std_vals  = statistics.pstdev(vals) if len(vals) > 1 else 0
    zscores   = [(v - mean_vals) / std_vals if std_vals > 0 else 0 for v in vals]
    team_ser["IGC"] = sum(zscores) / len(zscores)

    # 2.3) Crear DataFrame de features
    df_team = pd.DataFrame([team_ser])

    # Debug: antes de escalar
    SCALER_FEATURES = list(scaler.feature_names_in_)
    print("🔍 SCALER_FEATURES:", SCALER_FEATURES)
    print("🔍 df_team cols before scale:", df_team.columns.tolist())

    # 2.4) Escalado del superset para RF
    X_to_scale     = df_team[SCALER_FEATURES]
    X_scaled_array = scaler.transform(X_to_scale)
    df_scaled       = pd.DataFrame(X_scaled_array, columns=SCALER_FEATURES)
    # Inyectar 'Equipo' para RF
    df_scaled["Equipo"] = df_team["Equipo"].iloc[0]

    # Debug: tras escalado
    print("🔍 df_scaled cols:", df_scaled.columns.tolist())

    # 2.5) Filtrar para RF y predecir
    FEATURES_RF      = list(model_rf.feature_names_in_)
    print("🔍 FEATURES_RF:", FEATURES_RF)
    present_rf = [c for c in FEATURES_RF if c in df_scaled.columns]
    missing_rf = [c for c in FEATURES_RF if c not in df_scaled.columns]
    print("🔍 Present_rf:", present_rf)
    print("🔍 Missing_rf:", missing_rf)
    df_full_scaled = df_scaled[FEATURES_RF]
    pred_rf        = model_rf.predict(df_full_scaled)[0]
    print(f"🔸 RF pred: {pred_rf}")

    # 2.6) Filtrar subset LR y predecir
    print("🔍 FEATURES_LR:", FEATURES_LR)
    present_lr = [c for c in FEATURES_LR if c in df_full_scaled.columns]
    missing_lr = [c for c in FEATURES_LR if c not in df_full_scaled.columns]
    print("🔍 Present_lr:", present_lr)
    print("🔍 Missing_lr:", missing_lr)
    X_lr_scaled = df_full_scaled[FEATURES_LR]
    pred_lr     = model_lr.predict(X_lr_scaled)[0]
    print(f"🔸 LR pred: {pred_lr}")

    # 2.7) Ensemble
    ensemble_pred = (pred_lr + pred_rf) / 2
    print(f"🔹 Ensemble pred: {ensemble_pred}")
    return float(ensemble_pred)