'''
Compare to the producer.py, this producer will each time send 20 rows to the consumer
'''


from time import sleep
import csv
from json import dumps
from kafka import KafkaProducer


def json_serializer(data):
    return dumps(data).encode('utf-8')

topic = 'SWAT_MUL'
producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: dumps(x).encode('utf-8'))
rdr =  csv.DictReader(open("./data/Swat_dataset.csv")) 
window_size = 20
next(rdr,)


while True:
    try:
        lines = []
        for i in range(window_size):
            lines.append(next(rdr,None))
        result=dumps(lines)
        producer.send(topic,value=result)
        print("Sending message")
        sleep(5)
        
        if len(lines) < window_size:
            break
            
    except Exception as e: 
        print("Error")
        print(f"Type {e}")
        break