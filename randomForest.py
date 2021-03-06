"""
===================================================
Reconocedor de caras por SVM y PCA
===================================================

"""
print(__doc__)



datosAug =[]
labelsAug =[]

carpeta = "D:/Documentos HDD/10mo/TT1/Pruebas mulicategorico/Proyecto del 2018_September_09_21_02_57/"


#radius = 4
#n_points = 8
#nro = 0
#def SVM(carpeta,target_names):
from time import time
import matplotlib.pyplot as pl
import numpy as np
import os
import cv2  
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.decomposition import RandomizedPCA
from sklearn.svm import SVC
from skimage.feature import local_binary_pattern

from sklearn.ensemble import RandomForestClassifier




t0 = time()
folders = os.listdir(carpeta)
for im in folders:
    label =int(im[0])
    Rimagen = carpeta+im
    imagen=cv2.imread(Rimagen)
    image = cv2.cvtColor(imagen,cv2.COLOR_BGR2GRAY)
#        lbp = local_binary_pattern(image, n_points, radius, 'default')
#        im_flat = lbp.ravel() 
    im_flat = image.ravel() 
    im_flat = im_flat.tolist()
    datosAug.append(im_flat)
    labelsAug.append(label)
    
print("total time: ", time()-t0)

datosRostrosA = np.asarray(datosAug)
labelRostrosA = np.asarray(labelsAug)
###############################################################################
#    resizeW = 96
#    resizeH = 130
n_samples =datosRostrosA.shape[0]
print("Shape de rostrosA"+str(datosRostrosA.shape))
np.random.seed(20)

# for machine learning we use the data directly (as relative pixel
# position info is ignored by this model)
n_features = datosRostrosA.shape[1]
# the label to predict is the id of the person

target_names = ["Javier", "Luperta","Jesus"]
target_names = np.asarray(target_names)
n_classes = target_names.shape[0]


print("Total dataset size:")
print("n_samples: %d" % n_samples)
print("n_features: %d" % n_features)
print("n_classes: %d" % n_classes)



###############################################################################

X_train, X_test, y_train, y_test = train_test_split(datosRostrosA, labelRostrosA, test_size=0.2, random_state=15)
###############################################################################
# Compute a PCA (eigenfaces) on the face dataset (treated as unlabeled
# dataset): unsupervised feature extraction / dimensionality reduction
#n_components =  int(X_train.shape[0]*2/4)
n_components = 100
#
print("Extracting the top %d eigenfaces from %d faces" % (n_components, X_train.shape[0]))
t0 = time()
pca = RandomizedPCA(n_components=n_components, whiten=True).fit(X_train)
print("done in %0.3fs" % (time() - t0))

#eigenfaces = pca.components_.reshape((n_components, h, w))


print("Projecting the input data on the eigenfaces orthonormal basis")
t0 = time()
X_train_pca = pca.transform(X_train)
X_test_pca = pca.transform(X_test)
print("done in %0.3fs" % (time() - t0))

   ###########################################################
# Train a SVM classification model


print("Fitting the classifier to the training set")
t0 = time()
param_grid = {
         'C': [500,100,50,10,5,11e3, 5e3, 1e4, 5e4, 1e5,5e5,1e6],
          'gamma': [0.0001, 0.0005, 0.05,0.0007,0.07,0.007,0.006,0.001,0.002,0.003,0.004, 0.005,],
          }
# for sklearn version 0.16 or prior, the class_weight parameter value is 'auto'
clf = GridSearchCV(SVC(class_weight='balanced',probability=True,decision_function_shape = 'ovo'), param_grid, cv = 5)
clf = clf.fit(X_train_pca, y_train)
print("done SVM in %0.3fs" % (time() - t0))
print("Best estimator found by grid search:")
print(clf.best_estimator_)


###############################################################################
# Quantitative evaluation of the model quality on the test set


t0 = time()
param_gridRF = { 
    'n_estimators': [200,300,400,],
    'max_depth': [2,3,4]
}

rdmFor = RandomForestClassifier(n_estimators=400, max_depth=4,max_features='sqrt',
                              random_state=0, n_jobs =4,oob_score = True)
#CV_rfc = GridSearchCV(RandomForestClassifier(n_estimators=100, max_depth=2,max_features='sqrt',
#                              random_state=0, n_jobs =4,oob_score = True), param_grid=param_gridRF)
#CV_rfc.fit(X_train_pca, y_train)
rdmFor.fit(X_train_pca, y_train)

print("Este es el score")
print(rdmFor.oob_score_)
print("Este es el tiempo total con RandomForest: %0.3f" %(time()-t0))
y_predrFor= CV_rfc.predict(X_test_pca)
print("Predicting the people names on the testing set")
t0 = time()
y_pred = clf.predict(X_test_pca)
#from sklearn import cross_validation
#y_prueba = clf.predict()
#cv = cross_validation.ShuffleSplit(np.asarray(y_train).size, n_iter=3,test_size=0.3, random_state=15)
#scores = cross_validation.cross_val_score(clf,X_train,y_train,cv = cv)
#score_mean = np.mean(scores) 
print("done in %0.3fs" % (time() - t0))
print("CM para SVM")
print(classification_report(y_test, y_pred, target_names=target_names))
print(confusion_matrix(y_test, y_pred, labels=range(n_classes)))
print("CM para RandomForest")
print(classification_report(y_test, y_predrFor, target_names=target_names))
print(confusion_matrix(y_test, y_predrFor, labels=range(n_classes)))

#import pickle
#datos = {"modelo":clf, "pca": pca, "target_names": target_names}
#data = open(carpeta+"/archivo_modelo_LBP.pickle",'wb')
#pickle.dump(datos, data)

 
##    return clf, pca   
    
    
    