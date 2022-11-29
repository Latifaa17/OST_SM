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

        drift_detector_1 = drift.ADWIN()

        drift_detector_2 = drift.ADWIN()

        for message in consumer:
            #print(f"{message.value}")

            dict = message.value

            '''  FIT101  '''
            point_1 = Point("ADWIN_FIT101")
            point_1.field("label", float(dict["label"]))
            point_1.field("FIT101", float(dict["FIT101"]))
            drift_detector_1.update(float(dict["FIT101"]))
            if drift_detector_1.change_detected:
                # The drift detector indicates after each sample if there is a drift in the data
                print(f'Change detected at index {i}')
                #drift_detector_1.reset()   # As a best practice, we reset the detector
                point_1.field("prediction", 1)
            else:
                point_1.field("prediction", 0)

            point_1.time(datetime.utcnow(), WritePrecision.NS)
            
            write_api.write(bucket, org, point_1)

            '''  AIT203  '''
            point_2 = Point("ADWIN_AIT203")
            point_2.field("label", float(dict["label"]))
            point_2.field("AIT203", float(dict["AIT203"]))
            drift_detector_2.update(float(dict["AIT203"]))
            if drift_detector_2.change_detected:
                # The drift detector indicates after each sample if there is a drift in the data
                print(f'Change detected at index {i}')
                #drift_detector_2.reset()   # As a best practice, we reset the detector
                point_2.field("prediction", 1)
            else:
                point_2.field("prediction", 0)

            point_2.time(datetime.utcnow(), WritePrecision.NS)
            
            write_api.write(bucket, org, point_2)


            i+=1
            print("Message sent to influxDB", i)


if __name__ == "__main__":
    main()