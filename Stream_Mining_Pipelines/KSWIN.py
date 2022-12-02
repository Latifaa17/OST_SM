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

    golden_features = ['AIT402','MV304','PIT502']
    #                     'AIT203','LIT101','LIT301','P102',
    #                     'AIT503','AIT504','AIT401','AIT201','P201','FIT101',
    #                     'P101','DPIT301',      # Features have strongly correlated values with the label in my data analysis

    def change_detect(model,new_data):
        model.add_element(new_data)
        if model.change_detected:
            #Should be reset
            return True
        else:
            return False
        
    with InfluxDBClient(url="http://localhost:8086", token=f'{username}:{password}', org='-',bucket=bucket) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        consumer = KafkaConsumer(topic, bootstrap_servers=['localhost:9092'],auto_offset_reset='earliest', api_version=(0,10),enable_auto_commit=True,value_deserializer=lambda x: loads(x.decode('utf-8')))
        print("Connection established")
        i=0
        
        
        kswin_AIT402 = drift_detection.KSWIN()
        kswin_MV304 = drift_detection.KSWIN()
        kswin_PIT502 = drift_detection.KSWIN()
        
        for message in consumer:

            df = pd.DataFrame(message.value,index=[0])
            point = Point("SWAT_KSWIN") # The point for predicting change
            point.field("label", float(df.iloc[0]["label"])) 
            point.tag("label", float(df.iloc[0]["label"])) # tag:string
            point.field("label", float(df.iloc[0]["label"])) 
            point.tag("label", float(df.iloc[0]["label"])) # tag:string
            
            df_golden = df[golden_features]
            
            is_change_AIT402 = change_detect(kswin_AIT402,float(df_golden['AIT402']))
            is_change_MV304 = change_detect(kswin_MV304,float(df_golden['MV304']))
            is_change_PIT502 = change_detect(kswin_PIT502,float(df_golden['PIT502']))
            
            if any([is_change_AIT402,is_change_MV304,is_change_PIT502]) == True:
                point.field("change", 1) 
                point.tag("change", 1)
            else:
                point.field("change", 0) 
                point.tag("change", 0)
            print(point)
            point.time(datetime.utcnow(), WritePrecision.NS)
            write_api.write(bucket, org, point)

                
            dict = message.value
            point_original = Point("SWAT")            

            for key, val in dict.items():
                if key != 'Timestamp':
                    point_original.field(key, float(val))
                if key == 'label':
                    point_original.tag(key, float(val))

            point_original.time(datetime.utcnow(), WritePrecision.NS)

            write_api.write(bucket, org, point_original)

            i+=1
            print("Message sent to influxDB", i)
            
if __name__ == "__main__":
    main()


