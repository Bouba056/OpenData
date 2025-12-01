# ================================================================
# Application Open Data Logement (Gard & Hérault)
# ================================================================
# lanceur : streamlit run app.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import json as json
import pydeck as pdk
import numpy as np
import branca.colormap as cm
import plotly.io as pio
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import ml_models as ml  # Module ML



# Optimisation : Cache pour accélérer le chargement
@st.cache_data
def load_geojson(path):
    gdf = gpd.read_file(path)
    return gdf.set_crs(epsg=2154, allow_override=True).to_crs(epsg=4326)



@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

# ------------------------------------------------
# ⚙️ CONFIGURATION
# ------------------------------------------------
st.set_page_config(page_title="Open Data Logement", layout="wide")

# Style CSS personnalisé 
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .main { background: linear-gradient(135deg, #f5eee0 0%, #ecdaa2 100%); }

    .header-container {
    background: linear-gradient(135deg, #e8a87c 0%, #d17842 100%);
    padding: 40px 20px;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(209, 120, 66, 0.3);
    margin-bottom: 30px;
    transition: all 0.3s ease;
    }
    .header-container:hover {
    background: linear-gradient(135deg, #f0b68c 0%, #e08850 100%);
    box-shadow: 0 10px 40px rgba(209, 120, 66, 0.4);
    }
    
    .main-title { text-align: center; color: #fff; font-size: 42px; font-weight: 700; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .subtitle { text-align: center; color: #f9f3e8; font-size: 18px; margin-bottom: 10px; }
    
    h2, h3, h4 { color: #8b5e3c; font-weight: 600; }
    .info-card {
    background: linear-gradient(135deg, #faf6ef 0%, #f5eee0 100%);
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(139, 94, 60, 0.15);
    margin: 15px 0;
    border-left: 4px solid #d17842;
    transition: all 0.3s ease;
    }
    .info-card:hover { box-shadow: 0 6px 20px rgba(139, 94, 60, 0.25); transform: translateY(-2px); background: linear-gradient(135deg, #fff 0%, #f9f3e8 100%); }
    
    div[data-baseweb="tab-list"] {
    justify-content: center;
    gap: 15px !important;
    background: linear-gradient(135deg, #faf6ef 0%, #ecdaa2 100%);
    padding: 15px 20px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(139, 94, 60, 0.15);
    margin-bottom: 20px;
    }
    button[data-baseweb="tab"] {
    background: linear-gradient(135deg, #f5eee0 0%, #ecdaa2 100%);
    color: #8b5e3c; border-radius: 10px; padding: 12px 35px; font-size: 16px; font-weight: 600; border: 2px solid transparent;
    transition: all 0.3s ease; box-shadow: 0 2px 8px rgba(139, 94, 60, 0.1);
    }
    button[data-baseweb="tab"]:hover { background: linear-gradient(135deg, #ecdaa2 0%, #e0c896 100%); transform: translateY(-3px); box-shadow: 0 4px 12px rgba(139, 94, 60, 0.2); border: 2px solid #d17842; }
    button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #e8a87c 0%, #d17842 100%); color: white; box-shadow: 0 6px 20px rgba(209, 120, 66, 0.4); transform: translateY(-3px); border: 2px solid #c06838;
  }
  hr { border: none; height: 2px; background: linear-gradient(90deg, transparent, #d17842, transparent); margin: 25px 0; }
  
  .sidebar-title {
  color: #8b5e3c; font-size: 14px; font-weight: 600; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid #d17842;
  }
  
  .dataframe { border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(139, 94, 60, 0.1); }
  .stSelectbox > div > div { background: linear-gradient(135deg, #faf6ef 0%, #ecdaa2 100%); border: 2px solid #d17842; border-radius: 8px; }
  </style>
  """,
    unsafe_allow_html=True
)



# ------------------------------------------------
# IMPORT OPTIMISÉ DES DONNÉES avec cache
# ------------------------------------------------
gdf = load_geojson("DATA/communes_30_34_with_cc_2022.geojson")
data_carto = load_csv("SORTIE/data_clean_2022.csv")
datahab = load_csv("SORTIE/TAB_TYPEHAB.csv")
datacate = load_csv("SORTIE/TAB_CATEHAB.csv")
dataso = load_csv("SORTIE/RP_SO.csv")
dataty = load_csv("SORTIE/RP_TYPO.csv")

# ------------------------------------------------
# EN-TÊTE DE L'APPLICATION
# ------------------------------------------------
st.markdown("""
    <div class='header-container'>
        <h1 class='main-title'>Tableau de bord du parc de logement</h1>
        <p class='subtitle'>Gard (30) et Hérault (34) — Données 2013 à 2022</p>
    </div>
""", unsafe_allow_html=True)

# Création des onglets
tab1, tab2, tab3, tab4 = st.tabs(["🛖Accueil", "🌍 Cartographie", "📈 Analyse", "🧠 Intelligence Territoriale"])

# ------------------------------------------------
# ONGLET 1 : ACCUEIL
# ------------------------------------------------
with tab1:
    # Titre principal
    st.markdown(
        "<h2 style='text-align:center; color:#8b5e3c;'>Projet open data et web des données</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#8b5e3c; font-size:17px;'>"
        "Une application interactive pour explorer l'évolution du parc de logements "
        "dans les départements du <b>Gard (30)</b> et de <b>l'Hérault (34)</b>."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    

    #  Présentation générale
    st.markdown("<div class='info-card'><h3 style='color: #d17842; margin-top: 0;'>Objectif de l’application</h3>"
                "<p style='line-height: 1.8; color: #8b5e3c;'>Cette application a pour but de faciliter la <strong>visualisation</strong>, la <strong>comparaison</strong> et l’<strong>analyse temporelle</strong> des indicateurs liés au logements dans les communes du Gard et de l’Hérault. Elle met à disposition :"
                "</p><ul style='line-height: 1.8; color: #8b5e3c;'>"
                "<li>Une cartographie interactive des indicateurs (parts de résidences principales, logements vacants, etc.);</li>"
                "<li>Une analyse temporelle de l’évolution du parc par commune ;</li>"
                "<li>Des graphiques interactifs permettant d’explorer la composition du parc de logements ;</li></ul>"
                "</div>", unsafe_allow_html=True)
    
    # Source des données et traitement
    st.markdown("""
    <div class='info-card'>
        <h3 style='color: #d17842; margin-top: 0;'>Source et traitement des données</h3>
        <p style='line-height: 1.8; color: #8b5e3c;'>Les données proviennent des fichiers <strong>Insee</strong>,<strong> recensements de la population</strong> <strong>disponibles en Open Data.</strong></p>\nElles ont été retraitées pour :
        <ul style='line-height: 1.8; color: #8b5e3c;'>
            <li>Harmoniser les millésimes de 2013 à 2022 ;</li>
            <li>Calculer des indicateurs complémentaires (parts, taux, ratios...) ;</li>
            <li>Produire des jeux de données exploitables pour la visualisation.</li>
        </ul>
        <p style='line-height: 1.8; color: #8b5e3c;'>Les traitements ont été réalisés avec <strong>Python (pandas, geopandas)</strong> et les visualisations avec <strong>Streamlit</strong>, <strong>Plotly</strong> et <strong>Folium</strong>.</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='info-card'><h3 style='color: #d17842;'>Exemple de données utilisées</h3></div>", unsafe_allow_html=True)


    # Affichage d’un petit échantillon
    st.dataframe(
        data_carto.head(5).style.format(precision=1, thousands=" "),
        width='stretch'
    )

    # Légende explicative
    st.markdown("<div class='info-card'><h3 style='color: #d17842;'>Description des variables</h3></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: #faf6ef; padding: 20px; border-radius: 8px; border-left: 3px solid #d17842; margin-top: 15px;'>
        <p style='color: #8b5e3c; margin-bottom: 10px;'><em>Chaque ligne correspond à une commune et contient les indicateurs calculés pour l'année la plus récente (2022).</em></p>
        <p style='color: #8b5e3c; font-weight: 600; margin-bottom: 8px;'>Les principales variables sont :</p>
        <ul style='color: #8b5e3c; line-height: 1.8;'>
            <li><strong>LIBGEO</strong> : Nom de la commune;</li>
            <li><strong>DEP</strong> : Code du département (30 ou 34);</li>
            <li><strong>LOG, RP, RSECOCC, LOGVAC</strong> : Volumes de logements;</li>
            <li><strong>Plog_…, Prp_…</strong> : Indicateurs en pourcentage du parc total ou des résidences principales;</li>
        </ul>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Signature / contact
    st.markdown("""
  <div style='background: linear-gradient(135deg, #e8a87c 0%, #d17842 100%);
              padding: 30px; border-radius: 12px; margin-top: 40px;
              box-shadow: 0 4px 15px rgba(209, 120, 66, 0.3);'>
    <p style='text-align:center; color: white; font-size: 16px; margin: 0; line-height: 1.8;'>
      Développé dans le cadre du projet <strong>Open Data</strong> — Données INSEE, 2013–2022<br>
      Réalisation : <strong>Amadou Aboubacar, Ndiaye Ibrahima</strong><br>
      Master 2 MIASHS, Université Paul Valéry Montpellier
    </p>
  </div>
""", unsafe_allow_html=True)

    


# ------------------------------------------------
#  ONGLET 2 : CARTOGRAPHIE
# ------------------------------------------------


with tab2:
    # --- Préparation des données par département ---
    # Filtres département robustes (compatibles int/str)
    dep_str = data_carto['DEP'].astype(str)
    df_gard = data_carto[dep_str == "30"]
    df_herault = data_carto[dep_str == "34"]

    # --- Fonction pour générer la carte HTML double ---
    col1, col2, col3, col4, col5 = st.columns(5)

    # Fonction utilitaire pour créer une carte KPI
    def kpi_card(title, col_name):
        dep_str = data_carto["DEP"].astype(str)
        total_34 = data_carto.loc[dep_str == "34", col_name].sum()
        total_30 = data_carto.loc[dep_str == "30", col_name].sum()

        html = f"""
        <div style='text-align:center; background-color:#f9e8d8; border-radius:12px; 
                    padding:10px 5px; box-shadow:0px 2px 4px rgba(0,0,0,0.1);'>
            <h4 style='color:#8b5e3c; margin-bottom:8px;'>{title}</h4>
            <div style='display:flex; justify-content:space-around;'>
                <div style='flex:1;'>
                    <h3 style='color:#d17842; margin:0;'>{int(total_34):,}</h3>
                    <p style='color:#8b5e3c; font-size:13px; margin:0;'>Hérault (34)</p>
                </div>
                <div style='flex:1;'>
                    <h3 style='color:#d17842; margin:0;'>{int(total_30):,}</h3>
                    <p style='color:#8b5e3c; font-size:13px; margin:0;'>Gard (30)</p>
                </div>
            </div>
        </div>
        """
        st.markdown(html.replace(",", " "), unsafe_allow_html=True)

    # ------------------------------------------------
    # 🏘️ Lignes d'indicateurs
    # ------------------------------------------------
    with col1:
        total_com_34 = data_carto[data_carto["DEP"] == 34]["insee_com"].nunique()
        total_com_30 = data_carto[data_carto["DEP"] == 30]["insee_com"].nunique()
        html = f"""
        <div style='text-align:center; background-color:#f9e8d8; border-radius:12px; 
                    padding:10px 5px; box-shadow:0px 2px 4px rgba(0,0,0,0.1);'>
            <h4 style='color:#8b5e3c; margin-bottom:8px;'>Nombre de communes</h4>
            <div style='display:flex; justify-content:space-around;'>
                <div style='flex:1;'>
                    <h3 style='color:#d17842; margin:0;'>{total_com_34}</h3>
                    <p style='color:#8b5e3c; font-size:13px; margin:0;'>Hérault (34)</p>
                </div>
                <div style='flex:1;'>
                    <h3 style='color:#d17842; margin:0;'>{total_com_30}</h3>
                    <p style='color:#8b5e3c; font-size:13px; margin:0;'>Gard (30)</p>
                </div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    with col2:
        kpi_card("Logements totaux", "LOG")

    with col3:
        kpi_card("Résidences principales", "RP")

    with col4:
        kpi_card("Résidences secondaires", "RSECOCC")    

    with col5:
        kpi_card("Logements vacants", "LOGVAC")

    st.markdown("---")

# Layout : deux colonnes

    col_left, col_right = st.columns([3, 1], gap="small")
    with col_left:

        st.markdown("<h2 style='text-align:center; color:#8b5e3c;'>Cartographie interactive</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:left; color:#8b5e3c; margin-bottom: 20px;'>Sélectionnez et explorez les indicateurs de logement par commune</p>", unsafe_allow_html=True)

    with col_right:
        # --- NOUVEAU : Recherche de commune pour Zoom ---
        st.markdown("### Zoom sur une commune")
        
        # Correction : On enlève les valeurs nulles (.dropna()) avant de trier
        communes_propres = gdf["LIBGEO"].dropna().unique().tolist()
        
        # On crée la liste finale
        liste_communes = ["Aucune"] + sorted(communes_propres)
        
        selected_commune = st.selectbox("Sélectionnez pour mettre en évidence :", liste_communes)

    # Layout : deux colonnes
    col_left, col_right = st.columns([1, 3], gap="small")
    



    def reset_parc():
        st.session_state.radio_rp = None
        st.session_state.radio_loc = None
        st.session_state.selected_group = "parc"

    def reset_rp():
        st.session_state.radio_parc = None
        st.session_state.radio_loc = None
        st.session_state.selected_group = "rp"

    def reset_loc():
        st.session_state.radio_parc = None
        st.session_state.radio_rp = None
        st.session_state.selected_group = "loc"

    with col_left:
        
        # --- Initialisation de session pour un seul choix global ---
        if "selected_group" not in st.session_state:
            st.session_state.selected_group = "parc"

        # --- 1️) Part des catégories de logement dans tout le parc ---
        st.markdown("###### 🏠 Part des catégories de logement dans tout le parc")

        labels_parc = {
            "Plog_RP": "Part des résidences principales",
            "Plog_RS": "Part des résidences secondaires et occasionnelles",
            "Plog_VAC": "Part des logements vacants"
        }

        choice_parc = st.radio(
            "Variables (parc total)",
            options=list(labels_parc.values()),
            index=0 if st.session_state.selected_group == "parc" else None,
            horizontal=False,
            key="radio_parc",
            label_visibility="collapsed",
            on_change=reset_parc
        )


        if choice_parc:
            st.session_state.selected_group = "parc"

        st.markdown("---")

        # --- 2️) Part des catégories de résidences principales ---
        st.markdown("###### 🏡 Part des catégories de résidences principales dans tout le parc")

        labels_rp = {
            "Plog_RP_LOCHLM": "Part des résidences principales de type HLM",
            "Plog_RP_LOCPRIV": "Part des résidences principales de type privé"
        }

        choice_rp = st.radio(
            "Variables (résidences principales)",
            options=list(labels_rp.values()),
            index=0 if st.session_state.selected_group == "rp" else None,
            horizontal=False,
            key="radio_rp",
            label_visibility="collapsed",
            on_change=reset_rp
        )


        if choice_rp:
            st.session_state.selected_group = "rp"

        st.markdown("---")

        # --- 3️) Part des types de locatifs ---
        st.markdown("###### 🏘️ Part des types de locatifs (privé et public) dans les RP")

        labels_rpty = {
            "Prp_RP_LOCHLM": "Part des locatifs HLM dans les résidences principales",
            "Prp_RP_LOCPRIV": "Part des locatifs privés dans les résidences principales"
        }

        choice_loc = st.radio(
            "Variables (locatif)",
            options=list(labels_rpty.values()),
            index=0 if st.session_state.selected_group == "loc" else None,
            horizontal=False,
            key="radio_loc",
            label_visibility="collapsed",
            on_change=reset_loc
        )


        if choice_loc:
            st.session_state.selected_group = "loc"

        st.markdown("---")

        # --- Variable active ---
        variable = None
        if st.session_state.selected_group == "parc" and choice_parc:
            variable = {v: k for k, v in labels_parc.items()}[choice_parc]
        elif st.session_state.selected_group == "rp" and choice_rp:
            variable = {v: k for k, v in labels_rp.items()}[choice_rp]
        elif st.session_state.selected_group == "loc" and choice_loc:
            variable = {v: k for k, v in labels_rpty.items()}[choice_loc]

            

    with col_right:
        # -----------------------------
        # 1. Logique de Zoom & Centre (Conservée)
        # -----------------------------
        
        # Par défaut : Centre global
        center = gdf.geometry.union_all().centroid
        lat, lon = center.y, center.x
        zoom_level = 8 
        marker_data = None
        
        # Si une commune est sélectionnée, on ajuste la vue et on prépare la surbrillance
        if selected_commune != "Aucune":
            subset = gdf[gdf["LIBGEO"] == selected_commune]
            if not subset.empty:
                centroid = subset.geometry.centroid.iloc[0]
                lat, lon = centroid.y, centroid.x
                zoom_level = 6 # Zoom plus rapproché
                
                # Données pour le marqueur central
                marker_data = pd.DataFrame([{
                    "coordinates": [lon, lat],
                    "text": selected_commune
                }])

        # -----------------------------
        # 2. Préparation des Couleurs (Spécifique Pydeck)
        # -----------------------------
        
        min_val = gdf[variable].min()
        max_val = gdf[variable].max()
        
        def get_color_scale(val):
            # --- CORRECTION : Gestion des valeurs manquantes (NaN) ---
            if pd.isna(val): 
                return [200, 200, 200] # Gris clair pour les données manquantes
            
            # Normalisation entre 0 et 1
            if max_val == min_val: 
                norm = 0
            else: 
                norm = (val - min_val) / (max_val - min_val)
            
            # Sécurité : On s'assure que norm est bien entre 0 et 1
            norm = max(0, min(1, norm))
            
            # Interpolation simple : Jaune pale -> Rouge Foncé
            r = int(255 - (norm * (255 - 180)))
            g = int(255 - (norm * 255))
            b = int(200 - (norm * 200))
            return [r, g, b]

        # On applique la couleur
        gdf["fill_color"] = gdf[variable].apply(get_color_scale)

        # -----------------------------
        # 3. Configuration des Couches (Layers)
        # -----------------------------
        
        layers = []

        # A. Couche Principale (Choropleth)
        main_layer = pdk.Layer(
            "GeoJsonLayer",
            gdf,
            pickable=True,       # Permet le survol (tooltip)
            stroked=True,
            filled=True,
            extruded=False,      # Mettre à True pour la 3D
            wireframe=True,
            get_fill_color="fill_color", # On utilise la colonne calculée ci-dessus
            get_line_color=[50, 50, 50],
            get_line_width=70
        )
        layers.append(main_layer)

        # B. Couche de Sélection (Contour bleu vif)
        if selected_commune != "Aucune":
            highlight_geom = gdf[gdf["LIBGEO"] == selected_commune]
            if not highlight_geom.empty:
                highlight_layer = pdk.Layer(
                    "GeoJsonLayer",
                    data=highlight_geom,
                    stroked=True,
                    filled=False,
                    get_line_color=[57, 255, 20, 220], # Vert vif avec transparence
                    get_line_width=25 # Épaisseur en pixels
                    line_width_units='pixels'
                )
                layers.append(highlight_layer)

        # C. Couche Marqueur Central
        if marker_data is not None:
            marker_layer = pdk.Layer(
                'TextLayer',
                data=marker_data,
                get_position='coordinates',
                get_text='text',
                get_color=[0, 0, 0, 200],
                get_size=16,
                get_alignment_baseline="'bottom'",
            )
            layers.append(marker_layer)

        # -----------------------------
        # 4. Vue et Rendu
        # -----------------------------
        
        # Définition de la caméra
        view_state = pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=zoom_level,
            pitch=0, # Mettre à 45 pour une vue inclinée 3D
            bearing=0
        )

        # Tooltip (Infobulle au survol)
        tooltip = {
            "html": "<b>{LIBGEO} <br/>"
                    f"{{{variable}}}%",
            "style": {
                "backgroundColor": "#faf6ef",
                "color": "#8b5e3c",
                "border": "1px solid #d17842",
                "borderRadius": "5px"
            }
        }

        # Affichage
        r = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style=None,
            tooltip=tooltip
        )
        
        
        st.pydeck_chart(r, use_container_width=True,height=600)
        # -----------------------------------------
        # LÉGENDE COULEUR (Compatible Streamlit)
        # -----------------------------------------

        # On récupère min et max (valeurs réelles)
        min_val = float(gdf[variable].min())
        max_val = float(gdf[variable].max())
        mean_val = float(gdf[variable].mean())

        if max_val == min_val:
            mean_ratio = 0.5
        else:
            mean_ratio = (mean_val - min_val) / (max_val - min_val)
            mean_ratio = max(0, min(1, mean_ratio))

        mean_pct = mean_ratio * 100

        legend_html = f"""
        <div>
            <div style="position:relative; height: 18px; margin-bottom: 12px;">
                <div style="
                    height: 18px;
                    background: linear-gradient(to right, rgb(255,255,180), rgb(255,0,0));
                    border-radius: 5px;
                "></div>
                <div style="
                    position:absolute;
                    left: calc({mean_pct:.1f}% - 1px);
                    top: -4px;
                    width: 2px;
                    height: 26px;
                    background: #8b5e3c;
                    box-shadow: 0 0 6px rgba(0,0,0,0.15);
                "></div>
            </div>
            <div style="position:relative; color:#8b5e3c; font-size: 13px; height: 18px;">
                <span style="position:absolute; left:0;">{min_val:.1f} %</span>
                <span style="position:absolute; right:0;">{max_val:.1f} %</span>
                <span style="
                    position:absolute;
                    left: calc({mean_pct:.1f}%);
                    transform: translateX(-50%);
                ">moyenne : {mean_val:.1f}%</span>
            </div>
        </div>
        """

        st.markdown(legend_html, unsafe_allow_html=True)



         

# ------------------------------------------------
# 📊 ONGLET 3 : ANALYSE
# ------------------------------------------------
with tab3:
    # =====================================================
    #  ANALYSE PAR COMMUNE — DESIGN ÉPURÉ ET HARMONISÉ
    # =====================================================
    st.markdown("<h2 style='text-align:center; color:#8b5e3c;'>Analyse par commune</h2>", unsafe_allow_html=True)

    commune = st.selectbox(
        "Sélectionnez une commune :",
        sorted(datahab["LIBGEO"].unique()),
        index=0
    )
    
    # Récupération du département correspondant à la commune sélectionnée
    dep_value = gdf.loc[gdf["LIBGEO"] == commune, "DEP"].iloc[0]


    # Attribution du nom du département
    if dep_value == 34:
        departement = "Hérault"
    elif dep_value == 30:
        departement = "Gard"
    else:
        departement = "Autre département"
    st.markdown(f"<h4 style='text-align:center; color:#8b5e3c;'>Évolution historique de la commune : <b>{commune}</b><br>Département : {departement}</h4>", unsafe_allow_html=True)
    st.markdown("---")

    # Palette de couleurs beige-orange harmonisée
    couleurs = ["#d17842", "#e8a87c", "#8b5e3c", "#f0b68c", "#c06838"]

    # =====================================================
    # 1️⃣ Évolution du parc de logements
    # =====================================================
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        datahab2 = datahab[datahab["LIBGEO"] == commune]

        fig = px.bar(
            datahab2,
            x="AN",
            y="NOMBRE",
            barmode="stack",
            color="TYPE_HABITAT",
            text_auto=True,
            title="<b>Évolution du parc de 2013 à 2022 selon le type d'habitat</b>",
            color_discrete_sequence=couleurs[:2],
            labels={
                "AN": "Année",
                "NOMBRE": "Nombre de logements",
                "TYPE_HABITAT": "Type d'habitat"
            }
        )

        # Ligne du total
        totaux = datahab2.groupby("AN", as_index=False)["LOG"].first()
        fig.add_trace(
            go.Scatter(
                x=totaux["AN"],
                y=totaux["LOG"],
                line_shape='spline',
                mode="lines+markers+text",
                text=[f"{int(v):,}".replace(",", " ") for v in totaux["LOG"]],
                textposition="top center",
                name="Total logements",
                line=dict(color="#8b5e3c", width=2.5),
                marker=dict(size=6)
            )
        )

        # Mise en forme uniforme
        fig.update_layout(
            template="plotly_white",
            bargap=0.15,
            barmode="stack",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            #title_x=0.5,
            margin=dict(t=80, b=40, l=30, r=30),
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig, use_container_width=True,
    config={})

    # =====================================================
    # 2️⃣ Répartition des résidences principales (camembert)
    # =====================================================
    with col2:
        dataso2 = dataso[(dataso["LIBGEO"] == commune) & (dataso["AN"] == 2022)]

        fig2 = px.pie(
            dataso2,
            values="NOMBRE",
            names="STATUT",
            title="<b>Répartition des résidences principales en 2022 par statut d'occupation</b>",
            color_discrete_sequence=couleurs
        )
        fig2.update_traces(textinfo="percent+label", pull=[0.05, 0.05, 0.05, 0.05])
        fig2.update_layout(
            template="plotly_white",
            #title_x=0.5,
            margin=dict(t=80, b=40, l=30, r=30),
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig2, use_container_width=True,
      config={})

    st.markdown("---")

    # =====================================================
    # 3️⃣ Répartition des logements selon la catégorie
    # =====================================================
    col3, col4 = st.columns(2, gap="medium")
    with col3:
        datacate2 = datacate[datacate["LIBGEO"] == commune]

        fig3 = px.area(
            datacate2,
            x="AN",
            y="NOMBRE",
            color="TYPE_LOG",
            title="<b>Évolution des logements de 2013 à 2022 selon leur catégorie</b>",
            color_discrete_sequence=couleurs[:3],
            labels={
                "AN": "Année",
                "NOMBRE": "Nombre de logements",
                "TYPE_LOG": "Catégorie"
            }
        )
        fig3.update_layout(
            template="plotly_white",
            hovermode="x unified",
            #title_x=0.5,
            margin=dict(t=80, b=40, l=30, r=30),
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig3, use_container_width=True,
    config={})

    # =====================================================
    # 4️⃣ Typologie des résidences principales
    # =====================================================
    with col4:
        dataty2 = dataty[(dataty["LIBGEO"] == commune) & (dataty["AN"] == 2022)]

        fig4 = px.bar(
            dataty2,
            x="NOMBRE",
            y="TYPO",
            orientation="h",
            text_auto=True,
            title="<b>Répartition des résidences principales en 2022 selon leur typologie</b>",
            color_discrete_sequence=["#d17842"]
        )
        fig4.update_layout(
            template="plotly_white",
            #title_x=0.5,
            margin=dict(t=80, b=40, l=30, r=30),
            yaxis=dict(categoryorder="array", categoryarray=["T1", "T2", "T3", "T4", "T5et+"]),
        )
        st.plotly_chart(fig4, use_container_width=True, config={})

# ------------------------------------------------
# ONGLET 4 : INTELLIGENCE TERRITORIALE
# ------------------------------------------------
with tab4:

    st.markdown("<h2 style='text-align:center; color:#8b5e3c;'>Intelligence Territoriale</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8b5e3c; font-size:16px;'>Analyses avancées et aide à la décision</p>", unsafe_allow_html=True)
    st.markdown("---")

    # 🔧 CREATION AUTOMATIQUE DES VARIABLES MANQUANTES POUR LE ML
    if "Plog_MAISON" not in data_carto.columns:
        data_carto["Plog_MAISON"] = (data_carto["MAISON"] / data_carto["LOG"]) * 100

    if "Plog_APPART" not in data_carto.columns:
        data_carto["Plog_APPART"] = (data_carto["APPART"] / data_carto["LOG"]) * 100

    if "Plog_RP" not in data_carto.columns:
        data_carto["Plog_RP"] = (data_carto["RP"] / data_carto["LOG"]) * 100

    if "Plog_RS" not in data_carto.columns:
        data_carto["Plog_RS"] = (data_carto["RSECOCC"] / data_carto["LOG"]) * 100

    if "Plog_VAC" not in data_carto.columns:
        data_carto["Plog_VAC"] = (data_carto["LOGVAC"] / data_carto["LOG"]) * 100

    if "Prp_RP_PROP" not in data_carto.columns:
        data_carto["Prp_RP_PROP"] = (data_carto["RP_PROP"] / data_carto["RP"]) * 100

    # -------------------------------------------------
    # SOUS-ONGLETS
    ia_tab1, ia_tab2, ia_tab3 = st.tabs([
        "Profils de communes", 
        "Tension immobilière", 
        "Prédictions"
    ])

    # =====================================================
    # 1️⃣ PROFILS DE COMMUNES (Clustering K-Means)
    # =====================================================
    with ia_tab1:

        st.markdown("### Regrouper les communes similaires")
        st.markdown("<div class='info-card'><p style='color:#8b5e3c;margin:0;'>Regroupement automatique des communes aux profils proches (vacance, propriétaires, résidences secondaires).</p></div>", unsafe_allow_html=True)

        # → On fixe K=3
        n_profils = 3
        data_profils, noms_profils = ml.identifier_profils_communes(data_carto, n_profils)

        col_profils, col_map = st.columns([1, 2], gap="large")

        with col_profils:
            st.markdown("#### Groupes identifiés (3)")

            for profil_id, info in noms_profils.items():
                subset = data_profils[data_profils['Profil'] == profil_id]

                pct_vac = subset["Plog_VAC"].mean()
                pct_rs = subset["Plog_RS"].mean()

                st.markdown(f"""
                <div class='info-card'>
                    <h4 style='color:#d17842; margin-top:0;'>{info['nom']}</h4>
                    <p style='color:#8b5e3c; margin:5px 0;'><b>{len(subset)} communes</b></p>
                    <p style='color:#8b5e3c; margin:0; font-size:12px;'>
                        Vacance moyenne : {pct_vac:.1f}%<br>
                        Rés. secondaires moyenne : {pct_rs:.1f}%
                    </p>
                    <ul style='color:#8b5e3c; font-size:12px; padding-left:18px;'>
                        {''.join([f"<li>{point}</li>" for point in info.get('insights', [])])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)



        with col_map:
            st.markdown("#### Cartographie des profils identifiés")
            st.markdown("##### Trouver le profil d'une commune")
            commune_recherche = st.selectbox(
                "Sélectionnez une commune",
                sorted(data_profils["LIBGEO"].unique()),
                key="recherche_profil"
            )

            if commune_recherche:
                profil_commune = data_profils[data_profils['LIBGEO'] == commune_recherche]['Profil'].iloc[0]
                nom_profil = noms_profils[profil_commune]['nom']

                communes_similaires = data_profils[data_profils["Profil"] == profil_commune][["LIBGEO", "DEP"]].sort_values("LIBGEO")

                st.info(f"**{commune_recherche}** appartient au groupe : **{nom_profil}**")

            gdf_profils = gdf.merge(
                data_profils[["LIBGEO", "Profil", "Nom_Profil"]],
                on="LIBGEO",
                how="left",
            )

            highlight_geom = None
            if commune_recherche:
                highlight_geom = gdf_profils[gdf_profils["LIBGEO"] == commune_recherche]
                if highlight_geom.empty:
                    highlight_geom = None

            color_palette = [
                [209, 120, 66],
                [139, 94, 60],
                [247, 197, 142],
                [120, 158, 149],
                [183, 120, 180],
            ]
            profil_colors = {
                profil_id: color_palette[idx % len(color_palette)]
                for idx, profil_id in enumerate(sorted(noms_profils.keys()))
            }

            gdf_profils["fill_color"] = gdf_profils["Profil"].map(
                lambda x: profil_colors.get(x, [210, 210, 210])
            )

            center_geom = gdf.geometry.union_all().centroid
            profils_view = pdk.ViewState(
                latitude=center_geom.y,
                longitude=center_geom.x,
                zoom=8,
                pitch=0,
            )

            profils_layer = pdk.Layer(
                "GeoJsonLayer",
                gdf_profils,
                pickable=True,
                stroked=True,
                filled=True,
                get_fill_color="fill_color",
                get_line_color=[80, 80, 80],
                get_line_width=50,
            )

            layers = [profils_layer]

            if highlight_geom is not None:
                highlight_layer = pdk.Layer(
                    "GeoJsonLayer",
                    highlight_geom,
                    stroked=True,
                    filled=False,
                    get_line_color=[0, 0, 0],
                    get_line_width=300,
                    get_line_width_min_pixels=3,
                )
                layers.append(highlight_layer)

            profils_tooltip = {
                "html": "<b>{LIBGEO}</b><br/>Profil : {Nom_Profil}",
                "style": {
                    "backgroundColor": "#faf6ef",
                    "color": "#8b5e3c",
                    "border": "1px solid #d17842",
                    "borderRadius": "5px",
                },
            }

            profils_map = pdk.Deck(
                layers=layers,
                initial_view_state=profils_view,
                map_style=None,
                tooltip=profils_tooltip,
            )

            st.pydeck_chart(profils_map, use_container_width=True, height=500)

            legend_blocks = []
            for profil_id, info in noms_profils.items():
                color = profil_colors.get(profil_id, [210, 210, 210])
                nom = info["nom"].strip()
                if nom.lower().startswith("profil "):
                    nom = nom.split(" ", 1)[1]
                block = (
                    f"<div style='display:flex; align-items:center; margin-bottom:6px;'>"
                    f"<span style='width:16px; height:16px; border-radius:4px; background: rgb({color[0]}, {color[1]}, {color[2]}); display:inline-block; margin-right:8px; border:1px solid #8b5e3c;'></span>"
                    f"<span style='color:#8b5e3c; font-size:13px;'>Profil {nom}</span>"
                    f"</div>"
                )
                legend_blocks.append(block)

            legend_items = "".join(legend_blocks)

            st.markdown(
                f"""
                <div style='background:#faf6ef; padding:12px 16px; border-radius:10px; box-shadow:0 4px 12px rgba(139,94,60,0.12); margin-bottom:20px;'>
                    <h5 style='color:#d17842; margin-top:0;'>Légende des profils</h5>
                    {legend_items}
                </div>
                """,
                unsafe_allow_html=True,
            )




    # =====================================================
    # 2️⃣ SCORE DE TENSION IMMOBILIÈRE
    # =====================================================
    with ia_tab2:

        st.markdown("### Où le marché du logement est-il tendu ?")
        st.markdown("<div class='info-card'><p style='color:#8b5e3c;margin:0;'>Score 0–100 basé sur vacance, % propriétaires, résidences secondaires.</p></div>", unsafe_allow_html=True)
        st.markdown("---")

        data_tension = ml.calculer_tension_immobiliere(data_carto)

        col_top, col_flop = st.columns(2)

        with col_top:
            st.markdown("#### Marchés les PLUS tendus")
            top = data_tension.nlargest(10, "Score_Tension")[["LIBGEO", "Score_Tension", "Plog_VAC"]]
            st.dataframe(top, width='stretch')

        with col_flop:
            st.markdown("#### Marchés les MOINS tendus")
            flop = data_tension.nsmallest(10, "Score_Tension")[["LIBGEO", "Score_Tension", "Plog_VAC"]]
            st.dataframe(flop, width='stretch')

        st.markdown("---")

        # 🔎 Recherche
        st.markdown("#### Vérifier le score d'une commune")
        commune_tension = st.selectbox("Choisissez une commune", sorted(data_tension["LIBGEO"].unique()))

        if commune_tension:
            row = data_tension[data_tension["LIBGEO"] == commune_tension].iloc[0]
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Score", f"{row['Score_Tension']:.1f}/100")
            with col2: st.metric("Niveau", row["Niveau"])
            with col3: st.metric("Vacance", f"{row['Plog_VAC']:.1f}%")

    # =====================================================
    # 3️⃣ PRÉDICTION : Evolution du nombre de logements
    # =====================================================
    with ia_tab3:

        st.markdown("### Prédiction du parc de logements")
        st.markdown("<div class='info-card'><p style='color:#8b5e3c;margin:0;'>Projection simple basée sur la tendance historique.</p></div>", unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            commune_pred = st.selectbox("Sélectionnez une commune", sorted(datahab["LIBGEO"].unique()))
        with col2:
            annees_pred = st.slider("Années à prédire", 1, 5, 3)

        if st.button("Lancer la prédiction", type="primary"):

            predictions, croissance = ml.predire_evolution_logements(datahab, commune_pred, annees_pred)

            if predictions is not None:
                st.success("Prédiction réalisée")

                dernier_reel = predictions[predictions["Type"] == "Historique"]["Logements"].iloc[-1]
                dernier_pred = predictions[predictions["Type"] == "Prédiction"]["Logements"].iloc[-1]
                annee_fin = predictions[predictions["Type"] == "Prédiction"]["Année"].iloc[-1]

                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Logements en 2022", f"{int(dernier_reel):,}".replace(",", " "))
                with col2: st.metric(f"Prévision {annee_fin}", f"{int(dernier_pred):,}".replace(",", " "))
                with col3: st.metric("Évolution", f"{int(dernier_pred - dernier_reel):+}", delta=f"{croissance:.2f}%/an")

                fig = px.line(predictions, x="Année", y="Logements", color="Type", markers=True)
                fig.update_layout(template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(predictions, width='stretch')

            else:
                st.error("Pas assez de données pour prédire.")

    # ----------------------------------------------------
    # FOOTER
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#8b5e3c; font-size:13px;'>
        Les modèles utilisent des tendances historiques et doivent être interprétés avec prudence.
    </div>
    """, unsafe_allow_html=True)
