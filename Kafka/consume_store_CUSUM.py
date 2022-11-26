#!/usr/bin/env python
#This script consumes data points from kafka, stores them in influxDB "SWAT measurement" 
# + predicts whether a point is a change + stores predictions in influxdb "CUSUM measurement"
from json import loads
from kafka import KafkaConsumer
import argparse
import json
import numpy as np
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
#from scipy import stats
import pandas as pd
import numpy as np

#def standardize(df):
#    df = df.apply(pd.to_numeric, errors='ignore')
#    df = stats.zscore(df)
#return df

#detect_cusum detects changes in a single column x
def detect_cusum(x, threshold=1, drift=0, show=True, ax=None):
    x = np.atleast_1d(x).astype('float64')
    gp, gn = np.zeros(x.size), np.zeros(x.size)
    ta = np.array([], dtype=int)
    tap, tan = 0, 0
    # Find changes (online form)
    for i in range(1, x.size):
        s = x[i] - x[i-1]
        gp[i] = gp[i-1] + s - drift  # cumulative sum for + change
        gn[i] = gn[i-1] - s - drift  # cumulative sum for - change
        if gp[i] < 0:
            gp[i], tap = 0, i
        if gn[i] < 0:
            gn[i], tan = 0, i
        if gp[i] > threshold or gn[i] > threshold:  # change detected!
            ta = np.append(ta, i)    # alarm index
            #tai = np.append(tai, tap if gp[i] > threshold else tan)  # start
            gp[i], gn[i] = 0, 0      # reset alarm
    return ta


#_is_change loops over all the columns and calls the detect_cusum function for each column
def _is_change(df):

    keep=['FIT101','LIT101','P101','P102','AIT201','AIT202','AIT203','P201','P204',
              'DPIT301','FIT301','LIT301','MV301','MV302','MV303','MV304','AIT401','AIT402','LIT401','P403',
              'AIT501','AIT502','AIT503','AIT504','PIT502','FIT601','P602']
        #preprocessing
    df = df[keep]
    #df=standardize(df)
    df['Attack_Detected']=0
    #loop over all the columns
    for i in df.columns:
        x = df[i].to_numpy()
        ta=detect_cusum(x,1, 0.02, True) 
        for j in ta:
            df['Attack_Detected'][j]=1   
    return df

def main():

    topic="SWAT"
    print("Connecting to consumer ...")
    # You can generate an API token from the "API Tokens Tab" in the UI
    token = "1M9gu3cU91GR8s1x6OjrcjpM-s78uvYnvXhi4PJFo0mhOPdM5rEH3glOlni2Lm4tXD05IIGjCX3xLEAc2W9B4w=="
    # Please replace the org and bucket by your own values
    org = "elte"
    bucket = "SWAT"
    with InfluxDBClient(url="http://localhost:8086", token=token, org=org,bucket=bucket) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        consumer = KafkaConsumer(topic, bootstrap_servers=['localhost:9092'],auto_offset_reset='earliest', api_version=(0,10),enable_auto_commit=True,value_deserializer=lambda x: loads(x.decode('utf-8')))
        print("Connection established")
        
        cnt=0         #counter for the bucket size
        win_size=100  #Window size
        df=pd.DataFrame(columns=['Timestamp', 'FIT101', 'LIT101', 'MV101', 'P101', 'P102', 'AIT201',
       'AIT202', 'AIT203', 'FIT201', 'MV201', 'P201', 'P202', 'P203', 'P204',
       'P205', 'P206', 'DPIT301', 'FIT301', 'LIT301', 'MV301', 'MV302',
       'MV303', 'MV304', 'P301', 'P302', 'AIT401', 'AIT402', 'FIT401',
       'LIT401', 'P401', 'P402', 'P403', 'P404', 'UV401', 'AIT501', 'AIT502',
       'AIT503', 'AIT504', 'FIT501', 'FIT502', 'FIT503', 'FIT504', 'P501',
       'P502', 'PIT501', 'PIT502', 'PIT503', 'FIT601', 'P601', 'P602', 'P603',
       'label'])
        for message in consumer:
            #print(f"{message.value}")
            cnt= cnt+1
            dict = message.value
            temp=pd.DataFrame(dict,index=[0])
            
            #print(temp)
            point = Point("SWAT")           
            for key, val in dict.items():
                    if key != 'Timestamp':
                        point.field(key, float(val))
            #save data point
            point.time(datetime.utcnow(), WritePrecision.NS)
            write_api.write(bucket, org, point)
            print("Data point sent to influxDB")
            #convert dict to dataframe
            df = df.append(temp, ignore_index=True)
            if(cnt==win_size):
                #print(df)
                #reset dataframe,counter, and call the change detection model for the previous bucket
                cnt=0
                preds=_is_change(df)
                print("preds: " ,preds)
                for pred in range(len(preds)):
                    #print(preds)
                    point = Point("CUSUM") 
                    for col in preds.columns:

                        if col != 'Timestamp':
                            #print(col,": ",preds.iloc[pred][col])
                            
                            point.field(col, float(preds.iloc[pred][col]))
                    
                #save prediction to influxdb
                    point.time(datetime.utcnow(), WritePrecision.NS)
                    write_api.write(bucket, org, point)
                    print("Point prediction sent to influxDB")
                
                df=pd.DataFrame(columns=['Timestamp', 'FIT101', 'LIT101', 'MV101', 'P101', 'P102', 'AIT201',
                                          'AIT202', 'AIT203', 'FIT201', 'MV201', 'P201', 'P202', 'P203', 'P204',
                                           'P205', 'P206', 'DPIT301', 'FIT301', 'LIT301', 'MV301', 'MV302',
                                            'MV303', 'MV304', 'P301', 'P302', 'AIT401', 'AIT402', 'FIT401',
                                            'LIT401', 'P401', 'P402', 'P403', 'P404', 'UV401', 'AIT501', 'AIT502',
                                            'AIT503', 'AIT504', 'FIT501', 'FIT502', 'FIT503', 'FIT504', 'P501',
                                            'P502', 'PIT501', 'PIT502', 'PIT503', 'FIT601', 'P601', 'P602', 'P603',
                                            'label'])


if __name__ == "__main__":
    main()