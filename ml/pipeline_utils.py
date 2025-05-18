
import os
import joblib
import pandas as pd
import statistics
import numpy as np

from ml.predictor import modelo_lineal, modelo_rf
from ml.aggregators import mbti_agg, treo_agg, co_eval_agg, to_float_clean

# ─── 1) CARGA DE ARTIFACTS ────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
SCALER_PATH   = os.path.join(BASE, "scaler.pkl")

try:
    scaler   = joblib.load(SCALER_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"No se encontró el scaler en la ruta: {SCALER_PATH}")

model_lr = modelo_lineal
model_rf = modelo_rf

GLOBAL_CLIMA_STATS = {
    "Communication_mean": {"mean": 3.72123663, "std": 0.53265639},
    "Trust_mean": {"mean": 3.75686836, "std": 0.52847854},
    "Motivation_mean": {"mean": 3.69780246, "std": 0.51761451},
    "Commitment_mean": {"mean": 3.65991807, "std": 0.50726976},
    "WorkSatisfaction_mean": {"mean": 3.67493099, "std": 0.53790915},
    "DiversityPerception_mean": {"mean": 3.73491244, "std": 0.58075719},
    "EmotionalIntelligence_mean": {"mean": 3.76586159, "std": 0.57193606},
    "Autonomy_mean": {"mean": 3.70082602, "std": 0.50328700},
}
# --------------------------------------------------------------------

# ─── 2) FUNCIÓN DE PREDICCIÓN ─────────────────────────────────────────────
def predecir_desempeno_equipo(df_equipo: pd.DataFrame) -> float:
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_colwidth', None)

    df = df_equipo.copy()
    numeric_cols_input = [
        "Organizer","Doer","Challenger","Innovator","TeamBuilder","Connector",
        "Commitment","Communication","Motivation","GoalSetting",
        "DiversityPerception","EmotionalIntelligence","Trust",
        "WorkSatisfaction","Autonomy","ProcessIndicator", "prom_ponderado"
    ]
    for col in numeric_cols_input:
        if col in df.columns:
            df[col] = df[col].apply(to_float_clean)
        else:
            df[col] = np.nan

   
    
    team_ser_mbti = mbti_agg(df)
    team_ser_treo = treo_agg(df)
    team_ser_co_eval = co_eval_agg(df)

    team_ser_data = {**team_ser_mbti, **team_ser_treo, **team_ser_co_eval}
    if "prom_ponderado" in df.columns and df["prom_ponderado"].notna().any():
        team_ser_data["PromPond_equipo"] = df["prom_ponderado"].mean()
        team_ser_data["StdPromPond_equipo"] = df["prom_ponderado"].std(ddof=0)
    else:
        team_ser_data["PromPond_equipo"] = 0
        team_ser_data["StdPromPond_equipo"] = 0
    team_ser_data["NotaActividad_equipo"] = df_equipo["nota_actividad"].iloc[0] if "nota_actividad" in df_equipo and not df_equipo["nota_actividad"].empty else 0
    team_ser_data["Equipo"] = 0
    team_ser = pd.Series(team_ser_data)

    clima_cols_for_zscore = list(GLOBAL_CLIMA_STATS.keys())
    z_scores_dict = {}
    for col_name in clima_cols_for_zscore:
        current_val = team_ser.get(col_name, np.nan)
        z_score = np.nan
        if pd.notna(current_val) and col_name in GLOBAL_CLIMA_STATS:
            stats = GLOBAL_CLIMA_STATS[col_name]
            if pd.notna(stats.get("mean")) and pd.notna(stats.get("std")) and stats.get("std") != 0:
                z_score = (current_val - stats["mean"]) / stats["std"]
            elif pd.notna(stats.get("mean")) and stats.get("std") == 0:
                z_score = 0.0 if current_val == stats["mean"] else np.nan
        team_ser[f"{col_name}_zscore"] = z_score
        z_scores_dict[col_name] = z_score
    valid_z_scores = [zs for zs in z_scores_dict.values() if pd.notna(zs)]
    team_ser["IGC"] = statistics.mean(valid_z_scores) if valid_z_scores else 0

    team_ser["clima_alto"] = int(team_ser.get("Communication_mean", 0) >= 4)
    team_ser["has_high_doer"] = int(team_ser.get("#High_Doer", 0) >= 1)
    team_ser["has_high_tb"]   = int(team_ser.get("#High_TB", 0) >= 1)
    team_ser["has_high_org"]  = int(team_ser.get("#High_Organizer", 0) >= 1)

    current_team_size_val = team_ser.get("team_size", 0) 
    
    std_cols_from_aggregators = [k for k in team_ser.index if k.startswith("Std_")]
    for std_col_name in std_cols_from_aggregators:
        norm_col_name = f"{std_col_name}_norm"
        if std_col_name == "StdPromPond_equipo": 
            continue
        if current_team_size_val > 0:
            team_ser[norm_col_name] = team_ser.get(std_col_name, 0) / current_team_size_val
        else:
            team_ser[norm_col_name] = 0

    team_ser["Comm_x_TeamSize"] = team_ser.get("Communication_mean", 0) * current_team_size_val # Usa el team_size original
    
    z_motivation = z_scores_dict.get("Motivation_mean", 0)
    z_communication = z_scores_dict.get("Communication_mean", 0)
    team_ser["Motiv_x_Comm"] = z_motivation * z_communication


    std_doer_norm_val = team_ser.get("Std_Doer_norm", 0)
    communication_mean_direct = team_ser.get("Communication_mean", 0)
    team_ser["StdDoerNorm_x_Comm"] = std_doer_norm_val * communication_mean_direct
    team_ser["Std_Doer_norm_x_Comm"] = team_ser["StdDoerNorm_x_Comm"]

    coeval_direct_means_cols = [f"{c}_mean" for c in ["Commitment","Communication","Motivation","GoalSetting","DiversityPerception","EmotionalIntelligence","Trust","WorkSatisfaction","Autonomy"]]
    valid_coeval_direct_means = [team_ser[c] for c in coeval_direct_means_cols if c in team_ser and pd.notna(team_ser.get(c))]
    team_ser["PromedioCoevaluacion"] = statistics.mean(valid_coeval_direct_means) if valid_coeval_direct_means else 0

    # --- SECCIÓN DE WINSORIZACIÓN (ANTES DE CREAR df_team PARA EL SCALER) ---
    

    features_to_winsorize = [
        "team_size",        
        "Std_Doer_norm",   
    ]

    if hasattr(scaler, 'feature_names_in_') and hasattr(scaler, 'data_min_') and hasattr(scaler, 'data_max_'):
        scaler_feature_indices = {name: i for i, name in enumerate(scaler.feature_names_in_)}
        for feature_name in features_to_winsorize:
            if feature_name in team_ser.index and feature_name in scaler_feature_indices:
                original_value = team_ser[feature_name]
                winsorized_value = original_value
                idx = scaler_feature_indices[feature_name]

                if idx < len(scaler.data_min_) and idx < len(scaler.data_max_):
                    min_val_scaler = scaler.data_min_[idx]
                    max_val_scaler = scaler.data_max_[idx]
                    if pd.notna(original_value):
                        if original_value < min_val_scaler:
                            winsorized_value = min_val_scaler
                        elif original_value > max_val_scaler:
                            winsorized_value = max_val_scaler
                        team_ser[feature_name] = winsorized_value 

    # -------------------------------------------------------------------------

    df_team = pd.DataFrame([team_ser]) # df_team ahora usa los valores potencialmente winsorizados

    try:
        SCALER_FEATURES = list(scaler.feature_names_in_)
    except AttributeError:
        raise ValueError("El scaler cargado no tiene 'feature_names_in_'.")
    
    missing_features_for_scaler = []
    for feature in SCALER_FEATURES:
        if feature not in df_team.columns:
            df_team[feature] = 0.0
            missing_features_for_scaler.append(feature)

   
    if hasattr(scaler, 'data_min_') and hasattr(scaler, 'data_max_') and hasattr(scaler, 'feature_names_in_'):
        scaler_feature_indices = {name: i for i, name in enumerate(scaler.feature_names_in_)}
        features_to_check_detailed = ['Motiv_x_Comm', 'Std_Doer_norm', 'team_size', 'IGC',
                                      'Std_EI_norm', 'Std_NS_norm', 'Std_TF_norm', 'Std_JP_norm',
                                      'Std_Organizer_norm'] 
        for feature_name in features_to_check_detailed:
            if feature_name in df_team.columns and feature_name in scaler_feature_indices: 
                current_value = df_team[feature_name].iloc[0] 
                idx = scaler_feature_indices[feature_name]
                if idx < len(scaler.data_min_) and idx < len(scaler.data_max_):
                    s_min = scaler.data_min_[idx]
                    s_max = scaler.data_max_[idx]


    
    X_to_scale = df_team[SCALER_FEATURES]
    X_scaled_array = scaler.transform(X_to_scale)
    df_scaled = pd.DataFrame(X_scaled_array, columns=SCALER_FEATURES)
    df_scaled["Equipo"] = team_ser.get("Equipo", 0)



    FEATURES_RF = [c for c in model_rf.feature_names_in_ if c != 'Equipo']
    missing_rf = [f for f in FEATURES_RF if f not in df_scaled.columns]
    if missing_rf: raise ValueError(f"Faltan características para RF en df_scaled: {missing_rf}")
    df_input_rf = df_scaled[FEATURES_RF]
    pred_rf = model_rf.predict(df_input_rf)[0]
    print(f"🔸 RF pred: {pred_rf:.4f}")

    FEATURES_LR_MODEL = list(model_lr.feature_names_in_)
    missing_lr = [f for f in FEATURES_LR_MODEL if f not in df_scaled.columns]
    if missing_lr: raise ValueError(f"Faltan características para LR en df_scaled: {missing_lr}")
    X_lr_scaled = df_scaled[FEATURES_LR_MODEL]
    

    pred_lr = model_lr.predict(X_lr_scaled)[0]
    print(f"🔸 LR pred: {pred_lr:.4f}")

    ensemble_pred = (pred_lr + pred_rf) / 2
    print(f"🔹 Ensemble pred: {ensemble_pred:.4f}")
    return float(ensemble_pred)