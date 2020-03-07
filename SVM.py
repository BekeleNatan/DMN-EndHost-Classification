from ProfileBuilder import Graphlet
from joblib import dump, load
from CustomRWKernel import compute_random_walk_kernel


from sklearn import svm, datasets
import networkx as nx
import numpy as np


from grakel.utils import graph_from_networkx
from grakel.kernels import RandomWalkLabeled
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

graphlet = Graphlet('data/annotated-trace.csv')

X = graphlet.profile_graphlets
y = graphlet.get_graphlets_label()
y =[0 if el=='normal' else 1 for el in y]

act = graphlet.activity_graphlets

G = graph_from_networkx(X, node_labels_tag='type')
G = list(G)

# Splits the dataset into a training and a test set
G_train, G_test, y_train, y_test = train_test_split(G, y, test_size=0.3, random_state=42)


gk = RandomWalkLabeled(n_jobs= 4)
K_train = gk.fit_transform(G_train)
K_test = gk.transform(G_test)

# Uses the SVM classifier to perform classification
clf = SVC(kernel="precomputed")
clf.fit(K_train, y_train)
y_pred = clf.predict(K_test)

# Computes and prints the classification accuracy
acc = accuracy_score(y_test, y_pred)
print(acc)


dump(clf, 'svm_rand_walk.joblib') 