# ================================================================
# 🤖 MODULE ML — Version robuste et professionnelle (2025)
# ================================================================
# Ce module regroupe :
# 1. Clustering automatique optimisé (Silhouette + KMeans)
# 2. Score de tension immobilière basé sur PCA + pondération
# 3. Prédiction du nombre de logements (linéaire / exponentielle)
# ================================================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from scipy.optimize import curve_fit
import streamlit as st


# =================================================================
# 🔵 1) CLUSTERING — Profils de communes
# =================================================================

@st.cache_data
def identifier_profils_communes(data, k_max=5):
    """
    Clustering automatique basé sur KMeans + Silhouette.
    """
    
    df = data.copy().fillna(0)

    # ======= AJOUT ESSENTIEL POUR TON CAS =======
    # =============================================

    variables = [
        "Plog_RP",
        "Plog_RS",
        "Plog_VAC",
        "Plog_MAISON",
        "Plog_APPART"
    ]

    df = data.copy().fillna(0)
    df["Plog_MAISON"] = (df["MAISON"] / df["LOG"]) * 100
    df["Plog_APPART"] = (df["APPART"] / df["LOG"]) * 100

    X = df[variables]

    # Normalisation
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Sélection automatique du meilleur nombre de clusters (2 → k_max)
    best_k = 2
    best_sil = -1

    for k in range(2, k_max + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(X_scaled)
        sil = silhouette_score(X_scaled, labels)
        if sil > best_sil:
            best_sil = sil
            best_k = k

    # Clustering final
    final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    profils = final.fit_predict(X_scaled)

    df["Profil"] = profils

    global_means = df[variables].mean()

    label_for_var = {
        "Plog_RP": "Résidences principales",
        "Plog_RS": "Résidences secondaires",
        "Plog_VAC": "Vacance",
        "Plog_MAISON": "Part de maisons",
        "Plog_APPART": "Part d'appartements",
    }

    label_for_name = {
        "Plog_RP": ("résidences principales élevées", "résidences principales faibles"),
        "Plog_RS": ("résidences secondaires élevées", "peu de résidences secondaires"),
        "Plog_VAC": ("vacance marquée", "vacance limitée"),
        "Plog_MAISON": ("dominance des maisons", "faible part de maisons"),
        "Plog_APPART": ("dominance des appartements", "faible part d'appartements"),
    }

    descriptions = {}
    total_communes = len(df)

    for p in range(best_k):
        sous_df = df[df["Profil"] == p]
        stats = sous_df[variables].mean()

        deltas = {var: stats[var] - global_means[var] for var in variables}
        insights = []

        part = (len(sous_df) / total_communes) * 100 if total_communes else 0
        insights.append(f"{len(sous_df)} communes ({part:.1f}% de l'échantillon)")

        for var, label in label_for_var.items():
            delta = deltas[var]
            if np.isnan(delta):
                continue
            if delta >= 5:
                insights.append(f"{label} supérieures à la moyenne ({stats[var]:.1f}% ; {delta:.1f} pts)")
            elif delta <= -5:
                insights.append(f"{label} inférieures à la moyenne ({stats[var]:.1f}% ; {delta:.1f} pts)")

        if "DEP" in sous_df.columns:
            deps = sous_df["DEP"].astype(str).value_counts().head(2)
            if not deps.empty:
                dep_txt = ", ".join([
                    f"{dep} ({count / len(sous_df) * 100:.0f}%".rstrip("0").rstrip(".") + "%)"
                    for dep, count in deps.items()
                ])
                insights.append(f"Répartition des départements : {dep_txt}")

        significant_deltas = sorted(deltas.items(), key=lambda kv: abs(kv[1]), reverse=True)
        suffix = "profil équilibré"
        for var, delta in significant_deltas:
            if abs(delta) >= 3:
                name_options = label_for_name.get(var)
                if name_options:
                    suffix = name_options[0] if delta >= 0 else name_options[1]
                    break

        if suffix == "profil équilibré":
            profil_name = f"Profil {p+1}"
        else:
            profil_name = f"Profil {p+1} – {suffix}"

        detail_points = [txt for txt in insights[1:] if "%" in txt]
        description = " • ".join(detail_points[:2]) if detail_points else "Profil équilibré"

        descriptions[p] = {
            "nom": profil_name,
            "description": description,
            "insights": insights[:5]
        }

    df["Nom_Profil"] = df["Profil"].map(lambda x: descriptions[x]["nom"])

    return df, descriptions


# =================================================================
# 🔵 2) SCORE DE TENSION IMMOBILIÈRE (Méthode PCA pondérée)
# =================================================================

@st.cache_data
def calculer_tension_immobiliere(data):
    """
    Score de tension robuste basé sur :
    - Standardisation
    - PCA pour pondérer objectivement les variables
    - Score normalisé entre 0 et 100

    Variables utilisées :
        - Vacance (%)
        - Résidences secondaires (%)
        - Propriétaires (%)

    Retourne DF avec Score_Tension et Niveau.
    """

    df = data.copy().fillna(0)
    variables = ["Plog_VAC", "Plog_RS", "Prp_RP_PROP"]

    X = df[variables]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA pour pondération objective
    pca = PCA(n_components=1)
    composante = pca.fit_transform(X_scaled).flatten()

    # Normalisation en score 0-100
    score = (composante - composante.min()) / (composante.max() - composante.min())
    score = score * 100

    df["Score_Tension"] = score.round(1)

    df["Niveau"] = pd.cut(
        df["Score_Tension"],
        bins=[0, 25, 50, 75, 100],
        labels=["🟢 Faible", "🟡 Modérée", "🟠 Élevée", "🔴 Très élevée"],
        include_lowest=True
    )

    return df


# =================================================================
# 🔵 3) PRÉDICTION DU PARC — Linéaire ou exponentielle
# =================================================================

def _exp_model(x, a, b):
    """Modèle exponentiel simple : y = a * exp(bx)"""
    return a * np.exp(b * x)


@st.cache_data
def predire_evolution_logements(data, commune, annees_futures=3):
    """
    Prédit le nombre de logements d'une commune via :
    - Régression linéaire
    - Régression exponentielle
    Sélection automatique du meilleur modèle selon le RMSE.

    Retour :
      predictions (DataFrame)
      croissance annuelle (%)
    """

    df = data[data["LIBGEO"] == commune].sort_values("AN")
    if len(df) < 3:
        return None, None

    X = df["AN"].values
    y = df["LOG"].values
    X_reshape = X.reshape(-1, 1)

    # -------------------------
    # 🔹 Modèle LINÉAIRE
    # -------------------------
    lin = LinearRegression()
    lin.fit(X_reshape, y)
    y_pred_lin = lin.predict(X_reshape)
    rmse_lin = np.sqrt(((y - y_pred_lin) ** 2).mean())

    # -------------------------
    # 🔹 Modèle EXPONENTIEL
    # -------------------------
    try:
        params, _ = curve_fit(_exp_model, X, y, maxfev=10000)
        y_pred_exp = _exp_model(X, params[0], params[1])
        rmse_exp = np.sqrt(((y - y_pred_exp) ** 2).mean())
    except:
        rmse_exp = np.inf

    # -------------------------
    # 🔹 CHOIX AUTOMATIQUE
    # -------------------------
    if rmse_lin <= rmse_exp:
        model_used = "linéaire"
        future_years = np.arange(X.max() + 1, X.max() + annees_futures + 1)
        future_pred = lin.predict(future_years.reshape(-1, 1))
    else:
        model_used = "exponentiel"
        future_years = np.arange(X.max() + 1, X.max() + annees_futures + 1)
        future_pred = _exp_model(future_years, params[0], params[1])

    # -------------------------
    # 🔹 DATAFRAME FINAL
    # -------------------------
    df_hist = pd.DataFrame({
        "Année": X,
        "Logements": y,
        "Type": "Historique"
    })

    df_pred = pd.DataFrame({
        "Année": future_years,
        "Logements": future_pred,
        "Type": "Prédiction"
    })

    full = pd.concat([df_hist, df_pred], ignore_index=True)
    croissance = ((future_pred[-1] - y[-1]) / y[-1]) * 100 / annees_futures

    return full, croissance



def get_stats_profil(df, profil_id):
    """
    Retourne les statistiques simples d'un profil :
    - nombre de communes
    - moyenne LOG, RP, VAC, etc.
    """
    subset = df[df["Profil"] == profil_id]

    return {
        "count": len(subset),
        "log_mean": subset["LOG"].mean(),
        "rp_mean": subset["RP"].mean(),
        "vac_mean": subset["LOGVAC"].mean()
    }
