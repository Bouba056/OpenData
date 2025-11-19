# ================================================================
# 🤖 Module ML simplifié - Analyse intelligente du logement
# ================================================================
# Seulement les fonctionnalités les plus pertinentes et simples

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import streamlit as st

# ------------------------------------------------
# 1. PROFILS DE COMMUNES (Clustering simple)
# ------------------------------------------------
@st.cache_data
def identifier_profils_communes(data, n_profils=4):
    """
    Regroupe les communes en profils similaires
    Retourne : données avec profils + descriptions
    """
    # Calculer le % de maisons si pas déjà présent
    data_work = data.copy()
    if 'Plog_MAISON' not in data_work.columns:
        data_work['Plog_MAISON'] = (data_work['MAISON'] / data_work['LOG']) * 100
    
    # Variables clés simples à comprendre
    features = [
        'Plog_RP',      # % résidences principales
        'Plog_RS',      # % résidences secondaires  
        'Plog_VAC',     # % logements vacants
        'Prp_RP_PROP',  # % propriétaires
        'Plog_MAISON'   # % maisons
    ]
    
    # Préparation des données
    X = data_work[features].fillna(0)
    
    # Normalisation (pour comparer des pommes avec des pommes)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Clustering K-Means (optimisé pour la rapidité)
    kmeans = KMeans(n_clusters=n_profils, random_state=42, n_init=3, max_iter=100)
    profils = kmeans.fit_predict(X_scaled)
    
    # Ajout des profils
    data_profils = data_work.copy()
    data_profils['Profil'] = profils
    
    # Donner des noms compréhensibles aux profils
    noms_profils = {}
    for profil_id in range(n_profils):
        stats = data_profils[data_profils['Profil'] == profil_id][features].mean()
        
        # Logique simple de nommage
        if stats['Plog_RS'] > 25:
            nom = "Profil touristique"
            desc = f"Forte présence de résidences secondaires ({stats['Plog_RS']:.1f}%)"
        elif stats['Plog_VAC'] > 12:
            nom = "Profil sous-tension"
            desc = f"Taux de vacance important ({stats['Plog_VAC']:.1f}%)"
        elif stats['Prp_RP_PROP'] > 70 and stats['Plog_MAISON'] > 75:
            nom = "Profil résidentiel pavillonnaire"
            desc = f"Propriétaires en maison ({stats['Prp_RP_PROP']:.1f}% proprio)"
        else:
            nom = f"Profil mixte équilibré"
            desc = "Profil diversifié"
        
        noms_profils[profil_id] = {'nom': nom, 'description': desc}
    
    # Ajouter les noms lisibles
    data_profils['Nom_Profil'] = data_profils['Profil'].map(lambda x: noms_profils[x]['nom'])
    
    return data_profils, noms_profils

# ------------------------------------------------
# 2. SCORE DE TENSION IMMOBILIÈRE (0-100)
# ------------------------------------------------
@st.cache_data
def calculer_tension_immobiliere(data):
    """
    Calcule un score simple de 0 à 100
    100 = marché très tendu (peu de vacance, forte demande)
    0 = marché détendu (beaucoup de vacance)
    """
    data_tension = data.copy()
    
    # 3 indicateurs simples
    # 1. Vacance (moins de vacance = plus de tension)
    tension_vacance = 100 - data_tension['Plog_VAC'] * 5  # On inverse
    tension_vacance = tension_vacance.clip(0, 100)
    
    # 2. Résidences secondaires (si élevé, retire du marché = tension)
    tension_rs = data_tension['Plog_RS'] * 2
    tension_rs = tension_rs.clip(0, 100)
    
    # 3. Propriétaires (marché stable mais peu liquide)
    tension_proprio = data_tension['Prp_RP_PROP'] * 0.5
    tension_proprio = tension_proprio.clip(0, 100)
    
    # Score final (moyenne pondérée)
    data_tension['Score_Tension'] = (
        tension_vacance * 0.5 +      # 50% du poids sur la vacance
        tension_rs * 0.3 +            # 30% sur les rés. secondaires
        tension_proprio * 0.2         # 20% sur les propriétaires
    )
    
    # Arrondir pour simplifier
    data_tension['Score_Tension'] = data_tension['Score_Tension'].round(1)
    
    # Catégories simples
    data_tension['Niveau'] = pd.cut(
        data_tension['Score_Tension'],
        bins=[0, 30, 60, 80, 100],
        labels=['🟢 Faible', '🟡 Modérée', '🟠 Élevée', '🔴 Très élevée'],
        include_lowest=True
    )
    
    return data_tension

# ------------------------------------------------
# 3. PRÉDICTION SIMPLE (Tendance linéaire)
# ------------------------------------------------
@st.cache_data
def predire_evolution_logements(historical_data, commune, annees_futures=3):
    """
    Prédit l'évolution du nombre de logements
    Méthode : régression linéaire simple (tendance)
    """
    # Filtrer sur la commune
    commune_data = historical_data[historical_data['LIBGEO'] == commune].copy()
    
    if len(commune_data) < 3:
        return None, "Pas assez de données historiques"
    
    # Trier par année
    commune_data = commune_data.sort_values('AN')
    
    # Régression linéaire simple
    X = commune_data['AN'].values
    y = commune_data['LOG'].values
    
    # Calculer la pente (croissance annuelle moyenne)
    n = len(X)
    mean_x = X.mean()
    mean_y = y.mean()
    
    # Formule de la pente
    pente = ((X - mean_x) * (y - mean_y)).sum() / ((X - mean_x) ** 2).sum()
    intercept = mean_y - pente * mean_x
    
    # Prédictions futures
    annees_pred = np.arange(X.max() + 1, X.max() + annees_futures + 1)
    logements_pred = pente * annees_pred + intercept
    
    # Créer dataframe résultat
    predictions = pd.DataFrame({
        'Année': np.concatenate([X, annees_pred]),
        'Logements': np.concatenate([y, logements_pred]),
        'Type': ['Historique'] * len(X) + ['Prédiction'] * len(annees_pred)
    })
    
    # Calculer la croissance annuelle moyenne en %
    croissance_annuelle = (pente / mean_y) * 100
    
    return predictions, croissance_annuelle

# ------------------------------------------------
# 4. FONCTION HELPER : Statistiques du profil
# ------------------------------------------------
def get_stats_profil(data, profil_id):
    """
    Retourne les stats moyennes d'un profil
    """
    profil_data = data[data['Profil'] == profil_id]
    
    stats = {
        'nb_communes': len(profil_data),
        'pct_rs_moyen': profil_data['Plog_RS'].mean(),
        'pct_vac_moyen': profil_data['Plog_VAC'].mean(),
        'pct_proprio_moyen': profil_data['Prp_RP_PROP'].mean(),
        'pct_maison_moyen': profil_data['Plog_MAISON'].mean()
    }
    
    return stats
