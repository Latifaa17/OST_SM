from json import loads
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime


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
            point = Point("SWAT_sample")
                    

            for key, val in dict.items():
                    if key != 'Timestamp':
                        point.field(key, float(val))
            point.time(datetime.utcnow(), WritePrecision.NS)
            
            write_api.write(bucket, org, point)
            i+=1
            print("Message sent to influxDB", i)


if __name__ == "__main__":
    main()