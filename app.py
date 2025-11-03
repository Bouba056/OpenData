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
data_carto_path = "SORTIE/data_clean_2022.csv"
df_path = "SORTIE/Compil_clean.csv"

# Chargement direct
gdf = gpd.read_file(gdf_path)

gdf = gdf.set_crs(epsg=2154, allow_override=True).to_crs(epsg=4326)
data_carto = pd.read_csv(data_carto_path)
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

    # -----------------------------
    # 🧭 Layout : deux colonnes
    # -----------------------------
    col_left, col_right = st.columns([1, 3])

    with col_left:
        st.subheader("🧩 Variables disponibles")
        st.markdown("Sélectionnez une variable à afficher sur la carte :")
        variable = st.radio(
            "",
            ["LOG", "RP", "RSECOCC", "LOGVAC"],
            index=0,
            horizontal=False
        )
        st.markdown(
            f"📊 **Variable sélectionnée :** `{variable}`",
            help="Choisissez un indicateur à cartographier."
        )

    with col_right:
        # -----------------------------
        # 🗺️ Préparation des données
        # -----------------------------
        gdf[variable] = pd.to_numeric(gdf[variable], errors="coerce")

        # Calcul du centre géographique pour centrer la carte
        center = gdf.geometry.unary_union.centroid
        lat, lon = center.y, center.x

        # -----------------------------
        # 🎨 Carte Folium stylisée
        # -----------------------------
        m = folium.Map(
            location=[lat, lon],
            zoom_start=9,
            tiles="cartodbpositron",
            min_zoom=8,
            max_zoom=10,
            max_bounds=True
        )

        # Couche choroplèthe colorée
        folium.Choropleth(
            geo_data=gdf.__geo_interface__,
            data=gdf,
            columns=["insee_com", variable],
            key_on="feature.properties.insee_com",
            fill_color="YlOrRd",  # 🔥 palette plus vive
            fill_opacity=0.85,
            line_opacity=0.4,
            legend_name=f"{variable} (valeurs relatives)"
        ).add_to(m)

        # Contours + infobulle personnalisée
        folium.GeoJson(
            gdf,
            name="Communes",
            style_function=lambda x: {
                "fillColor": "transparent",
                "color": "black",
                "weight": 0.5,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["LIBGEO", variable],
                aliases=["🏙️ Commune :", f"📈 {variable} :"],
                localize=True,
                sticky=True,
                labels=True,
                style=(
                    "background-color: white; color: #333; "
                    "font-family: Arial; font-size: 13px; padding: 6px; "
                    "border-radius: 5px;"
                ),
            ),
        ).add_to(m)

        # Titre visuel
        st.markdown(
            f"<h4 style='text-align:center;'>Carte de la variable <span style='color:#ff5733'>{variable}</span></h4>",
            unsafe_allow_html=True,
        )

        # Affichage de la carte
        st_folium(m, width=900, height=600)

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
