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
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

def choose_para_KS(data_part,window_sizes=None,alphas=None):
    '''
    The function for choosing the parameter based on different features in the dataset offline, based on the visualization, so it would be better to run this code on jupyter notebook, by all the detected figures, you may choose the best parameter from it manually.
    data_part: You can choose the part of the data which has a ideal change, then the function will show how it change and how the KSWIN with following parameters detect works by visualization
    window_sizes: List of candidate window size
    alphas: List of candidate alpha
    '''
    if window_sizes == None:
        window_sizes = [10,30,50,100]
    if alphas == None:
        alphas = [0.005,0.001,0.0005,0.0001,0.00005,0.00001,0.000005,0.000001,0.0000005,0.0000001,0.00000005,0.00000001]
    for window_size in window_sizes:
        for stat_size in np.linspace(window_size/10,window_size/2,3):
            for alpha in alphas:
                print("window size:",window_size,"stat_size:",stat_size,"alpha:",alpha)
                model = drift_detection.KSWIN(alpha,window_size=100,stat_size=int(stat_size))
                is_change = []
                for index,input_value in enumerate(data_part):
                    model.add_element(input_value)
                    if model.change_detected:
                        is_change.append(1)
                    else:
                        is_change.append(0)

                plt.figure(figsize=(20,5))
                plt.subplot(2,1,1)
                plt.plot(data_part)
                plt.subplot(2,1,2)
                plt.plot(np.array(is_change),c='red')
                plt.show()
                
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


