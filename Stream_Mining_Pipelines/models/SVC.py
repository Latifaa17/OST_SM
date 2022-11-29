import pandas as pd
import pickle
from time import time 
from models import *
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV

df = pd.read_csv('../../Kafka/data/Swat_dataset.csv')
df.drop(df.columns[0],axis = 1, inplace=True)

df = df.drop(columns = ['Timestamp'])
#df.fillna(0, inplace = True)
dataset = df.values

X = dataset[:,:-1]
y = dataset[:,-1]

clf =SVC(random_state=0, tol=1e-5)

parameters = {
    
    "svc__C" : [0.1,1, 10, 100],
    "svc__gamma":[1,0.1,0.01,0.001],
    "svc__kernel": ['rbf', 'poly', 'sigmoid',"linear"],

}


grid_search = GridSearchCV(clf, parameters, n_jobs=-1, verbose=1)

print("Performing grid search...")
print("pipeline:", [name for name, _ in clf.steps])
print("parameters:")
print(parameters)
t0 = time()
grid_search.fit(X, y)
print("done in %0.3fs" % (time() - t0))
print()

print("Best score: %0.3f" % grid_search.best_score_)
print("Best parameters set:")
best_parameters = grid_search.best_estimator_.get_params()
for param_name in sorted(parameters.keys()):
    print("\t%s: %r" % (param_name, best_parameters[param_name]))

# pickle.dump(grid_search.best_estimator_ , open('LinearSVC.pkl', 'wb'))
# print("Model pickled")