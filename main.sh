#cd ./Stream_Mining_Pipelines
#bash run_preprocessing.sh

echo 'Running docker compose'
docker-compose build
docker-compose up -d
cd ./Kafka
echo 'Running producer'
python producer.py

# cd ../Stream_Mining_Pipelines
# python influxdbv1_consumer_sample.py
# wait