
from json import loads
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import pickle
import skmultiflow.drift_detection as drift_detection
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import warnings

from Morris_counter import counter
warnings.filterwarnings("ignore")

def main():
    topic="SWAT"
    print("Connecting to consumer ...")

    org = "elte"
    username = 'admin'
    password = 'admin'
    database = 'swat'
    retention_policy = 'autogen'
    bucket = f'{database}/{retention_policy}'
        
    with InfluxDBClient(url="http://localhost:8086", token=f'{username}:{password}', org='-',bucket=bucket) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        consumer = KafkaConsumer(topic, bootstrap_servers=['localhost:9092'],auto_offset_reset='earliest', api_version=(0,10),enable_auto_commit=True,value_deserializer=lambda x: loads(x.decode('utf-8')))
        print("Connection established")
        
        counter_normal = counter()
        counter_attacked= counter()
        cnt_normal = 0
        cnt_attacked = 0
        i = 1  
        for message in consumer:
                  
            dict = message.value
            point_original = Point("SWAT_MORRIS_COUNTER")            

            if dict['label'] == '1':
                counter_attacked.update()
                cnt_attacked += 1
            else:
                counter_normal.update()
                cnt_normal += 1
                
            point_original.field('MORRIS Count Normal', counter_normal.query())  
            point_original.field('MORRIS Count Attacked', counter_attacked.query())  
            
            point_original.field('Real Count Normal', cnt_normal)  
            point_original.field('Real Count Attacked', cnt_attacked) 
             

            point_original.field('label', float(dict['label']))
            point_original.field('Total Count', i)   
            
            point_original.time(datetime.utcnow(), WritePrecision.NS)

            write_api.write(bucket, org, point_original)

            print("Message sent to influxDB",i)
            i += 1
            
if __name__ == "__main__":
    main()


