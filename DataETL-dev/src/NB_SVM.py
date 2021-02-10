from sklearn import metrics
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

def nb_svm(X, Y, model, result_path):

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    if model == 'SVM':
        clf = SVC(kernel='linear')
    if model == 'NB':
        clf = MultinomialNB(alpha=0.1)
    clf.fit(X_train, Y_train)
    Y_predict = clf.predict(X_test)

    confusion_matrix = metrics.confusion_matrix(Y_test, Y_predict)
    acc = metrics.accuracy_score(Y_test, Y_predict)
    auc = metrics.roc_auc_score(Y_test, Y_predict)
    f1_score = metrics.f1_score(Y_test, Y_predict)

    with open(result_path, 'a') as f:
        print("Accuracy on test set is %f, AUC on test set is %f, F1_score on test set is %f" % (acc, auc, f1_score))
        print("Accuracy on test set is %f, AUC on test set is %f, F1_score on test set is %f" % (acc, auc, f1_score), file=f)
        print(confusion_matrix)
        print(confusion_matrix, file=f)

