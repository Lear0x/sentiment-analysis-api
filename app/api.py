import pickle
from flask import Flask, request, jsonify
import mysql.connector
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

if __name__ == '__main__':
    app.run(debug=True)
