'''
Don't forget using the Kafka/producer_mul.py as a producer to generate batch data not single data to do the prediction
'''
from json import loads
from kafka import KafkaConsumer
import argparse
import json
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import numpy as np
import pandas as pd
import pickle
from sklearn.metrics import accuracy_score,f1_score,recall_score

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
    df = pd.DataFrame(df.values,dtype='float',columns=list(df.columns[:-1])+['label'])
    return df

def calc_score(y_test,y_pred,pos_label=1):
    return accuracy_score(y_test,y_pred),f1_score(y_test,y_pred,zero_division=1,pos_label=pos_label),recall_score(y_test,y_pred,zero_division=1,pos_label=pos_label)


golden_features = ['AIT402','MV304','AIT203','LIT101','LIT301','P102',
                    'AIT503','AIT504','AIT401','AIT201','P201','FIT101',
                    'P101','DPIT301','PIT502'] 
model = pickle.load(open(f'./models/LogisticRegression.pkl', 'rb'))

with InfluxDBClient(url="http://localhost:8086", token=f'{username}:{password}', org='-',bucket=bucket) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    consumer = KafkaConsumer(topic, bootstrap_servers=['localhost:9092'],auto_offset_reset='earliest', api_version=(0,10),enable_auto_commit=True,value_deserializer=lambda x: loads(x.decode('utf-8')))
    print("Connection established")
    df_list = []
    i = 0
    for message in consumer:
        
        dic = message.value
        df = dic2df(dic)
        
        X = df[golden_features].values 
        y = df['label']
        
        y_pred = model.predict(X)
        
        acc, f1, recall = calc_score(y,y_pred,0)
        print(acc,f1,recall)
        
        for index,data in df.iterrows(): # Send rows into influexdb by point
            point = Point("SWAT_MUL_sample")
            for key,data in zip(data.index,data):
                point.field(key, float(data))
                point.time(datetime.utcnow(), WritePrecision.NS)
                
                if key == 'label':
                    point.tag("label", data)
                if acc < 0.6 or f1 < 0.6 or recall < 0.6:
                    print('change')
                    point.field('change', 1)
                    point.tag('change', 1)
                else:
                    point.field('change', 0)
                    point.tag('change', 0)
                    
            write_api.write(bucket, org, point)
            i+=1
#             print("Message sent to influxDB", i)
