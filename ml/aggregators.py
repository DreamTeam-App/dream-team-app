import re
import numpy as np
import pandas as pd
import statistics

def to_float_clean(s):
    """
    Limpia strings numéricos: cambia coma decimal, extrae primer número, o NaN.
    """
    if pd.isna(s):
        return np.nan
    s = str(s).replace(',', '.')
    m = re.search(r"\d+(?:\.\d+)?", s)
    return float(m.group()) if m else np.nan


def mbti_agg(subdf):
    """
    Métricas de diversidad MBTI + tamaño de equipo + nº líderes.
    """
    subdf = subdf[subdf["MBTI"].notna()]
    total = len(subdf)
    E_count = sum(m.startswith("E") for m in subdf["MBTI"])
    I_count = total - E_count

    S_count = sum(m[1] == "S" for m in subdf["MBTI"])
    N_count = total - S_count

    T_count = sum(m[2] == "T" for m in subdf["MBTI"])
    F_count = total - T_count

    J_count = sum(m[3] == "J" for m in subdf["MBTI"])
    P_count = total - J_count

    props = {
        'E': E_count/total, 'I': I_count/total,
        'S': S_count/total, 'N': N_count/total,
        'T': T_count/total, 'F': F_count/total,
        'J': J_count/total, 'P': P_count/total,
    }
    std_EI = statistics.pstdev([props['E'], props['I']])
    std_NS = statistics.pstdev([props['S'], props['N']])
    std_TF = statistics.pstdev([props['T'], props['F']])
    std_JP = statistics.pstdev([props['J'], props['P']])

    return {
        "team_size": total,
        "Std_EI": std_EI,
        "Std_NS": std_NS,
        "Std_TF": std_TF,
        "Std_JP": std_JP,
        "#Lideres_ENTJ_ESTP": sum(m in ["ENTJ", "ESTP"] for m in subdf["MBTI"]),
        "#TiposUnicosMBTI": subdf["MBTI"].nunique()
    }


def treo_agg(subdf):
    """
    Promedios y desviaciones TREO + nº de miembros >4 en Organizer, Doer, TeamBuilder.
    """
    roles = ["Organizer", "Doer", "Challenger", "Innovator", "TeamBuilder", "Connector"]
    out = {}
    for r in roles:
        out[f"Avg_{r}"] = subdf[r].mean()
        out[f"Std_{r}"] = subdf[r].std()
    out["#High_Organizer"] = (subdf["Organizer"] > 4).sum()
    out["#High_Doer"]      = (subdf["Doer"] > 4).sum()
    out["#High_TB"]        = (subdf["TeamBuilder"] > 4).sum()
    return out


def co_eval_agg(subdf):
    """
    Promedio de cada característica de coevaluación a nivel equipo.
    """
    cols = [
        "Commitment", "Communication", "Motivation", "GoalSetting",
        "DiversityPerception", "EmotionalIntelligence", "Trust",
        "WorkSatisfaction", "Autonomy", "ProcessIndicator"
    ]
    return {f"{c}_mean": subdf[c].mean() for c in cols}

# ─── 4) AGGREGATOR: Índice Global de Clima ────────────────────────────────────
def clima_agg(subdf):
    """
    Estandariza las 8 métricas de clima (z-score) y calcula el IGC (media de z-scores).
    """
    clima_cols = [
        "Communication_mean", "Trust_mean", "Motivation_mean",
        "Commitment_mean", "WorkSatisfaction_mean",
        "DiversityPerception_mean", "EmotionalIntelligence_mean",
        "Autonomy_mean"
    ]
    # Asegúrate de limpiar primero los NaN / strings
    clean = subdf.copy()
    for col in clima_cols:
        clean[col] = clean[col].apply(to_float_clean)

    # Cálculo de medias y desviaciones por característica
    means = clean[clima_cols].mean()
    stds  = clean[clima_cols].std()

    # Z-score por miembro y característica
    zscores = (clean[clima_cols] - means) / stds

    # IGC: promedio de todos los z-scores
    igc = zscores.values.mean()

    return {"IGC": igc}
