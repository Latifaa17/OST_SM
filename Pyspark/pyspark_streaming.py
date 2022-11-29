from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *


import pandas as pd




if __name__=="__main__":
    
    #os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 pyspark_streaming.py'

    spark = (
        SparkSession.builder.appName("Pyspark Streaming")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel('ERROR')

    cols = ['Index', 'Timestamp','FIT101','LIT101', 'MV101','P101','P102', 'AIT201','AIT202','AIT203','FIT201', 'MV201', 'P201', 
    'P202','P203', 'P204','P205','P206','DPIT301','FIT301','LIT301','MV301','MV302', 'MV303','MV304','P301','P302','AIT401',
    'AIT402','FIT401','LIT401','P401','P402','P403','P404','UV401','AIT501','AIT502','AIT503','AIT504','FIT501','FIT502','FIT503',
    'FIT504','P501','P502','PIT501','PIT502','PIT503','FIT601','P601','P602','P603','Normal/Attack']

    fields = [StructField(col_name, StringType(), True) for col_name in cols]
    csv_schema = StructType(fields)

    
    df = spark.readStream.format('csv').schema(csv_schema).option('header','true').option('delimiter',',').load('./Swat_dataset*.csv')
    df.printSchema()

    df_final = df.select("Index","MV301","AIT501","PIT503","Normal/Attack")

    def f(row):
        #print(row)
        row_dict = row.asDict()
        print(row_dict)
        df = pd.DataFrame(row_dict, index=[0])
        print("***************")
        

    query = df_final.writeStream.outputMode("append").foreach(f).option("checkpointLocation", "checkpoints").start().awaitTermination()
    
    # df_final.select(to_json(struct([col(c).alias(c) for c in df_final.columns])).alias("value"))\
    # .writeStream.format("kafka").outputMode("append").option("kafka.bootstrap.servers", "localhost:9092") \
    # .option("topic", "test") \
    # .option("checkpointLocation", "checkpoints").start().awaitTermination()