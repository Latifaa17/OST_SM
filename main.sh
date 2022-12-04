#cd ./Stream_Mining_Pipelines
#bash run_preprocessing.sh

echo 'Running docker compose'
# docker-compose build
docker-compose up -d
cd ./Kafka
echo 'Running producer'
python producer_mul.py
python producer.py

# cd ../Stream_Mining_Pipelines

# python Model_LogisticRegression_based_Changedetection.py
# python KSWIN.py
# python Kmeans.py
# wait