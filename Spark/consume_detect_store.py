from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
#from pyspark.sql.session import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

from influxDB_writer import InfluxDBWriter
from influxdb_client import InfluxDBClient

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime

if __name__=="__main__":
    os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 consume_detect_store.py'

    # Spark Instance
    # spark = SparkSession.builder.master('local[*]').getOrCreate()
    spark = (
        SparkSession.builder.appName("Kafka Pyspark Streaming")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel('ERROR')

    #spark = SparkSession.builder.getOrCreate()
    # spark = SparkSession \
    #     .builder \
    #     .appName("Csv_Reader").getOrCreate()

    # Define an input stream
    cols = [ 'Timestamp','FIT101','LIT101', 'MV101','P101','P102', 'AIT201','AIT202','AIT203','FIT201', 'MV201', 'P201', 
    'P202','P203', 'P204','P205','P206','DPIT301','FIT301','LIT301','MV301','MV302', 'MV303','MV304','P301','P302','AIT401',
    'AIT402','FIT401','LIT401','P401','P402','P403','P404','UV401','AIT501','AIT502','AIT503','AIT504','FIT501','FIT502','FIT503',
    'FIT504','P501','P502','PIT501','PIT502','PIT503','FIT601','P601','P602','P603','Normal/Attack']

    fields = [StructField(col_name, StringType(), True) for col_name in cols]
    schema = StructType(fields)

    # Read stream from json and fit schema
    inputStream = spark\
        .readStream\
        .format("kafka")\
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "SWAT")\
        .option("startingOffsets", "latest")\
        .load()

    inputStream = inputStream.select(col("value").cast("string").alias("data"))
    inputStream.printSchema()

    # Delete previous row | debug |
    #for m in ['ocsvm', 'kmeans', 'iso_log', 'dbcan']:
        #client = InfluxDBClient(url="http://influxdb:8086", token="iJHZR-dq4I5LIpFZCc5bTUHx-I7dyz29ZTO-B4W5DpU4mhPVDFg-aAb2jK4Vz1C6n0DDb6ddA-bJ3EZAanAOUw==", org="primary")
        #delete_api = client.delete_api()
        #start = "2010-01-01T00:00:00Z"
        #measurement = m
        #delete_api.delete(start, datetime.now(), f'_measurement="{measurement}"', bucket="swat", org="primary")
    #print("> Deleted")

    # Read stream and process
    print(f"> Reading the stream and storing ...")
    query = (inputStream
        .writeStream
        .outputMode("append")
        .foreach(InfluxDBWriter())
        .option("checkpointLocation", "checkpoints")
        .start())

        

    spark.streams.awaitAnyTermination()