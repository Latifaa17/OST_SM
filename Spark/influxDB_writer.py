from pyspark.sql import Row
from sklearn.preprocessing import MinMaxScaler

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from skmultiflow.drift_detection.adwin import ADWIN

import pickle
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime

class InfluxDBWriter:
    def __init__(self, approaches, cloud=False):
        self.url = "http://influxdb:8086"
        self.token = "PLVcjlNS8ffprnsg05h3-9rJA1Xxc3dojPvMKsWypVM3wt_uvstaEdbiYPZNzo5z0s29MnQDZaouKQ3-_QyeHQ=="
        self.org = "SWAT"
        self.bucket = "SWAT"
        self.approaches = approaches
        if cloud: # Connect to InfluxDB Cloud
            self.client = InfluxDBClient(
                url="<cloud.url>", 
                token="<cloud.token>", 
                org="<cloud.org>"
            )
        else: # Connect to a local instance of InfluxDB
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        # Create a writer API
        self.write_api = self.client.write_api()
    
    def standardize(df):
        cols = list(df.columns)
        cols.remove("Normal/Attack")
        cols.remove("Timestamp")
        #df[cols] = StandardScaler().fit_transform(df[cols])
        df[cols] = stats.zscore(df[cols])
        return df

    def _preprocess(self, row):
        # Row to Dict
        row_dict = json.loads(row)
        # Dict to Dataframe
        dataframe = pd.DataFrame(row_dict, index=[0])
        # Rename columns
        cols = list(dataframe.columns)
        #cols[1:] = [i.split('_')[1] for i in cols[1:]]
        dataframe.columns = cols
        # Drop unecessary columns
        keep=['Timestamp','FIT101','LIT101','P101','P102','AIT201','AIT202','AIT203','P201','P204',
              'DPIT301','FIT301','LIT301','MV301','MV302','MV303','MV304','AIT401','AIT402','LIT401','P403',
              'AIT501','AIT502','AIT503','AIT504','PIT502','FIT601','P602','Normal/Attack']
        dataframe=dataframe.drop(columns=[col for col in dataframe if col not in keep], inplace=True)

        # Extract continuous data
        continuous = dataframe[keep]
        # Normalize
        data_norm=standardize(continuous)
        return np.asarray(data_norm)
    
    def process(self, row):
        try:
            self.write_api.write(bucket=self.bucket, org=self.org, record=self._row_to_point(row["data"]))
        except Exception as ex:
            print(f"[x] Error {str(ex)}")

    def _row_to_point(self, row):
        # Load to dictionary
        row_dict = json.loads(row)
        change = 0.0
        points = []
        # String to timestamp
        timestamp = datetime.strptime(row_dict["Timestamp"], "%d/%m/%Y %H:%M:%S.%f %p")
        print(f"> Processing {timestamp}")
        # Handle multiple approaches
        
        approach = 'ADWIN'
            # Create a data point
        point = Point(approach)
            # Add fields to the point
        row_list = []
        for key, val in row_dict.items():
            if key != 'Timestamp':
                point.field(key, float(val))
                row_list.append(float(val))
            # Predict
        if self._is_change(row, approach)[0] == True:
            point.field('attack', np.mean(row_list))
        else:
            point.field('attack', False)
            # Add timestamp
        point.time(timestamp)
        return point
    
    def _is_change(self, row, approach):
        #import ADWIN_model
        #model = pickle.load(open(f'./models/{model}', 'rb'))
        model=ADWIN()
        # Detect change
        preds = model.fit_predict(self._preprocess(row))
        model.add_element(self._preprocess(row))
        if model.detected_change():
            print('Change detected in data: ' + str(self._preprocess(row)))
      