# ================================================================
# Application Open Data Logement (Gard & Hérault)
# ================================================================
# lanceur : streamlit run app.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
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

    st.markdown("<h2 style='text-align:center; color:#8b5e3c;'>Cartographie interactive</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8b5e3c; margin-bottom: 20px;'>Explorez les indicateurs de logement par commune</p>", unsafe_allow_html=True)

    # Layout : deux colonnes
    col_left, col_right = st.columns([1, 3], gap="small")
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
            index=None if st.session_state.selected_group != "parc" else 0,
            horizontal=False,
            key="radio_parc",
            label_visibility="collapsed",
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
            index=None if st.session_state.selected_group != "rp" else 0,
            horizontal=False,
            key="radio_rp",
            label_visibility="collapsed",
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
            index=None if st.session_state.selected_group != "loc" else 0,
            horizontal=False,
            key="radio_loc",
            label_visibility="collapsed",
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

        # Affichage des statistiques de la variable sélectionnée
        if variable:
            stats = gdf[variable].describe()
            st.markdown(f"""
            <div class='info-card'>
                <p style='margin: 0; color: #8b5e3c; font-size: 13px;'>
                    <b>Statistiques :</b><br>
                    Min: {stats['min']:.1f}% | 
                    Moy: {stats['mean']:.1f}%<br>
                    Max: {stats['max']:.1f}%
                </p>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        # -----------------------------
        # Préparation des données
        # -----------------------------
        #gdf[variable] = pd.to_numeric(gdf[variable], errors="coerce")

        # Calcul du centre géographique pour centrer la carte
        center = gdf.geometry.union_all().centroid
        lat, lon = center.y, center.x

        # -----------------------------
        # Carte Folium stylisée
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
            fill_color="YlOrRd",  # palette plus vive
            fill_opacity=0.85,
            line_opacity=0.4,
            legend_name=f"{variable} (%)"
        ).add_to(m)

        # Contours + infobulle personnalisée
        folium.GeoJson(
            gdf,
            name="Communes",
            style_function=lambda x: {
                "fillColor": "transparent",
                "color": "#d17842",
                "weight": 0.5,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["LIBGEO", variable],
                aliases=["Commune :", f"{variable} :"],
                localize=True,
                sticky=True,
                labels=True,
                style=(
                    "background-color: #faf6ef; color: #8b5e3c; font-family: Inter; font-size: 13px; " 
                    "padding: 8px; border: 2px solid #d17842; border-radius:6px;"
                ),
            ),
        ).add_to(m)

        # Titre visuel
        #st.markdown(
        #    f"<h4 style='text-align:center;'>Carte de la variable <span style='color:#ff5733'>{variable}</span></h4>",
        #    unsafe_allow_html=True,
        #)

        # Affichage de la carte
        st_folium(m, width=None, height=660)

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
        st.plotly_chart(fig, width='stretch')

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
        st.plotly_chart(fig2, width='stretch')

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
        st.plotly_chart(fig3, width='stretch')

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
        st.plotly_chart(fig4, width='stretch')

# ------------------------------------------------
# ONGLET 4 : INTELLIGENCE TERRITORIALE
# ------------------------------------------------
with tab4:
    st.markdown("<h2 style='text-align:center; color:#8b5e3c;'>Intelligence Territoriale</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8b5e3c; font-size:16px;'>Analyses avancées et aide à la décision</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Sous-onglets pour les 3 fonctionnalités
    ia_tab1, ia_tab2, ia_tab3 = st.tabs([
        "Profils de communes", 
        "Tension immobilière", 
        "Prédictions"
    ])
    
    # =====================================================
    # PROFILS DE COMMUNES (Clustering)
    # =====================================================
    with ia_tab1:
        st.markdown("### Regrouper les communes similaires")
        st.markdown("<div class='info-card'><p style='color:#8b5e3c;margin:0;'>Regroupement automatique des communes aux profils proches (vacance, propriétaires, résidences secondaires).</p></div>", unsafe_allow_html=True)
        
        # Analyse automatique au chargement
        n_profils = 3  # Fixé à 3 pour la simplicité
        data_profils, noms_profils = ml.identifier_profils_communes(data_carto, n_profils)
        
        # Affichage simple et direct
        st.markdown("#### Groupes identifiés (3)")
        
        # Afficher les cartes de profils en colonnes
        cols = st.columns(3)
        for idx, (profil_id, info) in enumerate(noms_profils.items()):
            with cols[idx]:
                nb_communes = len(data_profils[data_profils['Profil'] == profil_id])
                stats = ml.get_stats_profil(data_profils, profil_id)
                
                st.markdown(f"""
                <div class='info-card'>
                    <h4 style='color:#d17842; margin-top:0;'>{info['nom']}</h4>
                    <p style='color:#8b5e3c; font-size:14px;'>{info['description']}</p>
                    <p style='color:#8b5e3c; margin:5px 0;'><b>{nb_communes} communes</b></p>
                    <p style='color:#8b5e3c; margin:0; font-size:12px;'>
                    Vacance : {stats['pct_vac_moyen']:.1f}%<br>
                    Rés. secondaires : {stats['pct_rs_moyen']:.1f}%
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Recherche simple de commune
        st.markdown("#### Trouver le profil d'une commune")
        commune_recherche = st.selectbox(
            "Sélectionnez une commune",
            sorted(data_profils["LIBGEO"].unique()),
            key="recherche_profil"
        )
        
        if commune_recherche:
            profil_commune = data_profils[data_profils['LIBGEO'] == commune_recherche]['Profil'].iloc[0]
            nom_profil = noms_profils[profil_commune]['nom']
            
            # Afficher les communes similaires
            communes_similaires = data_profils[data_profils['Profil'] == profil_commune][
                ['LIBGEO', 'DEP']
            ].sort_values('LIBGEO').head(10)
            
            st.info(f"**{commune_recherche}** appartient au groupe : **{nom_profil}**")
            st.markdown(f"**Les 10 premières communes similaires :**")
            st.dataframe(communes_similaires, width='stretch', height=300)
    
    # =====================================================
    # SCORE DE TENSION IMMOBILIÈRE
    # =====================================================
    with ia_tab2:
        st.markdown("### Où le marché du logement est-il tendu ?")
        st.markdown("<div class='info-card'><p style='color:#8b5e3c;margin:0;'>Score 0–100 calculé à partir de la vacance, des résidences secondaires et des propriétaires.</p></div>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Calcul automatique
        data_tension = ml.calculer_tension_immobiliere(data_carto)
        
        # Affichage simple et direct - TOP 10
        col_top, col_flop = st.columns(2)
        
        with col_top:
            st.markdown("#### Marchés les PLUS tendus")
            st.markdown("*Là où il faut construire en priorité*")
            top_tension = data_tension.nlargest(10, 'Score_Tension')[
                ['LIBGEO', 'Score_Tension', 'Plog_VAC']
            ].reset_index(drop=True)
            top_tension.columns = ['Commune', 'Score /100', 'Vacance %']
            st.dataframe(top_tension, width='stretch', height=400)
        
        with col_flop:
            st.markdown("#### Marchés les MOINS tendus")
            st.markdown("*Là où il y a trop de logements vides*")
            low_tension = data_tension.nsmallest(10, 'Score_Tension')[
                ['LIBGEO', 'Score_Tension', 'Plog_VAC']
            ].reset_index(drop=True)
            low_tension.columns = ['Commune', 'Score /100', 'Vacance %']
            st.dataframe(low_tension, width='stretch', height=400)
        
        st.markdown("---")
        
        # Recherche par commune
        st.markdown("#### Vérifier le score d'une commune")
        commune_tension = st.selectbox(
            "Sélectionnez une commune",
            sorted(data_tension["LIBGEO"].unique()),
            key="recherche_tension"
        )
        
        if commune_tension:
            score = data_tension[data_tension['LIBGEO'] == commune_tension]['Score_Tension'].iloc[0]
            niveau = data_tension[data_tension['LIBGEO'] == commune_tension]['Niveau'].iloc[0]
            vacance = data_tension[data_tension['LIBGEO'] == commune_tension]['Plog_VAC'].iloc[0]
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Score de tension", f"{score:.1f}/100")
            with col_m2:
                st.metric("Niveau", niveau)
            with col_m3:
                st.metric("Vacance", f"{vacance:.1f}%")
    
    # =====================================================
    # PRÉDICTION D'ÉVOLUTION
    # =====================================================
    with ia_tab3:
        st.markdown("### Prédiction du parc de logements")
        st.markdown("<div class='info-card'><p style='color:#8b5e3c;margin:0;'>Projection simple basée sur la tendance historique.</p></div>", unsafe_allow_html=True)
        
        # Sélection commune
        col_commune, col_annees = st.columns([3, 1])
        with col_commune:
            commune_pred = st.selectbox(
                "Sélectionnez une commune",
                sorted(datahab["LIBGEO"].unique()),
                key="pred_commune"
            )
        with col_annees:
            annees_pred = st.slider("Années à prédire", 1, 5, 3)
        
        if st.button("Lancer la prédiction", type="primary"):
            with st.spinner(f"Prédiction pour {commune_pred}..."):
                predictions, croissance = ml.predire_evolution_logements(
                    datahab, commune_pred, annees_pred
                )
                
                if predictions is not None:
                    st.success("Prédiction réalisée avec succès")
                    
                    # Métrique de croissance
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        dernier_reel = predictions[predictions['Type'] == 'Historique']['Logements'].iloc[-1]
                        st.metric("Logements en 2022", f"{int(dernier_reel):,}".replace(',', ' '))
                    with col_m2:
                        dernier_pred = predictions[predictions['Type'] == 'Prédiction']['Logements'].iloc[-1]
                        annee_fin = int(predictions[predictions['Type'] == 'Prédiction']['Année'].iloc[-1])
                        st.metric(f"Prévision {annee_fin}", f"{int(dernier_pred):,}".replace(',', ' '))
                    with col_m3:
                        delta_logements = int(dernier_pred - dernier_reel)
                        st.metric("Évolution prévue", f"{delta_logements:+,}".replace(',', ' ') + " log.",
                                 delta=f"{croissance:.2f}%/an")
                    
                    # Graphique de prédiction
                    st.markdown("#### Courbe de prédiction")
                    fig_pred = px.line(
                        predictions,
                        x='Année',
                        y='Logements',
                        color='Type',
                        markers=True,
                        title=f"Évolution du parc de logements - {commune_pred}",
                        color_discrete_map={'Historique': '#8b5e3c', 'Prédiction': '#d17842'}
                    )
                    fig_pred.update_layout(
                        template="plotly_white",
                        hovermode="x unified",
                        xaxis_title="Année",
                        yaxis_title="Nombre de logements"
                    )
                    st.plotly_chart(fig_pred, width='stretch')
                    
                    # Tableau de détail
                    st.markdown("#### Détail des valeurs")
                    st.dataframe(
                        predictions.style.format({'Logements': '{:.0f}', 'Année': '{:.0f}'}),
                        width='stretch',
                        height=300
                    )
                else:
                    st.error("Données historiques insuffisantes pour cette commune.")
    
    # Footer de l'onglet IA
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#8b5e3c; font-size:13px; padding:20px;'>
        <p><b>Note :</b> Ces analyses utilisent des algorithmes de machine learning.<br>
        Les prédictions sont basées sur les tendances historiques et doivent être interprétées avec précaution.</p>
    </div>
    """, unsafe_allow_html=True)