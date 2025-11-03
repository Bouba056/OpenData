# ================================================================
# 🏠 Application Open Data Logement (Gard & Hérault)
# ================================================================

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

# ------------------------------------------------
# ⚙️ CONFIGURATION
# ------------------------------------------------
st.set_page_config(page_title="Open Data Logement", layout="wide")

# ------------------------------------------------
# 📂 IMPORT SIMPLE DES DONNÉES
# ------------------------------------------------
st.sidebar.success("✅ Données chargées")

# Chemins des fichiers
gdf_path = "DATA/communes_30_34_with_cc_2022.geojson"
df_path = "SORTIE/Compil_clean.csv"

# Chargement direct
gdf = gpd.read_file(gdf_path)
df_hist = pd.read_csv(df_path)

# ------------------------------------------------
# 🧭 ONGLET PRINCIPAL
# ------------------------------------------------
st.title("🏠 Application Open Data Logement")
st.markdown("Explorez les données de logement pour le **Gard (30)** et **l’Hérault (34)** de 2013 à 2022.")

# Création des onglets
tab1, tab2, tab3 = st.tabs(["🏡 Accueil", "🗺️ Cartographie", "📊 Analyse"])

# ------------------------------------------------
# 🏡 ONGLET 1 : ACCUEIL
# ------------------------------------------------
with tab1:
    st.header("Bienvenue 👋")
    st.write("""
    Cette application permet d'explorer les données de **logement** issues de l'Open Data.
    
    Vous trouverez :
    - Une **cartographie interactive** des communes du Gard et de l’Hérault ;
    - Une **analyse temporelle** des indicateurs logement par commune.
    """)


# ------------------------------------------------
# 🗺️ ONGLET 2 : CARTOGRAPHIE
# ------------------------------------------------
with tab2:
    st.header("🗺️ Cartographie interactive")

    # Liste automatique des colonnes numériques
    numeric_columns = [col for col in gdf.columns if gdf[col].dtype in ["float64", "int64"]]

    # Choix de la variable à afficher
    variable = st.selectbox(
        "Choisis une variable à afficher :",
        numeric_columns,
        index=numeric_columns.index("LOG") if "LOG" in numeric_columns else 0
    )

    # Création de la carte Folium
    m = folium.Map(location=[43.8, 4.2], zoom_start=8, tiles="cartodbpositron")

    # Fonction de style basée sur la variable choisie
    def style_function(feat):
        value = feat["properties"].get(variable, 0)
        # dégradé simple de bleu selon la valeur
        if value is None:
            color = "#cccccc"
        elif value < gdf[variable].quantile(0.33):
            color = "#a6cee3"
        elif value < gdf[variable].quantile(0.66):
            color = "#1f78b4"
        else:
            color = "#08306b"
        return {
            "fillColor": color,
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.7,
        }

    # Ajout du GeoJSON avec info-bulle
    folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=["insee_com", "Unemployment"],
    nan_fill_color="purple",
    nan_fill_opacity=0.4,
    key_on="feature.insee_com",
    fill_color="YlGn",
    ).add_to(m)

    # Affichage de la carte
    st_folium(m, width=1200, height=700)



# ------------------------------------------------
# 📊 ONGLET 3 : ANALYSE
# ------------------------------------------------
with tab3:
    st.header("📊 Analyse par commune")

    commune = st.selectbox("Sélectionnez une commune :", sorted(df_hist["LIBGEO"].unique()))
    data_commune = df_hist[df_hist["LIBGEO"] == commune]

    st.subheader(f"Évolution historique de la commune : {commune}")

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        ax.bar(data_commune["AN"], data_commune["LOG"], color="#4C72B0")
        ax.set_title("Nombre total de logements")
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        ax.bar(data_commune["AN"], data_commune["RP"], color="#55A868")
        ax.set_title("Résidences principales")
        st.pyplot(fig)

    col3, col4 = st.columns(2)
    with col3:
        fig, ax = plt.subplots()
        ax.bar(data_commune["AN"], data_commune["LOGVAC"], color="#C44E52")
        ax.set_title("Logements vacants")
        st.pyplot(fig)

    with col4:
        fig, ax = plt.subplots()
        ax.bar(data_commune["AN"], data_commune["RSECOCC"], color="#8172B3")
        ax.set_title("Résidences secondaires")
        st.pyplot(fig)
