# from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.model_selection import GridSearchCV
# from sklearn.decomposition import PCA
# from sklearn.svm import SVC

import pandas as pd
import numpy as np
import tqdm
import pickle
import warnings

warnings.filterwarnings("ignore") 

def recall_attacked(y_test,y_pred):
    TP,FN,FP,TN = confusion_matrix(y_test,y_pred,labels=[1,0]).flatten()
    recall = TP/(TP+FN)
    return recall

def grid_search_LR(C_list,X,y):
    '''
    For calculating recall of the attack class
    '''
    X_train,X_test,y_train,y_test = train_test_split(X,y,random_state=0)
    scores = []
    for C in tqdm.tqdm(C_list):
        lr = LogisticRegression(C=C)
        y_pred = lr.fit(X_train,y_train).predict(X_test)
        scores.append(recall_attacked(y_test,y_pred))
        
    scores = np.array(scores)
    best_C = C_list[np.argmax(scores)]
    best_score = np.max(scores)
    return best_C,best_score,scores

# Data reading
df = pd.read_csv('../../Kafka/data/Swat_dataset.csv',index_col=0)
golden_features = ['AIT402','MV304','AIT203','LIT101','LIT301','P102',
                    'AIT503','AIT504','AIT401','AIT201','P201','FIT101',
                    'P101','DPIT301','PIT502'] 
df_golden = df [golden_features+['Normal/Attack']]
X = df_golden.values[:,:-1]
y = df_golden.values[:,-1]
X_train,X_test,y_train,y_test = train_test_split(X,y)

# Choosing the best parameter C
# hyper_paras = {'C':np.linspace(0.1,1.0,10)}
# grid = GridSearchCV(LogisticRegression(),hyper_paras,)
# grid.fit(X_train,y_train)
# C = grid.best_params_

C_list = np.linspace(0.1,1.0,10)
best_C,best_score,scores = grid_search_LR(C_list,X,y)

print(scores)
print('The best C is',best_C,'with the recall on class 1',best_score)

lr = LogisticRegression(C=best_C)
lr.fit(X,y)
pickle.dump(lr, open('LogisticRegression.pkl', 'wb'))
print('Model saved')