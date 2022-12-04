import pandas as pd
import pickle

from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('../../Kafka/data/Swat_dataset.csv')
df = df.drop(columns = ['Timestamp', 'Unnamed: 0'])
df.fillna(0, inplace = True)
#df  = df.tail(200000)
dataset = df.values

X = dataset[:,:-1]
y = dataset[:,-1]

clf =LinearSVC(random_state=0, tol=1e-5)
clf.fit(X, y)
pickle.dump(clf, open('LinearSVC.pkl', 'wb'))

