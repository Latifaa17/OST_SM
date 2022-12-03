from json import loads
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import pickle
# import skmultiflow.drift_detection as drift_detection
from river import drift as drift_detection
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
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

    detect_features = ['AIT203','PIT502','AIT201','AIT501']

    def change_detect(model,new_data):
        # model.add_element(new_data)
        model.update(new_data)
        # if model.change_detected:
        if model.drift_detected:
            # model.reset()
            return 1
        else:
            return 0
        
    with InfluxDBClient(url="http://localhost:8086", token=f'{username}:{password}', org='-',bucket=bucket) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        consumer = KafkaConsumer(topic, bootstrap_servers=['localhost:9092'],auto_offset_reset='earliest', api_version=(0,10),enable_auto_commit=True,value_deserializer=lambda x: loads(x.decode('utf-8')))
        print("Connection established")
        i=0
        
        
        kswin_AIT203 = drift_detection.KSWIN(alpha=5e-05,window_size=30,stat_size=15)
        kswin_PIT502 = drift_detection.KSWIN(alpha=1e-07,window_size=100,stat_size=50)
        kswin_AIT201 = drift_detection.KSWIN(alpha=0.001,window_size=50,stat_size=25)
        kswin_AIT501 = drift_detection.KSWIN(alpha=0.005,window_size=100,stat_size=10)
        
        for message in consumer:

            df = pd.DataFrame(message.value,index=[0])
            point = Point("SWAT_kswin_ait203") # The point for predicting change
            point.field("label", float(df.iloc[0]["label"])) 
            point.tag("label", float(df.iloc[0]["label"])) # tag:string
            
            df_detect = df[detect_features]
            
            AIT203_change = change_detect(kswin_AIT203,float(df_detect['AIT203']))
            PIT502_change = change_detect(kswin_PIT502,float(df_detect['PIT502']))
            AIT201_change = change_detect(kswin_AIT201,float(df_detect['AIT201']))
            AIT501_change = change_detect(kswin_AIT501,float(df_detect['AIT501']))
            # is_change_MV304 = change_detect(kswin_MV304,float(df_golden['MV304']))
            # is_change_PIT502 = change_detect(kswin_PIT502,float(df_golden['PIT502']))
            
            
            for feature_name,change in zip(detect_features,[AIT203_change,PIT502_change,AIT201_change,AIT501_change]):
                point.field(feature_name+'_change', change) 
            
            point.field("sum_change", np.array([AIT203_change,PIT502_change,AIT201_change,AIT501_change]).sum()) 
            
            for key in df_detect:
                point.field(key, float(df.iloc[0][key]))    

            point.time(datetime.utcnow(), WritePrecision.NS)
            write_api.write(bucket, org, point)


            # dict = message.value
            # point_original = Point("SWAT")            

            # for key, val in dict.items():
            #     if key != 'Timestamp':
            #         point_original.field(key, float(val))
            #     if key == 'label':
            #         point_original.tag(key, float(val))

            # point_original.time(datetime.utcnow(), WritePrecision.NS)

            # write_api.write(bucket, org, point_original)

            i+=1
            print("Message sent to influxDB", i)
            
if __name__ == "__main__":
    main()


