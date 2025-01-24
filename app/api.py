from flask import Flask, request, jsonify
import mysql.connector
from config import Config

app = Flask(__name__)

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

        # Simulation des scores de sentiment pour chaque tweet
        results = {}
        for idx, tweet in enumerate(tweets):
            results[f"tweet{idx + 1}"] = round(len(tweet) % 3 - 1, 2)  # Score fictif

        # Retour des résultats
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
