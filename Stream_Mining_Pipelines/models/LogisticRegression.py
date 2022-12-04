# from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix,f1_score
from sklearn.model_selection import GridSearchCV
# from sklearn.decomposition import PCA
# from sklearn.svm import SVC

import pandas as pd
import numpy as np
import tqdm
import pickle
import warnings

warnings.filterwarnings("ignore") 


def grid_search_LR(C_list,weight_list,X,y):
    '''
    For grid searching the best parameter based on f1 of the class 1
    C_list: the parameter C candidates in LogisticRegression
    weight_list: because the dataset's class normal is far overweighed, give more weight on the class attacked to avoid biasing from model, and give more "chance" to minority class attacked 
    '''
    X_train,X_test,y_train,y_test = train_test_split(X,y,stratify=y)
    best_C = C_list[0]
    best_weight = weight_list[0]
    best_score = 0
    for C in tqdm.tqdm(C_list):
        for weight in weight_list:
            lr = LogisticRegression(C=C,class_weight={0:1-weight, 1:weight})
            y_pred = lr.fit(X_train,y_train).predict(X_test)
            score = f1_score(y_test,y_pred,pos_label=1)
            print('C:',C,',weight:',weight,',score:',score)
            if score > best_score:
                best_C = C
                best_weight = weight
                best_score = score
    return best_C,best_weight,best_score

# Data reading
# df = pd.read_csv('../../Kafka/data/Swat_dataset.csv',index_col=0)
df = pd.read_csv('../data/Swat_preprocessed.csv',index_col=0)  # Use the training set
golden_features = ['AIT402','MV304','AIT203','LIT101','LIT301','P102',
                    'AIT503','AIT504','AIT401','AIT201','P201','FIT101',
                    'P101','DPIT301','PIT502'] 
df_golden = df [golden_features+['Normal/Attack']]
X = df_golden.values[:,:-1]
y = df_golden.values[:,-1]
# Didn't normailization
C_list = [0.3,1,3,10,15,30,50]
weight_list = np.linspace(0.5,1.0,10)
best_C,best_weight,best_score = grid_search_LR(C_list,weight_list,X,y)

print('The best C is',best_C,',the best weight is',best_weight,'with the f1 on class 1',best_score)

lr = LogisticRegression(C=best_C,class_weight={0:1-best_weight, 1:best_weight})
lr.fit(X,y)

pickle.dump(lr, open('LogisticRegression.pkl', 'wb'))
print('Model saved')