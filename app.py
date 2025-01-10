import streamlit as st
import pandas as pd
from scrapping import input_search_criteria, scrape_flight_data
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# Configuration de la navigation multi-pages
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Recherche", "Résultats des vols", "Résultats de la Classification"])

# Initialisation de la session state
if 'flight_data' not in st.session_state:
    st.session_state.flight_data = None
if 'classification_results' not in st.session_state:
    st.session_state.classification_results = None

# Page principale pour la recherche de vols
if page == "Recherche":
    st.title("Recherche de vols")

    # Saisie des critères de recherche
    origin = st.text_input("Lieu de départ")
    destination = st.text_input("Lieu d'arrivée")
    travel_departure = st.date_input("Date de départ")

    if st.button("Run"):
        with st.spinner('En cours de traitement...'):
            input_search_criteria(origin, destination, travel_departure.strftime('%d/%m/%Y'))
            flight_data = scrape_flight_data()
            st.success('Traitement terminé, consulter résultat sur la page résultats')
            st.session_state.flight_data = flight_data  # Stocker les données dans la session

# Page de résultats des vols
elif page == "Résultats des vols":
    st.title("Résultats des vols")
    if st.session_state.flight_data is not None:
        df = pd.DataFrame(st.session_state.flight_data)
        st.dataframe(df, height=600, width=1000)
    else:
        st.write("Aucun résultat disponible. Veuillez effectuer une recherche de vols.")

# Page de résultats de la classification
elif page == "Résultats de la Classification":
    st.title("Résultats de la Classification")

    if st.session_state.flight_data is not None:
        # Chargement des données
        df = pd.DataFrame(st.session_state.flight_data)

        # Nettoyage
        df['Emission (kg CO2)'] = df['Emission (kg CO2)'].str.replace(' kg CO2e', '').astype(float)
        df['Price (€)'] = df['Price (€)'].str.replace('€', '').astype(float)
        df.set_index('Flight', inplace=True)

        # emission moyenne
        mean_emission = df['Emission (kg CO2)'].mean()

        # Définition des seuils pour les classes d'émission de carbone
        bins = [-float('inf'), mean_emission, float('inf')]
        labels = ['Faible', 'Moyen', 'Fort']
        df['Emission_Class'] = pd.cut(df['Emission (kg CO2)'], bins=bins, labels=labels, right=False, include_lowest=True)

        X = df.drop(columns=['Emission (kg CO2)', 'Emission_Class', 'Departure Time', 'Arrival Time'])
        y = df['Emission_Class']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        categorical_features = X.select_dtypes(include=['object']).columns
        numeric_features = X.select_dtypes(exclude=['object']).columns

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])

        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(random_state=42))
        ])

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        conf_matrix = confusion_matrix(y_test, y_pred)

        # result
        st.write("### Rapport de Classification")
        st.write(pd.DataFrame(report).transpose())

        st.write("### Matrice de Confusion")
        plt.figure(figsize=(10, 7))
        sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
        plt.xlabel('Prédiction')
        plt.ylabel('Réel')
        st.pyplot(plt)

        st.session_state.classification_results = {
            'report': report,
            'conf_matrix': conf_matrix
        }
    else:
        st.write("Aucun résultat disponible. Veuillez effectuer une recherche de vols.")
