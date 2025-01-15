import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import joblib
from math import ceil

# Set the page layout to wide
st.set_page_config(layout="wide", page_icon="🌎", page_title="Project DataViz")

# Custom HTML for background color and interactive elements
st.markdown(
    """
   <style>
    /* Section principale */
    .main {
        background-color: #FEF3E2;  /* Fond doux et lumineux */
        padding: 10px;
    }

    /* Barre latérale */
    [data-testid="stSidebar"] {
        background: #f5b647;  /* Slider couleur */
        color: #000000;  /* Texte noir */
    }

    /* Paragraphes */
    p {
        color: #000000;  /* Texte noir */
        font-family: 'Arial', sans-serif;
        font-size: 18px;
        font-weight: bold;
    }

    /* Boutons */
    .stButton button {
        background-color: #FA812F;  /* Couleur importante */
        color: #000000;  /* Texte noir */
        font-family: 'Arial Black', sans-serif;
        text-shadow: none;  /* Pas d'ombres */
        border: none;
        padding: 10px;
        border-radius: 8px;
    }
    .stButton button:hover {
        background-color: #FA812F;  /* Couleur du slider au survol */
        color: #FEF3E2;  /* Texte harmonieux */
    }

    /* Selectbox et sliders */
    .stSelectbox, .stSlider {
        color: #000000;  /* Texte noir */
        font-family: 'Arial', sans-serif;
    }

    .stSelectbox div[role="listbox"] ul li, .stSlider .step {
        background: #FEF3E2;  /* Fond doux et lumineux pour les options */
        color: #000000;  /* Texte noir */
    }

    .stSlider > div > div > div > div {
        background: #f5b647;  /* Slider couleur */
    }

    /* Boutons radio */
    input[type="radio"]:checked + div {
        background: #FA812F !important;  /* Couleur importante pour les boutons activés */
        border-radius: 30px;
        color: #000000;  /* Texte noir */
    }

    /* Champs d'entrée */
    input[type="text"], textarea {
        background-color: #FFFFFF;  /* Fond blanc */
        color: #000000;  /* Texte noir */
        border: 1px solid #f5b647;  /* Bordure du slider couleur */
        border-radius: 5px;
        padding: 5px;
    }
    input[type="text"]:focus, textarea:focus {
        border-color: #FA812F;  /* Bordure importante au focus */
        outline: none;
    }

    /* Checkbox */
    input[type="checkbox"]:checked + label {
        color: #FA812F;  /* Couleur importante pour les labels activés */
        font-weight: bold;
    }
</style>

    """,
    unsafe_allow_html=True
)

# Sidebar navigation
data = gpd.read_file("output_2.gpkg")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Visualisation des données géospatiales", "Correlation Heatmap", "Graphiques Comparatifs"])

main_bg_color = "#FEF3E2"  # Fond principal doux
text_color = "#000000"     # Texte noir
highlight_color = "#FA4032"  # Couleur importante
button_bg_color = "#f5b647"  # Slider couleur
button_hover_color = "#FA812F"  # Slider couleur au survol

if page == "Visualisation des données géospatiales":
    # Titre de l'application et bouton côte à côte
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Visualisation des données géospatiales")
    with col2:
        generate_button = st.button('Générer la carte')

    # Sélectionner une colonne pour la visualisation
    columns = ['dry', 'PRELIQ_MENS', 'T_MENS', 'EVAP_MENS', 'ETP_MENS', 'PE_MENS', 'SWI_MENS']
    column = st.selectbox("Sélectionnez une colonne à visualiser :", columns)

    # Ajouter un slider pour sélectionner l'année
    year = st.slider("Sélectionnez une année :", min_value=2019, max_value=2022, value=2019)

    # Placeholder for the map
    map_placeholder = st.empty()

    if generate_button:
        try:
            temp = data[data.year == year]

            # Créer et afficher le graphique
            fig, ax = plt.subplots(figsize=(20, 10), facecolor=main_bg_color)
            temp.plot(column=column, cmap="YlOrRd", legend=True, ax=ax, edgecolor='none')
            plt.title(f"Carte thématique : {column} pour l'année {year}", color=text_color)
            ax.set_facecolor(main_bg_color)
            plt.axis('off')
            map_placeholder.pyplot(fig)

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")

elif page == "Correlation Heatmap":
    st.title("Correlation Heatmap")

    temp = data[['dry', 'PRELIQ_MENS', 'T_MENS', 'EVAP_MENS', 'ETP_MENS', 'PE_MENS', 'SWI_MENS']]
    correlation_matrix = temp.corr()

    fig, ax = plt.subplots(figsize=(20, 10), facecolor=main_bg_color)
    sns.heatmap(correlation_matrix, annot=True, cmap="YlOrRd", ax=ax, cbar_kws={'shrink': 0.75})
    plt.title("Linear Correlation Heatmap", color=text_color)
    ax.set_facecolor(main_bg_color)
    st.pyplot(fig)

elif page == "Graphiques Comparatifs":
    model = joblib.load('random_forest_classification_model.pkl')
    features = ['PRELIQ_MENS', 'T_MENS', 'EVAP_MENS', 'ETP_MENS', 'PE_MENS', 'SWI_MENS']

    st.title("Prédiction d'Arrêt de Sécheresse")
    codgeo = st.text_input('Entrez le code INSEE ', value='75056')
    annee = st.slider('Sélectionnez l\'année', 2019, 2022, 2019)

    if st.button('Prédire'):
        tempo = data[data.codgeo == codgeo]
        if len(tempo) > 0:
            tempo = tempo[tempo.year == annee]
            if len(tempo) > 0:
                tempo_features = tempo[features]
                prediction = model.predict(tempo_features)
                tempo["temporaire"] = prediction

                fig, ax = plt.subplots(figsize=(6, 3), facecolor=main_bg_color)
                tempo.plot(column="temporaire", cmap="YlOrRd", legend=False, ax=ax, edgecolor='none')
                plt.title(f"Carte thématique : temporaire pour l'année {annee}", color=text_color)
                ax.set_facecolor(main_bg_color)
                plt.axis('off')
                st.pyplot(fig)

                probabilities = model.predict_proba(tempo_features)[0]
                classe = model.classes_

                st.subheader("Probabilités de survenance d'arrêt CATNAT:")
                fig, ax = plt.subplots()
                ax.pie(probabilities, labels=[f'Classe {classe[i]}: {probabilities[i]*100:.2f}%' for i in range(len(classe))], 
                       colors=['#FA4032', button_bg_color], startangle=90, wedgeprops=dict(width=0.3, edgecolor='w'))
                plt.axis('equal')
                st.pyplot(fig)

                st.subheader('Principales caractéristiques affectant la prédiction:')
                feature_importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
                fig, ax = plt.subplots()
                ax.barh(feature_importances.index, feature_importances.values, color=['#FA4032', button_bg_color])
                ax.set_facecolor(main_bg_color)
                
                
                
                
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.tick_params(left=False, bottom=False)
                st.pyplot(fig)

            else:
                st.warning("Aucune donnée pour cette année.")
        else:
            st.warning("Code INSEE non valide.")
