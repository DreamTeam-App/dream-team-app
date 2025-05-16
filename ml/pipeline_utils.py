
import os
import joblib
import pandas as pd
import statistics
import numpy as np # Asegúrate de que esté importado

from ml.predictor import modelo_lineal, modelo_rf # Asume que estos son los modelos cargados
from ml.aggregators import mbti_agg, treo_agg, co_eval_agg, to_float_clean

# ─── 1) CARGA DE ARTIFACTS ────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
SCALER_PATH   = os.path.join(BASE, "scaler.pkl")

try:
    scaler   = joblib.load(SCALER_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"No se encontró el scaler en la ruta: {SCALER_PATH}")

model_lr = modelo_lineal # Ya cargados desde ml.predictor
model_rf = modelo_rf # Ya cargados desde ml.predictor

# --- !! DEBES RELLENAR ESTAS CONSTANTES GLOBALES CON TUS VALORES !! ---
# Estas son las medias y desviaciones estándar de las 8 _mean de clima,
# calculadas sobre TODO el conjunto de entrenamiento original.
# Reemplaza los placeholders con los valores reales que calculaste.
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

# Lista original de features para LR (como referencia, pero el modelo usa feature_names_in_)
# FEATURES_LR_ORIGINAL_DEF = [
#     'IGC', 'Motiv_x_Comm', 'Std_Doer_norm', 'Std_Organizer_norm',
#     'Comm_x_TeamSize', 'team_size', '#TiposUnicosMBTI', '#High_Doer', 'StdPromPond_equipo'
# ]

# ─── 2) FUNCIÓN DE PREDICCIÓN ─────────────────────────────────────────────
def predecir_desempeno_equipo(df_equipo: pd.DataFrame) -> float:
    """
    Recibe el DataFrame de raw inputs del equipo, aplica limpieza,
    agregaciones según el método original, cálculo de IGC, scaling
    y devuelve el promedio de predicciones de Linear y Random Forest.
    """
    # --- Opciones de Pandas para mostrar todo en logs de debug ---
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 200) # Ajusta este ancho si es necesario
    pd.set_option('display.max_colwidth', None)
    # -------------------------------------------------------------

    # 2.1) Limpieza de columnas numéricas de entrada
    df = df_equipo.copy()
    numeric_cols_input = [ # Columnas que vienen del CSV y necesitan ser numéricas
        "Organizer","Doer","Challenger","Innovator","TeamBuilder","Connector",
        "Commitment","Communication","Motivation","GoalSetting",
        "DiversityPerception","EmotionalIntelligence","Trust",
        "WorkSatisfaction","Autonomy","ProcessIndicator", "prom_ponderado"
    ]
    for col in numeric_cols_input:
        if col in df.columns:
            df[col] = df[col].apply(to_float_clean)
        else:
            # Si una columna numérica esperada del input no existe, añadirla con NaN
            # Esto puede suceder si el formato del CSV de entrada cambia.
            print(f"Advertencia (Input): La columna '{col}' no estaba en df_equipo. Se añadió con NaN.")
            df[col] = np.nan

    # 2.2) Agregaciones a nivel equipo (usando funciones de aggregators.py)
    print("\n--- DEBUG: DataFrame de entrada (df) para agregaciones (primeras filas) ---")
    print(df.head())
    
    team_ser_mbti = mbti_agg(df)        # Debe devolver "team_size", "Std_EI", "Std_NS", etc.
    team_ser_treo = treo_agg(df)        # Debe devolver "Avg_Rol", "Std_Rol", "#High_Rol" (Std con ddof=0)
    team_ser_co_eval = co_eval_agg(df)  # Debe devolver "Caracteristica_mean"

    # Ensamblar la serie de características del equipo
    team_ser_data = {
        **team_ser_mbti,
        **team_ser_treo,
        **team_ser_co_eval,
    }

    # Manejo de prom_ponderado y nota_actividad
    # "PromedioPonderado" en la descripción original
    if "prom_ponderado" in df.columns and df["prom_ponderado"].notna().any():
        team_ser_data["PromPond_equipo"] = df["prom_ponderado"].mean()
        team_ser_data["StdPromPond_equipo"] = df["prom_ponderado"].std(ddof=0) # ddof=0 según original
    else:
        team_ser_data["PromPond_equipo"] = 0 # o np.nan
        team_ser_data["StdPromPond_equipo"] = 0 # o np.nan
        
    # NotaActividad_equipo (si se usa y viene del df_equipo original)
    # Si 'nota_actividad' es una columna en df_equipo (el DataFrame que entra a la función):
    team_ser_data["NotaActividad_equipo"] = df_equipo["nota_actividad"].iloc[0] if "nota_actividad" in df_equipo and not df_equipo["nota_actividad"].empty else 0


    team_ser_data["Equipo"] = 0 # Placeholder, parece no usarse en modelos

    team_ser = pd.Series(team_ser_data)

    # --- INICIO DE INGENIERÍA DE CARACTERÍSTICAS SEGÚN MÉTODO ORIGINAL ---

    # Punto 1 Original: Estandarización de las 8 escalas de clima y cálculo de IGC
    clima_cols_for_zscore = [
        "Communication_mean", "Trust_mean", "Motivation_mean", "Commitment_mean",
        "WorkSatisfaction_mean", "DiversityPerception_mean", "EmotionalIntelligence_mean", "Autonomy_mean"
    ]
    z_scores_dict = {} # Para almacenar los z-scores individuales

    print("\n--- DEBUG: Calculando Z-scores para clima_cols ---")
    for col_name in clima_cols_for_zscore:
        current_col_mean_value = team_ser.get(col_name, np.nan)
        z_score = np.nan # Valor por defecto

        if pd.notna(current_col_mean_value) and col_name in GLOBAL_CLIMA_STATS:
            global_mean = GLOBAL_CLIMA_STATS[col_name].get("mean")
            global_std = GLOBAL_CLIMA_STATS[col_name].get("std")

            if pd.notna(global_mean) and pd.notna(global_std):
                if global_std != 0:
                    z_score = (current_col_mean_value - global_mean) / global_std
                else: # Si std global es 0, y la media actual es igual a la global, z-score es 0. Sino, es indefinido (o un valor grande).
                    z_score = 0.0 if current_col_mean_value == global_mean else np.nan # O manejar como error/valor extremo
                    print(f"Advertencia Z-score: std global para '{col_name}' es 0. Z-score establecido a {z_score}.")
            else:
                print(f"Advertencia Z-score: Faltan mean/std globales para '{col_name}'. Z-score establecido a NaN.")
        else:
            print(f"Advertencia Z-score: Columna '{col_name}' no encontrada en team_ser o GLOBAL_CLIMA_STATS. Z-score establecido a NaN.")
        
        team_ser[f"{col_name}_zscore"] = z_score # Guardar la versión z-score
        z_scores_dict[col_name] = z_score
        print(f"  {col_name}: Valor_mean={current_col_mean_value:.4f}, Z-score={z_score:.4f}")

    # Calcular IGC como la media de los z-scores válidos
    valid_z_scores = [zs for zs in z_scores_dict.values() if pd.notna(zs)]
    if valid_z_scores:
        team_ser["IGC"] = statistics.mean(valid_z_scores)
    else:
        team_ser["IGC"] = 0 # o np.nan si todos los z-scores fueron NaN
    print(f"  IGC (media de z-scores válidos): {team_ser['IGC']:.4f}")

    # Punto 3 Original: Efecto umbral de comunicación (usa Communication_mean directa, NO z-score)
    team_ser["clima_alto"] = int(team_ser.get("Communication_mean", 0) >= 4)

    # Punto 4 Original: Presencia de "High Performers"
    team_ser["has_high_doer"] = int(team_ser.get("#High_Doer", 0) >= 1)
    team_ser["has_high_tb"]   = int(team_ser.get("#High_TB", 0) >= 1)
    team_ser["has_high_org"]  = int(team_ser.get("#High_Organizer", 0) >= 1)

    # Punto 5 Original: Heterogeneidad ajustada por tamaño de equipo
    # Normaliza TODAS las Std_* por team_size para crear las _norm
    current_team_size = team_ser.get("team_size", 0)
    std_cols_from_aggregators = [k for k in team_ser.index if k.startswith("Std_")] # Todas las Std_ calculadas

    print(f"\n--- DEBUG: Normalizando Std_* por team_size ({current_team_size}) ---")
    for std_col_name in std_cols_from_aggregators: # ej: "Std_EI", "Std_Organizer", "StdPromPond_equipo"
        norm_col_name = f"{std_col_name}_norm" # ej: "Std_EI_norm", "Std_Organizer_norm"
        
        # Excepción: StdPromPond_equipo no parece necesitar _norm según tus SCALER_FEATURES
        if std_col_name == "StdPromPond_equipo": # Si esta no se normaliza, sáltala.
            print(f"  Skipping normalization for {std_col_name} as it seems not to be a _norm feature in scaler.")
            continue

        if current_team_size > 0:
            team_ser[norm_col_name] = team_ser.get(std_col_name, 0) / current_team_size
        else:
            team_ser[norm_col_name] = 0 # o np.nan
        print(f"  {std_col_name} ({team_ser.get(std_col_name, 0):.4f}) / {current_team_size} -> {norm_col_name} ({team_ser[norm_col_name]:.4f})")
            
    # Punto 6 Original: Interacción clima-tamaño (usa Communication_mean directa)
    team_ser["Comm_x_TeamSize"] = team_ser.get("Communication_mean", 0) * current_team_size

    # Punto 7 Original: Sinergia Motivación × Comunicación (USA Z-SCORES)
    z_motivation = z_scores_dict.get("Motivation_mean", 0) # Usa el z-score calculado
    z_communication = z_scores_dict.get("Communication_mean", 0) # Usa el z-score calculado
    team_ser["Motiv_x_Comm"] = z_motivation * z_communication
    print(f"\n--- DEBUG: Para Motiv_x_Comm (con z-scores) ---")
    print(f"  Motivation_mean_zscore: {z_motivation:.4f}")
    print(f"  Communication_mean_zscore: {z_communication:.4f}")
    print(f"  Motiv_x_Comm (producto z-scores): {team_ser['Motiv_x_Comm']:.4f}")

    # Punto 8 Original: Moderación de la diversidad de Doers por la comunicación
    # (Usa Communication_mean directa y Std_Doer_norm)
    # Std_Doer_norm ya debería estar calculada en el bucle de Punto 5
    std_doer_norm_val = team_ser.get("Std_Doer_norm", 0)
    communication_mean_direct = team_ser.get("Communication_mean", 0)
    team_ser["StdDoerNorm_x_Comm"] = std_doer_norm_val * communication_mean_direct
    
    # Alias (si son necesarios para el scaler o modelos)
    team_ser["Std_Doer_norm_x_Comm"] = team_ser["StdDoerNorm_x_Comm"]
    # team_ser["Std_Doer_norm_mod"] = team_ser["StdDoerNorm_x_Comm"] # Si es realmente un alias de lo mismo

    # PromedioCoevaluacion (según tu implementación anterior, como media de medias directas)
    # Esto es distinto del IGC. Asegúrate si esta característica se usó en el entrenamiento.
    coeval_direct_means_cols = [f"{c}_mean" for c in [
        "Commitment","Communication","Motivation","GoalSetting",
        "DiversityPerception","EmotionalIntelligence","Trust",
        "WorkSatisfaction","Autonomy" # Excluyendo ProcessIndicator
    ]]
    valid_coeval_direct_means = [team_ser[c] for c in coeval_direct_means_cols if c in team_ser and pd.notna(team_ser.get(c))]
    if valid_coeval_direct_means:
        team_ser["PromedioCoevaluacion"] = statistics.mean(valid_coeval_direct_means)
    else:
        team_ser["PromedioCoevaluacion"] = 0 # o np.nan

    # --- FIN DE INGENIERÍA DE CARACTERÍSTICAS ---

    print("\n>>> team_ser keys (después de ingeniería de características FINAL):", sorted(list(team_ser.index)))
    df_team = pd.DataFrame([team_ser])

    # 2.3) Preparación para el escalado
    try:
        SCALER_FEATURES = list(scaler.feature_names_in_)
    except AttributeError:
        raise ValueError("El scaler cargado no tiene el atributo 'feature_names_in_'. Asegúrate de que fue ajustado con nombres de características.")
    
    print("\n--- DEBUG: df_team ANTES DE ESCALAR (verificando SCALER_FEATURES) ---")
    missing_features_for_scaler = []
    for feature in SCALER_FEATURES:
        if feature not in df_team.columns:
            # Si una característica esperada por el scaler no se generó, es un problema.
            # Podrías añadirla con 0/NaN y advertir, o levantar un error.
            # Por ahora, advertiremos y añadiremos con 0.
            print(f"ADVERTENCIA CRÍTICA: La SCALER_FEATURE '{feature}' no fue generada en team_ser. Se añadirá con 0.")
            df_team[feature] = 0.0 # O np.nan
            missing_features_for_scaler.append(feature)
    if missing_features_for_scaler:
         print(f"  Columnas que faltaban y se añadieron con 0 para el scaler: {missing_features_for_scaler}")
    print(df_team[SCALER_FEATURES])
    
    # --- DEBUG: Comparación de valores actuales (antes de escalar) con rangos del scaler ---
    print("\n--- DEBUG: Comparación de valores actuales (antes de escalar) con rangos del scaler (MinMaxScaler asumido) ---")
    if hasattr(scaler, 'data_min_') and hasattr(scaler, 'data_max_') and hasattr(scaler, 'feature_names_in_'):
        scaler_feature_indices = {name: i for i, name in enumerate(scaler.feature_names_in_)}
        features_to_check_detailed = ['Motiv_x_Comm', 'Std_Doer_norm', 'team_size', 'IGC'] # Añadido IGC
        for feature_name in features_to_check_detailed:
            if feature_name in df_team.columns and feature_name in scaler_feature_indices:
                current_value = df_team[feature_name].iloc[0]
                idx = scaler_feature_indices[feature_name]
                # Verificar si idx está dentro del rango de data_min_ y data_max_
                if idx < len(scaler.data_min_) and idx < len(scaler.data_max_):
                    s_min = scaler.data_min_[idx]
                    s_max = scaler.data_max_[idx]
                    print(f"  Feature: {feature_name}")
                    print(f"    Valor Actual (antes de escalar): {current_value:.4f}")
                    print(f"    Scaler min (entrenamiento):    {s_min:.4f}")
                    print(f"    Scaler max (entrenamiento):    {s_max:.4f}")
                    if pd.notna(current_value) and pd.notna(s_max) and current_value > s_max: print(f"    ¡ALERTA! Valor actual > Scaler max")
                    if pd.notna(current_value) and pd.notna(s_min) and current_value < s_min: print(f"    ¡ALERTA! Valor actual < Scaler min")
                else:
                    print(f"  Índice {idx} para '{feature_name}' fuera de rango para data_min_/data_max_ del scaler.")
            else:
                print(f"  Feature '{feature_name}' no en df_team o no en scaler.feature_names_in_ para depuración detallada.")
    else:
        print("  El scaler no es MinMaxScaler o faltan atributos para la depuración detallada de rangos.")
    # -----------------------------------------------------------------------------------
    
    # 2.4) Escalado
    X_to_scale = df_team[SCALER_FEATURES]
    X_scaled_array = scaler.transform(X_to_scale)
    df_scaled = pd.DataFrame(X_scaled_array, columns=SCALER_FEATURES)
    df_scaled["Equipo"] = team_ser.get("Equipo", 0) # Re-inyectar si es necesario, usando valor de team_ser

    print("\n--- DEBUG: df_scaled (DESPUÉS de escalar) ---")
    print(df_scaled.head())

    # 2.5) Predicción con Random Forest
    FEATURES_RF = [c for c in model_rf.feature_names_in_ if c != 'Equipo'] # Excluir 'Equipo' si RF no lo usa
    missing_rf = [f for f in FEATURES_RF if f not in df_scaled.columns]
    if missing_rf:
        raise ValueError(f"Faltan características para RF en df_scaled: {missing_rf}")
    df_input_rf = df_scaled[FEATURES_RF]
    pred_rf = model_rf.predict(df_input_rf)[0]
    print(f"🔸 RF pred: {pred_rf:.4f}")

    # 2.6) Predicción con Regresión Lineal
    FEATURES_LR_MODEL = list(model_lr.feature_names_in_)
    missing_lr = [f for f in FEATURES_LR_MODEL if f not in df_scaled.columns]
    if missing_lr:
        raise ValueError(f"Faltan características para LR en df_scaled: {missing_lr}")
    X_lr_scaled = df_scaled[FEATURES_LR_MODEL] # Seleccionar y reordenar según el modelo LR

    print("\n--- DEBUG: Características que entran al modelo LR (X_lr_scaled) ---")
    print(X_lr_scaled)
    
    pred_lr = model_lr.predict(X_lr_scaled)[0]
    print(f"🔸 LR pred: {pred_lr:.4f}")

    # 2.7) Ensemble
    ensemble_pred = (pred_lr + pred_rf) / 2
    print(f"🔹 Ensemble pred: {ensemble_pred:.4f}")
    return float(ensemble_pred)
