
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

        drift_detector = drift.PageHinkley()

        for message in consumer:

            dict = message.value

            point = Point("SWAT_PageHinkley")
            point.field("label", float(dict["label"]))
            point.tag("label", float(dict["label"]))
           #detect change on FIT101
            drift_detector.update(float(dict["FIT101"]))


            if drift_detector.change_detected:
                print(f'Change detected at index {i}, col: FIT101')
                drift_detector.reset()  
                point.field("prediction", 1)
                point.tag("prediction", 1)
            else:
                point.field("prediction", 0)
                point.tag("prediction", 0)

            point.time(datetime.utcnow(), WritePrecision.NS)
            write_api.write(bucket, org, point)

            i+=1


if __name__ == "__main__":
    main()