from flask import Flask, request, jsonify
import mysql.connector
from config import Config

app = Flask(__name__)

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
            # Simulation du score (remplacer par une logique ou un modèle plus tard)
            sentiment_score = round(len(tweet) % 3 - 1, 2)
            positive = 1 if sentiment_score > 0 else 0
            negative = 1 if sentiment_score < 0 else 0

            # Sauvegarde dans la base de données
            save_tweet_to_db(tweet, positive, negative)

            # Ajout des résultats pour la réponse
            results[f"tweet{idx + 1}"] = sentiment_score

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
