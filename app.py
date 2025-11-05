# ================================================================
# (logo ?? a voir) Application Open Data Logement (Gard & Hérault)
# ================================================================
# lanceur : py -m streamlit run app.py 
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

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
#df_path = "SORTIE/Compil_clean.csv"

# Chargement direct
gdf = gpd.read_file(gdf_path)

gdf = gdf.set_crs(epsg=2154, allow_override=True).to_crs(epsg=4326)  # iMPORTANT SINON LA CARTE NE MARCHE PAS 
data_carto = pd.read_csv(data_carto_path)
#df_hist = pd.read_csv(df_path)


datahab = pd.read_csv("SORTIE/TAB_TYPEHAB.csv")
datacate = pd.read_csv("SORTIE/TAB_CATEHAB.csv")

dataso = pd.read_csv("SORTIE/RP_SO.csv")
dataty = pd.read_csv("SORTIE/RP_TYPO.csv")

# ------------------------------------------------
# 🧭 ONGLET PRINCIPAL
# ------------------------------------------------
st.title("(logo ? a voir) Application Open Data Logement")
st.markdown("Explorez les données de logement pour le **Gard (30)** et **l’Hérault (34)** de 2013 à 2022.")

# Création des onglets
tab1, tab2, tab3 = st.tabs(["🏡 Accueil", "🗺️ Cartographie", "📊 Analyse"])

# ------------------------------------------------
# 🏡 ONGLET 1 : ACCUEIL
# ------------------------------------------------
with tab1:
    st.header("Bienvenue !...")
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
        
        st.markdown("Sélectionnez une variable à afficher sur la carte :")
        variable = st.radio(
            "Variable à afficher",
            # ["Plog_RP", "Plog_RS", "Plog_VAC", "Plog_RP_LOCHLM", "Plog_RP_LOCPRIV","Prp_RP_LOCHLM", "Prp_RP_LOCPRIV"], # contenus dans data_carto
            ["LOG", "RP", "RSECOCC", "LOGVAC"],
            index=0,
            horizontal=False,
            label_visibility="collapsed"
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
        center = gdf.geometry.union_all().centroid
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

    commune = st.selectbox("Sélectionnez une commune :", sorted(datahab["LIBGEO"].unique()))
    

    st.subheader(f"Évolution historique de la commune : {commune}")

    col1, col2 = st.columns(2)
    with col1:
        datahab2 = datahab[datahab["LIBGEO"] == commune]
        
        fig = px.bar(
        datahab2,
        x="AN",          # ton année
        y="NOMBRE",
        barmode="stack",
        color="TYPE_HABITAT",   # empilement par type
        title=f"Évolution des logements du parc selon le type de l'habitat<br><sup>Commune : {commune}",
        color_discrete_sequence=["#4C72B0", "#C44E52"],  # couleurs perso
        labels={
            "AN": "Année",
            "NOMBRE": "Nombre de logements",
            "TYPE_HABITAT": "Type d'habitat"
            }
         )   

        # --- Ajouter la ligne du total ---
        # On calcule le total LOG pour chaque année
        totaux = datahab2.groupby("AN", as_index=False)["LOG"].first()  # ou sum() si répétitions

        fig.add_trace(
            go.Scatter(
                x=totaux["AN"],
                y=totaux["LOG"],
                mode="lines+markers+text",
                text=[f"{int(v):,}".replace(",", " ") for v in totaux["LOG"]],
                textposition="top center",
                name="Total logements",
                line=dict(color="black", width=2),
                marker=dict(size=6)
            )
        )

        # --- Personnalisation générale ---
        fig.update_layout(
            template="plotly_white",
            barcornerradius=15,
            
            legend_title_text="Type d'habitat"
        )

        # --- Affichage Streamlit ---
        st.plotly_chart(fig, use_container_width=True)


    with col2:
        dataso2 = dataso[dataso["LIBGEO"] == commune]
        dataso2=dataso2[(dataso2["AN"]==2022)]
        
        fig2 = px.pie(
            dataso2,
            values="NOMBRE", 
            names="STATUT",
            title=f"Répartition des résidences principales selon la catégorie<br><sup>Commune : {commune}",
            color_discrete_sequence=px.colors.sequential.RdBu
         )   
        


        # --- Personnalisation générale ---
        fig2.update_layout(
            template="plotly_white",
            barcornerradius=15,
            legend_title_text="Type d'habitat"
        )

        # --- Affichage Streamlit ---
        st.plotly_chart(fig2, use_container_width=True)





    col3, col4 = st.columns(2)
    with col3:
        datacate2 = datacate[datacate["LIBGEO"] == commune]
        
        fig3 = px.area(
            datacate2,
            x="AN",
            y="NOMBRE",
            color="TYPE_LOG",
            title=f"Évolution de la répartition des logements selon leur catégorie<br><sup>Commune : {commune}",
            color_discrete_sequence=["#4C72B0", "#C44E52", "#85B31A"],
            labels={
                "AN": "Année",
                "NOMBRE": "Nombre de logements",
                "TYPE_LOG": "Catégorie de l'habitat"
            }
        )

        fig3.update_layout(
            template="plotly_white",
            legend_title_text="Catégorie de logement",
            hovermode="x unified"  # joli survol groupé
        )

        st.plotly_chart(fig3, use_container_width=True)




    with col4:
        dataty2 = dataty[dataty["LIBGEO"] == commune]
        dataty2 =dataty2 [(dataty2 ["AN"]==2022)]
        
        fig4 = px.bar(
            dataty2,
            x="NOMBRE", 
            y="TYPO",
            orientation = "h",
            title=f"Répartition des résidences principales selon leur typologie<br><sup>Commune : {commune}"
         )   
        


        # --- Personnalisation générale ---
        fig4.update_layout(
            
            template="plotly_white",
            barcornerradius=15
        )

        # --- Affichage Streamlit ---
        st.plotly_chart(fig4, use_container_width=True)