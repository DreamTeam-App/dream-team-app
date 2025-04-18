import statistics
import pandas as pd
import numpy as np
import re

# -------------------------
# Función de limpieza
# -------------------------
def to_float_clean(s):
    """
    Convierte un string a float, tolerando errores como comas y caracteres extra.
    """
    if pd.isna(s):
        return np.nan
    s = str(s).replace(',', '.')
    m = re.search(r'\d+(?:\.\d+)?', s)
    return float(m.group()) if m else np.nan

# -------------------------
# Agregación MBTI
# -------------------------
def mbti_agg(subdf):
    subdf = subdf[subdf["MBTI"].notna()]
    total = len(subdf)

    if total == 0:
        return {
            "team_size": 0,
            "Std_EI": 0, "Std_NS": 0, "Std_TF": 0, "Std_JP": 0,
            "#Lideres_ENTJ_ESTP": 0,
            "#TiposUnicosMBTI": 0
        }

    E_count = sum(m.startswith("E") for m in subdf["MBTI"])
    I_count = total - E_count
    S_count = sum(m[1] == "S" for m in subdf["MBTI"])
    N_count = total - S_count
    T_count = sum(m[2] == "T" for m in subdf["MBTI"])
    F_count = total - T_count
    J_count = sum(m[3] == "J" for m in subdf["MBTI"])
    P_count = total - J_count

    props = {
        'E':E_count/total, 'I':I_count/total,
        'S':S_count/total, 'N':N_count/total,
        'T':T_count/total, 'F':F_count/total,
        'J':J_count/total, 'P':P_count/total,
    }

    return {
        "team_size": total,
        "Std_EI": statistics.pstdev([props['E'], props['I']]),
        "Std_NS": statistics.pstdev([props['S'], props['N']]),
        "Std_TF": statistics.pstdev([props['T'], props['F']]),
        "Std_JP": statistics.pstdev([props['J'], props['P']]),
        "#Lideres_ENTJ_ESTP": sum(m in ["ENTJ", "ESTP"] for m in subdf["MBTI"]),
        "#TiposUnicosMBTI": subdf["MBTI"].nunique()
    }

# -------------------------
# Agregación TREO
# -------------------------
def treo_agg(subdf):
    roles = ["Organizer", "Doer", "Challenger", "Innovator", "TeamBuilder", "Connector"]
    out = {}
    for r in roles:
        out[f"Avg_{r}"] = subdf[r].mean()
        out[f"Std_{r}"] = subdf[r].std()
    out["#High_Organizer"] = (subdf["Organizer"] > 4).sum()
    out["#High_Doer"] = (subdf["Doer"] > 4).sum()
    out["#High_TB"] = (subdf["TeamBuilder"] > 4).sum()
    return out

# -------------------------
# Agregación Coevaluación
# -------------------------
def co_eval_agg(subdf):
    c_cols = ["Commitment", "Communication", "Motivation", "GoalSetting",
              "DiversityPerception", "EmotionalIntelligence", "Trust",
              "WorkSatisfaction", "Autonomy", "ProcessIndicator"]
    return {f"{c}_mean": subdf[c].mean() for c in c_cols}
