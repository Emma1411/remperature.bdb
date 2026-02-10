# Utilise une image Spark avec Python intégré
FROM spark:3.5.7-scala2.12-java17-python3-ubuntu

WORKDIR /app
COPY . /app

USER root

# Installer les bibliothèques Python nécessaires
RUN pip install pyspark kafka-python happybase

# Ajouter les dépendances Kafka pour Spark Structured Streaming
RUN wget https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.7/spark-sql-kafka-0-10_2.12-3.5.7.jar -P /opt/spark/jars \
 && wget https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.7/spark-token-provider-kafka-0-10_2.12-3.5.7.jar -P /opt/spark/jars \
 && wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.0/kafka-clients-3.5.0.jar -P /opt/spark/jars \
 && wget https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.12.0/commons-pool2-2.12.0.jar -P /opt/spark/jars

# Revenir à l'utilisateur spark pour exécution
USER spark

CMD ["spark-submit", "src/spark/spark_streaming.py"]
