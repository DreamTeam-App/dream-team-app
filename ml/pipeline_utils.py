import pandas as pd
import numpy as np
import re
import statistics
from ml.predictor import modelo
from ml.aggregators import mbti_agg, treo_agg, co_eval_agg, to_float_clean

def predecir_desempeno_equipo(df_equipo):
    """
    Recibe un DataFrame con los datos de los estudiantes de un equipo
    (como los del dataset_consolidado.csv), lo limpia, lo agrega a nivel de equipo
    y lo pasa al modelo para predecir el desempeño.
    """
    # columnas numéricas a limpiar
    numeric_cols = [
        "Organizer","Doer","Challenger","Innovator","TeamBuilder","Connector",
        "Commitment","Communication","Motivation","GoalSetting",
        "DiversityPerception","EmotionalIntelligence","Trust",
        "WorkSatisfaction","Autonomy","ProcessIndicator",
        "Promedio Ponderado", "Nota actividad"
    ]
    for col in numeric_cols:
        if col in df_equipo.columns:
            df_equipo[col] = df_equipo[col].apply(to_float_clean)

    # Agregación de datos
    df_team = pd.Series({
        **mbti_agg(df_equipo),
        **treo_agg(df_equipo),
        **co_eval_agg(df_equipo),
        "PromPond_equipo": df_equipo["Promedio Ponderado"].mean(),
        "NotaActividad_equipo": df_equipo["Nota actividad"].mean()
    })

    # Promedio global de coevaluación
    coeval_means = [k for k in df_team.index if k.endswith("_mean") and k != "ProcessIndicator_mean"]
    df_team["PromedioCoevaluacion"] = df_team[coeval_means].mean()

    # Preparar datos para predicción
    df_team = pd.DataFrame([df_team])  # convertir a DataFrame
    X = df_team[modelo.feature_names_in_]
    return modelo.predict(X)[0]
