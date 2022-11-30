import pandas as pd
import pickle

from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('../../Kafka/data/Swat_dataset.csv')

features=['FIT101','LIT101','P101','P102','AIT203','P201','DPIT301','FIT301',
    'LIT301','MV302','MV304','AIT402','LIT401','AIT501','AIT502','AIT503','PIT502']

df = df[features].astype(float)
df.fillna(0, inplace = True)
#df  = df.iloc[:15000]
dataset = df.values

X = dataset[:,:-1]
y = dataset[:,-1]

clf =LinearSVC(random_state=0, tol=1e-5)
clf.fit(X, y)
pickle.dump(clf, open('LinearSVC.pkl', 'wb'))
print("Model Pickled")
