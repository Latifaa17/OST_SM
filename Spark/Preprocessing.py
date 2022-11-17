import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
    

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

    #Separate data from target value
    X = df.iloc[ :-1].values
    y = df.iloc[ -1].values
    #Standardization
    scale= StandardScaler()
    X = scale.fit_transform(X) 

    #encoding target value
    le = preprocessing.LabelEncoder()
    le.fit(y)
    list(le.classes_)
    y = le.transform(y)
    
    #split test and train
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, stratify=True, test_size=0.2)