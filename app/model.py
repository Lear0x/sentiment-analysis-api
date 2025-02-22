import pickle
import mysql.connector
import pandas as pd
from config import Config
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sqlalchemy import create_engine

def load_data():
    try:
        # Créer une connexion SQLAlchemy
        engine = create_engine(f"mysql+mysqlconnector://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}/{Config.MYSQL_DB}")
        query = "SELECT text, positive, negative FROM tweets;"
        df = pd.read_sql(query, engine)  # Utilisation de SQLAlchemy
        engine.dispose()

        # Préparer X (texte) et y (labels)
        X = df["text"]
        y_positive = df["positive"]
        y_negative = df["negative"]
        
        return X, y_positive, y_negative
    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")
        return None, None, None

    
def train_model(X, y):
  
    vectorizer = CountVectorizer()
    X_vect = vectorizer.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_vect, y, test_size=0.2, random_state=42)

    # Entraîner le modèle
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Évaluer le modèle
    y_pred = model.predict(X_test)
    print("Rapport de classification :")
    print(classification_report(y_test, y_pred, zero_division=1))

    plot_confusion_matrix(y_test, y_pred, "Matrice de Confusion")

    return model, vectorizer

def plot_confusion_matrix(y_true, y_pred, title):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap="Blues", xticklabels=["Négatif", "Positif"], yticklabels=["Négatif", "Positif"])
    plt.xlabel("Prédictions")
    plt.ylabel("Réel")
    plt.title(title)
    plt.show(block=False)
    plt.pause(5)
    plt.close()

if __name__ == "__main__":
    # Charger les données
    X, y_positive, y_negative = load_data()
    
    print(f"y_positive : {y_positive.count()}")
    print(f"y_negative : {y_negative.count()}")
    if X is not None and y_positive is not None:
        print("Entraînement pour les sentiments positifs...")
        model_positive, vectorizer_positive = train_model(X, y_positive)

        print("Entraînement pour les sentiments négatifs...")
        model_negative, vectorizer_negative = train_model(X, y_negative)

        # Sauvegarder les modèles et vectorizers
        with open("model_positive.pkl", "wb") as f:
            pickle.dump((model_positive, vectorizer_positive), f)

        with open("model_negative.pkl", "wb") as f:
            pickle.dump((model_negative, vectorizer_negative), f)

        print("Modèles sauvegardés avec succès.")