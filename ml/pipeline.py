# ml/pipeline.py
import pandas as pd
import joblib
from ml.predictor import modelo
from ml.aggregators import mbti_agg, treo_agg, co_eval_agg, to_float_clean
from firebase_admin import firestore

numeric_cols = [ # asegúrate que estos coincidan con tu dataset
    "Organizer","Doer","Challenger","Innovator","TeamBuilder","Connector",
    "Commitment","Communication","Motivation","GoalSetting",
    "DiversityPerception","EmotionalIntelligence","Trust",
    "WorkSatisfaction","Autonomy","ProcessIndicator",
    "Promedio Ponderado", "Nota actividad"
]

def obtener_datos_individuales(equipo_id):
    db = firestore.client()
    estudiantes = db.collection("estudiantes").where("Equipo", "==", equipo_id).stream()
    filas = [doc.to_dict() for doc in estudiantes]
    return pd.DataFrame(filas)

def predecir_equipo_desde_firebase(equipo_id):
    df_ind = obtener_datos_individuales(equipo_id)
    if df_ind.empty:
        raise ValueError("No se encontraron estudiantes para ese equipo")

    # limpieza
    for col in numeric_cols:
        if col in df_ind.columns:
            df_ind[col] = df_ind[col].apply(to_float_clean)

    # agregación
    df_team = (
        df_ind
        .groupby("Equipo")
        .apply(lambda g: pd.Series({
            **mbti_agg(g),
            **treo_agg(g),
            **co_eval_agg(g),
            "PromPond_equipo": g["Promedio Ponderado"].mean(),
            "NotaActividad_equipo": g["Nota actividad"].mean()
        }))
        .reset_index()
    )

    # cálculo de desempeño
    ratio_raw  = df_team["NotaActividad_equipo"] / df_team["PromPond_equipo"]
    ratio_norm = (ratio_raw.clip(lower=0, upper=1.5)) / 1.5
    coev_norm  = df_team["PromedioCoevaluacion"] / 5
    proc_norm  = df_team["ProcessIndicator_mean"] / 5

    df_team["Desempenho"] = (
        0.5 * ratio_norm +
        0.3 * coev_norm +
        0.2 * proc_norm
    )

    # predicción
    X = df_team[modelo.feature_names_in_]
    return modelo.predict(X)[0]
