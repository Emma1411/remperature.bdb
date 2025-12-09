# remperature.bdb
mini-projet complet de pipeline de données simulant un capteur de température et son traitement automatisé.

🔥 Ce que fait le projet

Simule un capteur IoT qui génère des températures (Python)

Envoie les données dans Kafka via un Producer

Stocke les données grâce à un Consumer Kafka (fichier, DB ou Data Lake)

Automatise le pipeline avec Apache Airflow :

ingestion quotidienne

nettoyage / validation

archivage

transformation / agrégation

Fournit une visualisation simple de l’évolution de la température

🎯 Objectifs du projet

Comprendre un pipeline IoT → Kafka → Airflow

Apprendre à orchestrer des tâches dépendantes

Manipuler des flux temps réel et du batch

Créer un mini Data Pipeline reproductible avec Docker

🧰 Technologies utilisées

Python

Apache Kafka

Apache Airflow

PostgreSQL / CSV

Docker & Docker Compose
