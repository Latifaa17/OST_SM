
#https://pypi.org/project/river/#history version  river==0.11.0 is working
from json import loads
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
from river import drift
import pandas as pd

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
        drift_detector_FIT101 = drift.PageHinkley()
        drift_detector_AIT203 = drift.PageHinkley()
        drift_detector_PIT502 = drift.PageHinkley()
        drift_detector_AIT201 = drift.PageHinkley()
        drift_detector_AIT501 = drift.PageHinkley()

        for message in consumer:

            dict = message.value
            change = False
            point = Point("SWAT_PageHinkley")
            #detect change on FIT101
            drift_detector_FIT101.update(float(dict["FIT101"]))
           #detect change on AIT203
            drift_detector_AIT203.update(float(dict["AIT203"]))
           #detect change on PIT502
            drift_detector_PIT502.update(float(dict["PIT502"]))
           #detect change on AIT201
            drift_detector_AIT201.update(float(dict["AIT201"]))
           #detect change on AIT501
            drift_detector_AIT501.update(float(dict["AIT501"]))

            if drift_detector_FIT101.change_detected:
                print(f'Change detected at index {i}, col: FIT101')
                drift_detector_FIT101.reset()  
                change= True


            if drift_detector_AIT203.change_detected:
                print(f'Change detected at index {i}, col: AIT203')
                drift_detector_AIT203.reset()  
                change= True


            if drift_detector_PIT502.change_detected:
                print(f'Change detected at index {i}, col: PIT502')
                drift_detector_PIT502.reset()  
                change= True

            if drift_detector_AIT201.change_detected:
                print(f'Change detected at index {i}, col: AIT201')
                drift_detector_AIT201.reset()  
                change= True



            if drift_detector_AIT501.change_detected:
                print(f'Change detected at index {i}, col: AIT501')
                drift_detector_AIT501.reset()  
                change= True
                


            if change:
                point.field("prediction", 1)
                point.tag("prediction", 1)
            else :
                point.field("prediction", 0)
                point.tag("prediction", 0)


            for key, val in dict.items():
                if key != 'Timestamp' and key != 'prediction':
                   point.field(key, float(val))
 
                if key == 'label' :
                    point.tag(key, float(val))

            
            point.time(datetime.utcnow(), WritePrecision.NS)
            write_api.write(bucket, org, point)
            
            i+=1


if __name__ == "__main__":
    main()