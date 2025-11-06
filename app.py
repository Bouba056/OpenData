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

# Style CSS personnalisé 
st.markdown(
    """
    <style>
    /* Centrage du titre principal */
    .main-title {
        text-align: center;
        color: #2E4053;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: -10px;
    }
    /* Sous-titre */
    .subtitle {
        text-align: center;
        color: #7F8C8D;
        font-size: 18px;
        margin-bottom: 30px;
    }
    /* Titres des sections */
    h2, h3, h4 {
        color: #2E4053;
    }
  /* ───────────────
       🧭 ONGLET DESIGN
       ─────────────── */
    div[data-baseweb="tab-list"] {
        justify-content: center;
        gap: 20px !important;
    }

    /* Style des boutons d'onglets */
    button[data-baseweb="tab"] {
        background-color: #f4f6f8;
        color: #2E4053;
        border-radius: 12px;
        padding: 10px 30px;
        font-size: 17px;
        font-weight: 600;
        border: 1px solid #d0d3d4;
        transition: all 0.2s ease-in-out;
    }

    /* Effet hover */
    button[data-baseweb="tab"]:hover {
        background-color: #e6e9eb;
        border-color: #b0b3b5;
        transform: translateY(-2px);
    }

    /* Onglet actif */
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #2E86C1;
        color: white;
        border: 1px solid #2E86C1;
        box-shadow: 0px 3px 6px rgba(46, 134, 193, 0.3);
        transform: translateY(-2px);
    }

    /* Separator line */
    hr {
        border: none;
        height: 1px;
        background-color: #ccc;
        margin: 15px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# ------------------------------------------------
# 📂 IMPORT SIMPLE DES DONNÉES
# ------------------------------------------------

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
# ------------------------------------------------
# 🧭 EN-TÊTE DE L'APPLICATION
# ------------------------------------------------

st.markdown("<h1 class='main-title'>Tableau de bord du parc de logement</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Gard (30) et Hérault (34) — Données 2013 à 2022</p>", unsafe_allow_html=True)


# Création des onglets
tab1, tab2, tab3 = st.tabs(["🛖Accueil", "🌍 Cartographie", "📈 Analyse"])

# ------------------------------------------------
# ONGLET 1 : ACCUEIL
# ------------------------------------------------
with tab1:
    # Titre principal
    st.markdown(
        "<h2 style='text-align:center; color:#2E4053;'>Projet open data et web des données</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#7F8C8D; font-size:17px;'>"
        "Une application interactive pour explorer l’évolution du parc de logements "
        "dans les départements du <b>Gard (30)</b> et de <b>l’Hérault (34)</b>."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    #  Présentation générale
    st.markdown("### 🎯 Objectif de l’application")
    st.write(
        """
        Cette application a pour but de faciliter la **visualisation**, la **comparaison** et 
        l’**analyse temporelle** des indicateurs liés au logement dans les communes du Gard et de l’Hérault.  
        Elle met à disposition :
        - Une **cartographie interactive** des indicateurs (parts de résidences principales, logements vacants, etc.) ;
        - Une **analyse temporelle** de l’évolution du parc par commune ;
        - Des graphiques interactifs permettant d’explorer la composition du parc de logements.
        """
    )

    st.markdown("---")

    # 📦 Sources et traitements
    st.markdown("### 🗂️ Source et traitement des données")
    st.write(
        """
        Les données proviennent des fichiers **Insee, recensements de la population. ** disponibles en Open Data.  
        Elles ont été retraitées pour :
        - Harmoniser les millésimes de **2013 à 2022** ;
        - Calculer des indicateurs complémentaires (parts, taux, ratios...) ;
        - Produire des jeux de données exploitables pour la visualisation.

        Les traitements ont été réalisés avec **Python (pandas, geopandas)** et les visualisations avec **Streamlit**, **Plotly** et **Folium**.
        """
    )

    st.markdown("---")

    # 📊 Aperçu des données
    st.markdown("### ⎍ Exemple de données utilisées")

    # Affichage d’un petit échantillon
    st.dataframe(
        data_carto.head(5).style.format(precision=1, thousands=" "),
        use_container_width=True
    )

    st.markdown(
        """
        🔍 *Chaque ligne correspond à une commune et contient les indicateurs calculés pour l’année la plus récente (2022).  
        Les principales variables sont :*
        - **LIBGEO** : nom de la commune ;
        - **DEP** : code du département (30 ou 34) ;
        - **LOG**, **RP**, **RSECOCC**, **LOGVAC** : volumes de logements ;
        - **Plog_…**, **Prp_…** : indicateurs en pourcentage du parc total ou des résidences principales.
        """
    )

    st.markdown("---")

    # 🤝 Signature / contact
    st.markdown(
        """
        <p style='text-align:center; color:#7F8C8D; font-size:15px;'>
        Développé dans le cadre du projet <b>Open Data</b> — Données INSEE, 2013–2022.<br>
        Réalisation : <b>Amadou Aboubacar, Ndiaye Ibrahima</b> — Master 2 MIASHS, Université Paul Valéry Montpellier.
        </p>
        """,
        unsafe_allow_html=True,
    )

    


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
        
        # --- Initialisation de session pour un seul choix global ---
        if "selected_group" not in st.session_state:
            st.session_state.selected_group = "parc"

        # --- 1️⃣ Part des catégories de logement dans tout le parc ---
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

        # --- 2️⃣ Part des catégories de résidences principales ---
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

        # --- 3️⃣ Part des types de locatifs ---
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

        # --- Déterminer la variable active ---
        variable = None
        if st.session_state.selected_group == "parc" and choice_parc:
            variable = {v: k for k, v in labels_parc.items()}[choice_parc]
        elif st.session_state.selected_group == "rp" and choice_rp:
            variable = {v: k for k, v in labels_rp.items()}[choice_rp]
        elif st.session_state.selected_group == "loc" and choice_loc:
            variable = {v: k for k, v in labels_rpty.items()}[choice_loc]

        # --- Message ou affichage ---
       # if variable is None:
      #      st.warning("➡️ Sélectionnez une variable dans l’un des trois blocs pour afficher la carte.")
       # else:
       #     st.markdown(
       #         f"📊 **Variable sélectionnée :** `{variable}`",
       #         help="Choisissez un indicateur à cartographier."
      #      )



    with col_right:
        # -----------------------------
        # 🗺️ Préparation des données
        # -----------------------------
        #gdf[variable] = pd.to_numeric(gdf[variable], errors="coerce")

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
                "color": "#1f77b4",
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
        #st.markdown(
        #    f"<h4 style='text-align:center;'>Carte de la variable <span style='color:#ff5733'>{variable}</span></h4>",
        #    unsafe_allow_html=True,
        #)

        # Affichage de la carte
        st_folium(m, width=1000, height=660)

# ------------------------------------------------
# 📊 ONGLET 3 : ANALYSE
# ------------------------------------------------
with tab3:
    # =====================================================
    #  ANALYSE PAR COMMUNE — DESIGN ÉPURÉ ET HARMONISÉ
    # =====================================================
    st.markdown("<h2 style='text-align:center; color:#2E4053;'>Analyse par commune</h2>", unsafe_allow_html=True)

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
    st.markdown(f"<h4 style='text-align:center; color:#7F8C8D;'>Évolution historique de la commune : <b>{commune}</b><br>Département : {departement}</h4>", unsafe_allow_html=True)
    st.markdown("---")

    # Palette de couleurs cohérente
    couleurs = ["#4C72B0", "#C44E52", "#85B31A", "#FFA726"]

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
                line=dict(color="#2E4053", width=2.5),
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
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

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
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

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
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

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
            color_discrete_sequence=["#2E86C1"]
        )
        fig4.update_layout(
            template="plotly_white",
            #title_x=0.5,
            margin=dict(t=80, b=40, l=30, r=30),
            yaxis=dict(categoryorder="array", categoryarray=["T1", "T2", "T3", "T4", "T5et+"]),
        )
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
