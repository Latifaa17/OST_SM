'''
This file can be used when you're using the Kafka/producer_mul.py as a producer
Then in each message from Kafka, there will be 20 rows(a window, size can be modified) in the dataframe
After some process, use the for loop to send each row in the dataframe as a point to the influxdb
Then the timestamp of the points can be considered as processing time but not the event time
'''
from json import loads
from kafka import KafkaConsumer
import argparse
import json
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
from skmultiflow.drift_detection.adwin import ADWIN
import numpy as np
import pandas as pd

topic = 'SWAT_MUL'
print("Connecting to consumer ...")

org = "elte"
username = 'admin'
password = 'admin'
database = 'swat'
retention_policy = 'autogen'
bucket = f'{database}/{retention_policy}'

def dic2df(dic):
    dic = json.loads(dic)
    df = pd.DataFrame.from_dict(dic,)
    df.drop(columns=['','Timestamp'],inplace=True)
    df.columns[-1]
    df = pd.DataFrame(df.values,dtype='float',columns=df.columns)
    return df

with InfluxDBClient(url="http://localhost:8086", token=f'{username}:{password}', org='-',bucket=bucket) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    consumer = KafkaConsumer(topic, bootstrap_servers=['localhost:9092'],auto_offset_reset='earliest', api_version=(0,10),enable_auto_commit=True,value_deserializer=lambda x: loads(x.decode('utf-8')))
    print("Connection established")
    df_list = []
    i = 0
    for message in consumer:
        
        dic = message.value
        df = dic2df(dic)
        
        
        for index,data in df.iterrows(): # Send rows into influexdb by point
            point = Point("SWAT_MUL_sample")
            for key,data in zip(data.index,data):
                point.field(key, float(data))
                point.time(datetime.utcnow(), WritePrecision.NS)
            write_api.write(bucket, org, point)
            i+=1
#             print("Message sent to influxDB", i)
