from time import sleep
import csv
from json import dumps
from kafka import KafkaProducer



def json_serializer(data):
    return dumps(data).encode('utf-8')

producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: dumps(x).encode('utf-8'))
rdr =  csv.DictReader(open('data/test.csv')) 

next(rdr)


while True:
    try:
        line=next(rdr,None)
        if line is None:
            break
        sleep(1)
        result=dumps(line)
        producer.send('SWAT',value=result)
        print(result)
    except Exception as e: 
        print("Error")
        print(f"Type {e}")
        break