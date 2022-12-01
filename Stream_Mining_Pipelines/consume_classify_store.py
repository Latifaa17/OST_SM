from json import loads
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import pandas as pd
import pickle
import warnings
warnings.filterwarnings('ignore')

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
        i=0
        for message in consumer:
            #print(f"{message.value}")
            dict = message.value
            features=['FIT101','LIT101','P101','P102','AIT203','P201','DPIT301','FIT301',
        'LIT301','MV302','MV304','AIT402','LIT401','AIT501','AIT502','AIT503','PIT502','label']
            pred_row = pd.DataFrame(dict, index = [0])
            print(pred_row)
            

            #to_predict = pred_row.drop(pred_row.columns.difference(features), 1, inplace=True)

            to_predict = pred_row.values[:,1:-1]
            #print(to_predict)
            model = pickle.load(open(f'models/LinearSVC.pkl', 'rb'))
            preds = model.predict(to_predict)
          
            pred_row["prediction"] = preds
            point = Point("SWAT_classified")
            for key, val in pred_row.items():
                if key != 'Timestamp':
                   point.field(key, float(val))
 
                if key == 'prediction' or key == 'label':
                    point.tag(key, float(val))
            point.time(datetime.utcnow(), WritePrecision.NS)
            
            write_api.write(bucket, org, point)
            i+=1
            print("Message sent to influxDB", i)
        


if __name__ == "__main__":
    main()