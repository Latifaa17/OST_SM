import pandas as pd
import numpy as np
from scipy import stats
#from sklearn.preprocessing import StandardScaler

    

def drop_constant_columns(df):
    result = df.copy()
    for column in df.columns:
        if len(df[column].unique()) == 1:
            result = result.drop(column,axis=1)
    return result


def drop_corr_features(df):
    corr_matrix = df.corr().abs()
    # Select upper triangle of correlation matrix
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))
    # Find features with correlation greater than 0.95
    to_drop = [column for column in upper.columns if any(upper[column] > 0.95)]
    # Drop features 
    df.drop(to_drop, axis=1, inplace=True)
    return df

def standardize(df):
    cols = list(df.columns)
    cols.remove("Normal/Attack")
    cols.remove("Timestamp")
    #df[cols] = StandardScaler().fit_transform(df[cols])
    df[cols] = stats.zscore(df[cols])
    return df


if __name__=="__main__":
  
    #Loading the dataset
    path = './data/SWaT_Dataset_Attack_v0.csv'
    df = pd.read_csv(path)

    #Fixing Column Labels
    df.columns=df.columns.str.strip()

    #Encoding target 
    df['Normal/Attack'] = df['Normal/Attack'].map({'A ttack':1,'Normal':0,'Attack':1})

    #Saving the data to use for streaming (keeping all features)
    df.to_csv('../Kafka/data/Swat_dataset.csv') 

    #Remove Constant Features
    df = drop_constant_columns(df)

    #Remove Correlated Features
    df = drop_corr_features(df)

    #Standardization
    #df=standardize(df)

    #Saving preprocessed data
    df.to_csv('./data/Swat_preprocessed.csv') 

    print('\n Successfully preprocessed the data')
