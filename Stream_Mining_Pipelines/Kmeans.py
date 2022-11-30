from json import loads
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import pickle

import pandas as pd

import warnings
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

    model = pickle.load(open(f'./models/kmeans.pickle', 'rb'))
    keep = ['FIT101', 'LIT101', 'P101', 'P102', 'AIT201', 'AIT202', 'AIT203',
       'P201', 'P204', 'DPIT301', 'FIT301', 'LIT301', 'MV301', 'MV302',
       'MV303', 'MV304', 'AIT401', 'AIT402', 'LIT401', 'P403', 'AIT501',
       'AIT502', 'AIT503', 'AIT504', 'PIT502', 'FIT601', 'P602']
    

    with InfluxDBClient(url="http://localhost:8086", token=f'{username}:{password}', org='-',bucket=bucket) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        consumer = KafkaConsumer(topic, bootstrap_servers=['localhost:9092'],auto_offset_reset='earliest', api_version=(0,10),enable_auto_commit=True,value_deserializer=lambda x: loads(x.decode('utf-8')))
        print("Connection established")
        i=0

        for message in consumer:

            df = pd.DataFrame(message.value,index=[0])
            point = Point("Kmeans")
            point.field("label", float(df.iloc[0]["label"]))
            point.tag("label", float(df.iloc[0]["label"]))

            df_clean = df[keep]
           
            prediction = model.predict(df_clean.iloc[0].to_numpy().reshape(1,-1))
            #print(prediction[0])
            point.field("prediction", float(prediction[0]))
            point.tag("prediction", float(prediction[0]))
            
            point.time(datetime.utcnow(), WritePrecision.NS)
            write_api.write(bucket, org, point)


            '''For EDA'''
            dict = message.value
            point_1 = Point("SWAT_EDA")            

            for key, val in dict.items():
                    if key != 'Timestamp':
                        point_1.field(key, float(val))
                    if key== 'label':
                        point.tag(key, float(val))

            point_1.time(datetime.utcnow(), WritePrecision.NS)
            
            write_api.write(bucket, org, point_1)

            i+=1
            print("Message sent to influxDB", i)


if __name__ == "__main__":
    main()