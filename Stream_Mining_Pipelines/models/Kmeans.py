from sklearn.cluster import KMeans
import pickle

import pandas as pd


df = pd.read_csv('Swat_preprocessed.csv')
#df_train = df.tail(200000)
#df_train = df_train.drop(columns = ['Timestamp', 'Unnamed: 0', 'Normal/Attack'])
#df_train  = df.tail(200000)
df_train = df
df_train = df_train[['FIT101', 'AIT203', 'DPIT301']]

kmeans = KMeans(n_clusters=2).fit(df_train)

with open('kmeans.pickle', 'wb') as f:
    pickle.dump(kmeans, f)