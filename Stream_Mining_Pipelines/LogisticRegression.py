
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
    
    golden_features = ['AIT402','MV304','AIT203','LIT101','LIT301','P102',
                    'AIT503','AIT504','AIT401','AIT201','P201','FIT101',
                    'P101','DPIT301','PIT502'] 
    
    model = pickle.load(open(f'./models/LogisticRegression.pkl', 'rb'))
    
    with InfluxDBClient(url="http://localhost:8086", token=f'{username}:{password}', org='-',bucket=bucket) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        consumer = KafkaConsumer(topic, bootstrap_servers=['localhost:9092'],auto_offset_reset='earliest', api_version=(0,10),enable_auto_commit=True,value_deserializer=lambda x: loads(x.decode('utf-8')))
        print("Connection established")
        i = 0  
        for message in consumer:
                
            df = pd.DataFrame(message.value,index=[0])
            df_golden = df[golden_features]
            
            
            point_lr = Point("SWAT_LR_PRED")            
            point_lr.field("label", float(df.iloc[0]["label"]))
            point_lr.tag("label", float(df.iloc[0]["label"]))

            prediction = model.predict(df_golden.iloc[0].to_numpy().reshape(1,-1))
            point_lr.field("prediction", float(prediction[0]))
            point_lr.tag("prediction", float(prediction[0]))
            

            for key in df_golden:
                point_lr.field(key, float(df.iloc[0][key]))
            
            point_lr.time(datetime.utcnow(), WritePrecision.NS)

            write_api.write(bucket, org, point_lr)

            print("Message sent to influxDB",i)
            i += 1
            
if __name__ == "__main__":
    main()


