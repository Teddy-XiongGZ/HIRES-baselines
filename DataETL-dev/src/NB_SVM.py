from sklearn import metrics
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from text_preprocessing import EPItem
import numpy as np
import gc, sys, os, psutil
from scipy.sparse import vstack

from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, MaxAbsScaler
from text_preprocessing import getsentences, mapX2epitem

# import pdb

FEATURE_SIZE = 40000


def nb_svm(X, Y, model, result_path, Xt=None,Yt=None):

    # pdb.set_trace()
    if Xt:
        X_train_tmp = X
        Y_train = Y
        X_test = Xt
        Y_test = Yt
    else:
        X_train_tmp, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    print(u'当前进程的内存使用：%.4f GB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024) )
    print(sys.getsizeof(X) / 1024 / 1024 / 1024, 'GB')
    del X, Y
    gc.collect()
    print(sys.getsizeof(Y_train) / 1024 / 1024 / 1024, 'GB')
    del Y_train
    gc.collect()

    tfidfvect = TfidfVectorizer(stop_words='english', max_features=FEATURE_SIZE)
    X_train_data = tfidfvect.fit_transform(getsentences(X_train_tmp))
    X_test_data = tfidfvect.transform(getsentences(X_test))

    if model=='SVM':
        scaler = MaxAbsScaler()
        scaler.fit(X_train_data)
        X_train_data = scaler.transform(X_train_data)
        X_test_data = scaler.transform(X_test_data)

    mapX2epitem(X_train_tmp, X_train_data)
    # del X_train_data
    # gc.collect()
    mapX2epitem(X_test, X_test_data)
    # del X_test_data
    # gc.collect()

    print(u'当前进程的内存使用：%.4f GB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024) )
    if model == 'SVM':
        clf = SVC(kernel='linear', max_iter = 5000, random_state=0)
    if model == 'NB':
        clf = MultinomialNB(alpha=0.1)
    if model == 'RF':
        clf = RandomForestClassifier(random_state=0)
    X_train = vstack([item.getdata() for item in X_train_tmp])

    print(sys.getsizeof(X_train) / 1024 / 1024 / 1024, 'GB')
    Y_train = np.concatenate([item.getalllabel() for item in X_train_tmp], axis=0)
    del X_train_tmp
    gc.collect()
    print("begin to fit")
    clf.fit(X_train, Y_train)
    print("begin to predict")
    Y_predict = []
    for item in X_test:
        pred = clf.predict(item.getdata())
        pred = np.argmax(np.bincount(pred))
        Y_predict.append(pred)
    #Y_predict = clf.predict(X_test)

    confusion_matrix = metrics.confusion_matrix(Y_test, Y_predict)
    #acc = metrics.accuracy_score(Y_test, Y_predict)
    #auc = metrics.roc_auc_score(Y_test, Y_predict)
    #f1_score = metrics.f1_score(Y_test, Y_predict)

    with open(result_path, 'a') as f:
        print(model)
        print(model, file=f)
        print('feature size:', X_train.shape[1])
        print('feature size:{}'.format(X_train.shape[1]), file=f)
        #print("Accuracy on test set is %f, AUC on test set is %f, F1_score on test set is %f" % (acc, auc, f1_score))
        #print("Accuracy on test set is %f, AUC on test set is %f, F1_score on test set is %f" % (acc, auc, f1_score), file=f)
        print(confusion_matrix)
        print(confusion_matrix, file=f)

