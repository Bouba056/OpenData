Cartographie intelligente du logement (Base CC Logement 2021)
Objectif

Ce projet vise à explorer la Base CC Logement 2021 afin d’analyser la structure du parc de logements en France et d’identifier des profils types de communes.
L’application Streamlit permet de visualiser ces résultats de manière interactive et cartographique.

Contenu du projet

Prétraitement des données : nettoyage, sélection et normalisation des variables clés (résidences principales, secondaires, vacantes, type de logement, ancienneté…).

Analyse exploratoire : statistiques descriptives et corrélations entre variables.

Clustering : identification de groupes de communes similaires (méthode PCA + K-Means).

Détection d’anomalies : mise en évidence de communes atypiques (Isolation Forest).

Cartographie interactive : visualisation des clusters et anomalies via Folium / Plotly intégrés à Streamlit.

Outils et librairies

Python : pandas, numpy, scikit-learn, geopandas

Visualisation : plotly, folium, matplotlib

Interface : Streamlit

Lancer le projet
pip install -r requirements.txt
streamlit run app/dashboard.py

Résultat attendu

Une carte interactive affichant les clusters de communes selon leur profil logement,
ainsi que les communes atypiques détectées par les algorithmes, avec des graphiques comparatifs et un résumé automatique du profil choisi.
