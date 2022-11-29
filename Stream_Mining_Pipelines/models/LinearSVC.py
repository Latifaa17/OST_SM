import pandas as pd
import pickle

from sklearn.svm import LinearSVC

df = pd.read_csv('../../Kafka/data/Swat_dataset.csv')
df.drop(df.columns[0],axis = 1, inplace=True)

df = df.drop(columns = ['Timestamp'])
df.fillna(0, inplace = True)
dataset = df.values

X = dataset[:,:-1]
y = dataset[:,-1]

clf =LinearSVC()

clf.fit(X, y)
pickle.dump(clf, open('LinearSVC.pkl', 'wb'))
print("Model pickled")