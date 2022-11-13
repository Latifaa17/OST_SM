import pandas as pd
import numpy as np

    

def drop_constant_columns(df):
    result = df.copy()
    for column in df.columns:
        if len(df[column].unique()) == 1:
            result = result.drop(column,axis=1)
    return result



if __name__=="__main__":
  
    #Loading the dataset
    path = './data/SWaT_Dataset_Attack_v0.xlsx'
    df = pd.read_excel(path, skiprows=[0])

    #Fixing Column Labels
    df.columns=df.columns.str.strip()

    #Encoding target 
    df['Normal/Attack'] = df['Normal/Attack'].map({'A ttack':1,'Normal':0,'Attack':1})

    #Saving the data to use for streaming (keeping all features)
    df.to_csv('../Kafka/data/Swat_dataset.csv') 

    #Remove Constant Features
    df = drop_constant_columns(df)

    #Remove Correlated Features


    #Standardization


    #split test and train







  