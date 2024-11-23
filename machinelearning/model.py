#!/usr/bin/python3

#   DISCLAIMER
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

import argparse
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.inspection import permutation_importance
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay
import matplotlib.pyplot as plt
from joblib import dump, load

# filenames
DATADIR = '../data/'
FILES = {
    'training': {
        'data':     DATADIR + 'training_data.csv',
        'labels':   DATADIR + 'training_labels.csv',
    },
    'testing': {
        'data':     DATADIR + 'testing_data.csv',
        'labels':   DATADIR + 'testing_labels.csv',
    },
    'model': {
        'features': DATADIR + 'features.joblib',
        'scaler':   DATADIR + 'scaler.joblib',
        'model':    DATADIR + 'model.joblib',
        'results':  DATADIR + 'results.png',
        'analysis': DATADIR + 'analysis.png',
    },
}

# get labels
def get_labels(df: pd.DataFrame, file: str):
    if file:
        pids = pd.read_csv(file)
        pids['y'] = 1
        return df.join(pids.set_index('PID'), on='PID').fillna(0)['y']
    else:
        return df['C_max'].map(lambda x: 1 if x > 100 else 0)

def best_features_linear(coef, feature_names):
    abs_coef = abs(*coef)
    importance, feature_names = zip(*sorted(zip(abs_coef, feature_names)))
    plt.barh(range(len(feature_names)), importance, align='center')
    plt.yticks(range(len(feature_names)), feature_names)
    plt.savefig(FILES['model']['analysis'])

def best_features_rbf(perm_importance, feature_names):
    features = np.array(feature_names)
    sorted_idx = perm_importance.importances_mean.argsort()
    plt.barh(features[sorted_idx], perm_importance.importances_mean[sorted_idx])
    plt.xlabel("Permutation Importance")
    plt.savefig(FILES['model']['analysis'])

def refit_strategy(cv_results):
    # print results
    df = pd.DataFrame(cv_results)
    df = df.sort_values(by=["rank_test_recall"])
    pd.set_option('display.max_colwidth', 100)
    print(df[["params", "rank_test_recall", "rank_test_balanced_accuracy", "mean_test_recall", "mean_test_balanced_accuracy"]])

    # select the highest ranked
    return df["rank_test_recall"].idxmin()

def train(file: str):
    X_train = pd.read_csv(FILES['training']['data'])
    y_train = get_labels(X_train, file)

    # get rid of PID column, dont use for training
    X_train.drop(columns=['PID'], inplace=True)

    # save the features in the training dataset
    dump(X_train.columns, FILES['model']['features'])

    # scale the training data
    scaler = StandardScaler().fit(X_train)
    dump(scaler, FILES['model']['scaler'])
    
    scaler.transform(X_train)

    # SVM classifier

    # grid search SVM hyper parameters
    kernel = ['rbf'] # 'rbf' or 'linear'
    class_weight = [{1: w} for w in np.linspace(10, 200, 10)]
    C = np.logspace(-1, 0, 10)
    param_grid = dict(class_weight=class_weight, kernel=kernel, C=C)
    scores = ['recall', 'balanced_accuracy']
    grid = GridSearchCV(svm.SVC(max_iter=1_000_000), param_grid=param_grid, scoring=scores, refit=refit_strategy)
    grid.fit(X_train, y_train)

    best_classifier = grid.best_estimator_

    dump(best_classifier, FILES['model']['model'])

    score = best_classifier.score(X_train, y_train)
    print("Training score: %f" % score)

    feature_names = X_train.columns.to_list()
    if kernel[0] == 'linear':
        best_features_linear(best_classifier.coef_, feature_names)
    elif kernel[0] == 'rbf':
        best_features_rbf(permutation_importance(best_classifier, X_train, y_train), feature_names)


def test(file: str):
    X_test = pd.read_csv(FILES['testing']['data'])
    y_test = get_labels(X_test, file)

    # get rid of PID column, dont use for training
    X_test.drop(columns=['PID'], inplace=True)

    # make sure to use the same features as for training
    training_features = load(FILES['model']['features'])
    test_features = X_test.columns
    # drop new features
    X_test.drop(columns=[f for f in test_features if f not in training_features], inplace=True)
    # add missing features
    for f in training_features:
        if f not in test_features:
            X_test[f] = 0

    # scale the test data
    scaler = load(FILES['model']['scaler'])
    scaler.transform(X_test)

    # predict with the previously trained classifier
    classifier = load(FILES['model']['model'])

    score = classifier.score(X_test, y_test)
    print("Testing score: %f" % score)

    # confusion matrix
    cm_display = ConfusionMatrixDisplay.from_estimator(classifier, X_test, y_test)

    # ROC Curve -> should use precision-recall curve instead
    roc_display = RocCurveDisplay.from_estimator(classifier, X_test, y_test)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    cm_display.plot(ax=ax1)
    roc_display.plot(ax=ax2)
    plt.savefig(FILES['model']['results'])

def pred():
    X_test = pd.read_csv(FILES['testing']['data'])
    #y_test = get_labels(X_test, file)
    pidarr = X_test['PID']

    # get rid of PID column, dont use for training
    X_test.drop(columns=['PID'], inplace=True)

    # make sure to use the same features as for training
    training_features = load(FILES['model']['features'])
    test_features = X_test.columns
    # drop new features
    X_test.drop(columns=[f for f in test_features if f not in training_features], inplace=True)
    # add missing features
    for f in training_features:
        if f not in test_features:
            X_test[f] = 0

    # scale the test data
    scaler = load(FILES['model']['scaler'])
    scaler.transform(X_test)

    # predict with the previously trained classifier
    classifier = load(FILES['model']['model'])

    prediction = pd.DataFrame({'PID': pidarr, 'Pred': classifier.predict(X_test)})
    #pd.set_option('display.max_rows', len(prediction))
    print(prediction.to_string())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', action='store_true', help='Train a new model')
    parser.add_argument('--test', action='store_true', help='Test an existing model')
    parser.add_argument('--labels', default='file', choices=['file','data'], help='Read labels from file or data')
    parser.add_argument('--predict', action='store_true', help='Predict using an existing model')
    args = parser.parse_args()

    if args.train:
        if args.labels == 'file':
            train(file=FILES['training']['labels'])
        else:
            train(file=None)
    
    if args.test:
        if args.labels == 'file':
            test(file=FILES['testing']['labels'])
        else:
            test(file=None)

    if args.predict:
        pred()


if __name__ == '__main__':
    main()
