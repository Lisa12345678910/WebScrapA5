import streamlit as st
import pandas as pd
from scrapping import input_search_criteria, scrape_flight_data
from MachineLearningProb import cleaning_data, prepare_classification_data, perform_classification, plot_confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Recherche", "Résultats des vols", "Résultats de la Classification"])

if 'flight_data' not in st.session_state:
    st.session_state.flight_data = None
if 'classification_results' not in st.session_state:
    st.session_state.classification_results = None

if page == "Recherche":
    st.title("Recherche de vols")

    origin = st.text_input("Lieu de départ")
    destination = st.text_input("Lieu d'arrivée")
    travel_departure = st.date_input("Date de départ")

    if st.button("Run"):
        with st.spinner('En cours de traitement...'):
            input_search_criteria(origin, destination, travel_departure.strftime('%d/%m/%Y'))
            flight_data = scrape_flight_data()
            st.success('Traitement terminé, consulter résultat sur la page résultats')
            st.session_state.flight_data = flight_data 

elif page == "Résultats des vols": #results from flights
    st.title("Résultats des vols")
    if st.session_state.flight_data is not None:
        df = pd.DataFrame(st.session_state.flight_data)
        df['Emission (kg CO2)'] = df['Emission (kg CO2)'].str.replace(' kg CO2e', '').astype(float)
        df['Price (€)'] = df['Price (€)'].str.replace('€', '').astype(float)
        df.set_index('Flight', inplace=True)
        st.dataframe(df, height=600, width=1000)
    else:
        st.write("Aucun résultat disponible")

elif page == "Résultats de la Classification": #results from classifiaction
    st.title("Résultats de la Classification")

    if st.session_state.flight_data is not None:
        df = prepare_classification_data(st.session_state.flight_data)
        report, conf_matrix = perform_classification(df)
        st.write("### Rapport de Classification")
        st.write(pd.DataFrame(report).transpose())

        st.write("### Matrice de Confusion")
        labels = ['Faible', 'Moyen', 'Fort']
        plot_confusion_matrix(conf_matrix, labels)
        st.pyplot(plt)

        st.session_state.classification_results = {
            'report': report,
            'conf_matrix': conf_matrix
        }
    else:
        st.write("Aucun résultat disponible")