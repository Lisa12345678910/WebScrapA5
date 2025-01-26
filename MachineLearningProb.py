import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def cleaning_data(df):
    df['Emission (kg CO2)'] = df['Emission (kg CO2)'].str.replace(' kg CO2e', '').astype(float)
    df['Price (€)'] = df['Price (€)'].str.replace('€', '').astype(float)
    df.set_index('Flight', inplace=True)
    return df

def prepare_classification_data(flight_data):
    df = pd.DataFrame(flight_data)
    df = cleaning_data(df)

    max_emission = df['Emission (kg CO2)'].max()
    bins = [0, max_emission / 3, 2 * max_emission / 3, max_emission]
    labels = ['Faible', 'Moyen', 'Fort']
    df['Emission_Class'] = pd.cut(df['Emission (kg CO2)'], bins=bins, labels=labels, right=False, include_lowest=True)

    df.dropna(subset=['Emission (kg CO2)',  'Emission_Class'], inplace=True)

    return df

def perform_classification(df):
    X = df[['Emission (kg CO2)']]
    y = df['Emission_Class']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)

    report = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred)

    return report, conf_matrix

def plot_confusion_matrix(conf_matrix, labels):
    plt.figure(figsize=(10, 7))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.xlabel('Prédiction')
    plt.ylabel('Réel')
    plt.show()


