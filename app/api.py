from datetime import datetime, timedelta
import pickle
from flask import Flask, request, jsonify
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
from app.model import train_model
from config import Config

app = Flask(__name__)

# Charger les modèles et vectorizers
with open("model_positive.pkl", "rb") as f:
    model_positive, vectorizer_positive = pickle.load(f)

with open("model_negative.pkl", "rb") as f:
    model_negative, vectorizer_negative = pickle.load(f)

# Fonction pour enregistrer un tweet dans la base de données
def save_tweet_to_db(text, positive, negative):
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO tweets (text, positive, negative) VALUES (%s, %s, %s)",
            (text, positive, negative)
        )
        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Erreur lors de l'insertion en base de données : {err}")

# Endpoint pour analyser les sentiments
@app.route('/analyze', methods=['POST'])
def analyze_sentiments():
    try:
        # Récupération des tweets depuis la requête JSON
        data = request.get_json()
        tweets = data.get("tweets", [])

        # Vérification que la liste n'est pas vide
        if not tweets:
            return jsonify({"error": "La liste des tweets est vide."}), 400

        results = {}
        for idx, tweet in enumerate(tweets):
            # Prédiction des probabilités
            prob_positive = model_positive.predict_proba(vectorizer_positive.transform([tweet]))[0][1]
            prob_negative = model_negative.predict_proba(vectorizer_negative.transform([tweet]))[0][1]

            # Calcul du score final
            sentiment_score = prob_positive - prob_negative
            print(f"Tweet {idx + 1} : {tweet} - Score : {sentiment_score}")
            # Ajouter le score dans le résultat
            results[f"tweet{idx + 1}"] = round(float(sentiment_score), 2)
            
            if sentiment_score > 0:
                positive = 1
                negative = 0
            else:
                positive = 0
                negative = 1
            # Enregistrer le tweet dans la base de données      
            save_tweet_to_db(tweet, positive, negative)
            
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tweets', methods=['GET'])
def get_all_tweets():
    try:
        # Connexion à la base de données
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor(dictionary=True)  # Retourne les résultats sous forme de dictionnaire

        # Récupérer tous les tweets
        cursor.execute("SELECT * FROM tweets;")
        tweets = cursor.fetchall()

        cursor.close()
        connection.close()

        # Retourner les tweets au format JSON
        return jsonify(tweets), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Erreur de base de données : {err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def log_retraining(name, last_tweet_id):
    try:
        last_tweet_id = int(last_tweet_id)
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()
        print("insertion données")
        cursor.execute(
            "INSERT INTO retraining_logs (name, timestamp, last_tweet_id) VALUES (%s, NOW(), %s)",
            (name, last_tweet_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        print("Réentraînement logué avec succès.")
    except mysql.connector.Error as err:
        print(f"Erreur lors de la journalisation du réentraînement : {err}")

def check_last_retraining():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM retraining_logs;")
        last_retraining = cursor.fetchone()[0]  # Récupère la dernière date de réentraînement
        cursor.close()
        connection.close()

        if last_retraining is None:
            return True

        # Vérifier si plus de 7 jours se sont écoulés
        seven_days_ago = datetime.now() - timedelta(days=7)
        return last_retraining < seven_days_ago
    except mysql.connector.Error as err:
        print(f"Erreur lors de la vérification du dernier réentraînement : {err}")
        return False

def load_new_data(last_tweet_id):
    try:
        
        # Créer une connexion SQLAlchemy
        engine = create_engine(f"mysql+mysqlconnector://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}/{Config.MYSQL_DB}")
        query = f"SELECT id, text, positive, negative FROM tweets WHERE id > {last_tweet_id};"
        df = pd.read_sql(query, engine)  # Utilisation de SQLAlchemy
        engine.dispose()
        return df
    except mysql.connector.Error as err:
        print(f"Erreur lors du chargement des nouveaux tweets : {err}")
        return None
# Fonction de réentraînement
def retrain_model():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(last_tweet_id) FROM retraining_logs;")
        last_tweet_id = int(cursor.fetchone()[0] or 0)
        cursor.close()
        connection.close()

        df = load_new_data(last_tweet_id)
        if df is None or df.empty:
            print("Aucun nouveau tweet trouvé pour le réentraînement.")
            return

        X = df["text"]
        y_positive = df["positive"]
        y_negative = df["negative"]

        print("Réentraînement du modèle positif...")
        model_positive, vectorizer_positive = train_model(X, y_positive)

        print("Réentraînement du modèle négatif...")
        model_negative, vectorizer_negative = train_model(X, y_negative)

        with open("model_positive.pkl", "wb") as f:
            pickle.dump((model_positive, vectorizer_positive), f)

        with open("model_negative.pkl", "wb") as f:
            pickle.dump((model_negative, vectorizer_negative), f)

        last_tweet_id = df["id"].max()
        log_retraining("API_start_retraining", last_tweet_id)
        print("Réentraînement terminé et logué avec succès.")
    except Exception as e:
        print(f"Erreur lors du réentraînement : {e}")

# Vérification au démarrage
def retrain_model_if_needed():
    if check_last_retraining():
        print("Le dernier réentraînement date de plus de 7 jours. Lancement du réentraînement...")
        retrain_model()
    else:
        print("Le modèle est à jour. Aucun réentraînement nécessaire.")
        
if __name__ == '__main__':
    retrain_model_if_needed()
    app.run(debug=True)
