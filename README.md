
# Sentiment Analysis API

## Description
Ce projet permet d'analyser les sentiments des tweets à l'aide d'une API Flask, d'une base de données MySQL et d'un modèle de régression logistique entraîné avec `scikit-learn`.

---

## Prérequis
Avant de commencer, assurez-vous d'avoir installé les outils suivants :
- **Python 3.9+**
- **Docker et Docker Compose**
- **Git**

---

## Installation du Projet

### 1. **Cloner le dépôt**
Clonez ce projet sur votre machine :
```bash
git clone <URL_DU_DEPOT>
cd sentiment-analysis-api
```

### 2. **Configurer l'environnement Python**
Créez un environnement virtuel et installez les dépendances :
```bash
python3 -m venv venv
source venv/bin/activate          # Sous Windows : venv\Scripts\activate
pip install -r requirements.txt
```

### 3. **Configurer Docker**
Lancez la base de données MySQL avec Docker :
```bash
docker-compose up -d
```

Vérifiez que le conteneur MySQL est bien en cours d'exécution :
```bash
docker ps
```

### 4. **Créer le fichier `.env`**
Créez un fichier `.env` à la racine du projet pour stocker les variables d'environnement :
```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=sentiment_user
MYSQL_PASSWORD=user_password
MYSQL_DB=sentiment_db
FLASK_ENV=development
```

### 5. **Initialiser la base de données**
Créez la table `tweets` dans la base de données :
```bash
python app/database.py create_table
```

### 6. **Tester la base de données**
Pour voir les données (s'il y en a) dans la table `tweets` :
```bash
python -m app.database create_table
```

---

## Utilisation

### 1. **Lancer l'API Flask**
Activez l'environnement virtuel (si ce n'est pas encore fait) et lancez le serveur Flask :
```bash
source venv/bin/activate          # Sous Windows : venv\Scripts\activate
python app/api.py
```

L'API sera disponible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

### 2. **Endpoint d'Analyse des Sentiments**
Utilisez un client HTTP comme **Postman** ou **curl** pour interagir avec l'API.

#### Exemple de requête :
```bash
curl -X POST http://127.0.0.1:5000/analyze \
-H "Content-Type: application/json" \
-d '{
    "tweets": ["J'adore ce projet !", "Ce programme est horrible..."]
}'
```

#### Exemple de réponse :
```json
{
    "tweet1": 0.8,
    "tweet2": -0.6
}
```

---

## Scripts Disponibles

### Initialiser la base de données
Créer la table `tweets` :
```bash
python -m app.database create_table
```

### Voir les données de la base de données
Afficher les entrées existantes dans la table `tweets` :
```bash
python -m app.database fetch_tweets
```

### Réentraînement du modèle
(À venir) Script pour automatiser le réentraînement.

---

## Contribution
1. Créez une branche pour vos modifications :
   ```bash
   git checkout -b feature/<nom_de_la_feature>
   ```
2. Faites vos changements et commitez-les :
   ```bash
   git add .
   git commit -m "Description des changements"
   ```
3. Poussez vos modifications vers le dépôt distant :
   ```bash
   git push origin feature/<nom_de_la_feature>
   ```
4. Ouvrez une Pull Request sur la branche `main`.

---

## Aide
Si vous rencontrez des problèmes, contactez [Mathieu](mailto:mathieu@example.com) ou ouvrez une issue sur GitHub.
