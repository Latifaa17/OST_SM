from json import loads
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
from river import drift

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

        drift_PIT502 = drift.HDDM_A()
        drift_FIT101 =drift.HDDM_A()

        for message in consumer:
            #print(f"{message.value}")

            dict = message.value

            point = Point("HDDM_A_PIT502")
            drift_PIT502.update(float(dict["PIT502"]))
            if drift_PIT502.drift_detected:
                # The drift detector indicates after each sample if there is a drift in the data
                print(f'Change detected at index {i}, col: PIT502')
                point.field("prediction", 1)
                point.tag("prediction", 1)

            else:
                point.field("prediction", 0)
                point.tag("prediction", 0)

            
            for key, val in dict.items():
                if key != 'Timestamp':
                    point.field(key, float(val))
                if key=="label":
                    point.tag(key, float(val))

            point.time(datetime.utcnow(), WritePrecision.NS)
            write_api.write(bucket, org, point)

            
            point2 = Point("HDDM_A_FIT101")
            drift_FIT101.update(float(dict["FIT101"]))
            if drift_FIT101.drift_detected:
                # The drift detector indicates after each sample if there is a drift in the data
                print(f'Change detected at index {i}, col: FIT101')
                point2.field("prediction", 1)
                point2.tag("prediction", 1)

            else:
                point2.field("prediction", 0)
                point2.tag("prediction", 0)

            
            for key, val in dict.items():
                    if key != 'Timestamp':
                        point2.field(key, float(val))
                    if key=="label":
                        point2.tag(key, float(val))

            point2.time(datetime.utcnow(), WritePrecision.NS)
            write_api.write(bucket, org, point2)

            i+=1
            #print("Message sent to influxDB", i)

if __name__ == "__main__":
    main()