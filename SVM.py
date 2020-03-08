from ProfileBuilder import Graphlet
from joblib import dump, load
from CustomRWKernel import compute_random_walk_kernel


from sklearn import svm, datasets
import networkx as nx
import numpy as np
import pickle

from grakel.utils import graph_from_networkx
from grakel.kernels import RandomWalkLabeled
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix


def main():
    graphlet = Graphlet('data/annotated-trace.csv')
    graplet_test = Graphlet('data/not-annotated-trace.csv', test=True)
    

    X = graphlet.profile_graphlets
    y = graphlet.get_graphlets_label()
    y =[0 if el=='normal' else 1 for el in y]
  
    X_test = graplet_test.profile_graphlets
    
    
  
    train = list(graph_from_networkx(X, node_labels_tag='type'))
    G_test = list(graph_from_networkx(X_test, node_labels_tag='type'))

    # Splits the dataset into a training and a validation set
    G_train, G_val, y_train, y_val = train_test_split(train, y, test_size=0.1, random_state=42)


    gk = RandomWalkLabeled(n_jobs= 4)
    K_train = gk.fit_transform(train)
    K_val = gk.transform(G_val)
    pickle.dump(K_train, open( "k_train.p", "wb" ) )
    pickle.dump(K_val, open( "k_val.p", "wb" ) )
    pickle.dump(gk, open("gk.p", "wb"))

    # Uses the SVM classifier to perform classification
    clf = SVC(kernel="precomputed")
    clf.fit(K_train, y)
   
    y_pred = clf.predict(K_val)

    # Computes and prints the classification accuracy
    print(acc)
    dump(clf, 'svm_rand_walk.joblib') 
    
    K_test = gk.transform(G_test)
    y_test_pred = clf.predict(K_test)
    
    print(y_test_pred)
    pickle.dump(K_test, open( "k_test.p", "wb" ) )
  
    
if __name__ == "__main__":
    main()