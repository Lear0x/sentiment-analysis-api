import sys
import mysql.connector
from config import Config

def create_table():
    connection = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            text VARCHAR(255) NOT NULL,
            positive TINYINT(1),
            negative TINYINT(1)
        );
        
        CREATE TABLE IF NOT EXISTS retraining_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_tweet_id INT NOT NULL
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()
    print("Table 'tweets' créée avec succès.")

def fetch_tweets():
    connection = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tweets;")
    results = cursor.fetchall()
    for row in results:
        print(row)
    cursor.close()
    connection.close()


#lancement commande python -m app.database fetch_tweets ou python -m app.database create_table
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python database.py <create_table|fetch_tweets>")
    elif sys.argv[1] == "create_table":
        create_table()
    elif sys.argv[1] == "fetch_tweets":
        fetch_tweets()
    else:
        print("Action inconnue. Utilisez 'create_table' ou 'fetch_tweets'.")

