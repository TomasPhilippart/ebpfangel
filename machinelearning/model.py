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


def refit_strategy(cv_results):

    # print results
    df = pd.DataFrame(cv_results)
    df = df.sort_values(by=["rank_test_recall"])
    print(df[["params", "rank_test_recall", "rank_test_balanced_accuracy", "mean_test_recall", "mean_test_balanced_accuracy"]])

    return df["rank_test_recall"].idxmin()


def train(file: str):
    X_train = pd.read_csv(FILES['training']['data'])
    y_train = get_labels(X_train, file)

    # save the features in the training dataset
    dump(X_train.columns, FILES['model']['features'])

    # scale the training data
    scaler = StandardScaler().fit(X_train)
    dump(scaler, FILES['model']['scaler'])
    
    scaler.transform(X_train)

    # SVM classifier

    # grid search SVM hyper parameters
    class_weight = [{1: w} for w in np.linspace(5, 500, 20)]
    param_grid = dict(class_weight=class_weight)

    scores = ['recall', 'balanced_accuracy']
    grid = GridSearchCV(svm.SVC(), param_grid=param_grid, scoring=scores, refit=refit_strategy)
    grid.fit(X_train, y_train)

    best_classifier = grid.best_estimator_

    dump(best_classifier, FILES['model']['model'])

    score = best_classifier.score(X_train, y_train)
    print("Training score: %f" % score)


def test(file: str):
    X_test = pd.read_csv(FILES['testing']['data'])
    y_test = get_labels(X_test, file)

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

    # ROC Curve
    roc_display = RocCurveDisplay.from_estimator(classifier, X_test, y_test)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    cm_display.plot(ax=ax1)
    roc_display.plot(ax=ax2)
    plt.savefig(FILES['model']['results'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', action='store_true', help='Train a new model')
    parser.add_argument('--test', action='store_true', help='Test an existing model')
    parser.add_argument('--labels', default='file', choices=['file','data'], help='Read labels from file or data')
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


if __name__ == '__main__':
    main()
