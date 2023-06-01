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
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay
import matplotlib.pyplot as plt
from joblib import dump, load

# filenames
TRAINING_FILENAME   = 'training_data.csv'
TESTING_FILENAME    = 'testing_data.csv'
FEATURES_FILENAME   = 'features.joblib'
SCALER_FILENAME     = 'scaler.joblib'
CLASSIFIER_FILENAME = 'classifier.joblib'
DISPLAY_FILENAME    = 'display.png'

# CAUTION !!
# this should be provided by the user - using C_max is a trick
def get_labels(df):
    return df['C_max'].map(lambda x: 1 if x > 100 else 0)


def train():
    X_train = pd.read_csv(TRAINING_FILENAME)
    y_train = get_labels(X_train)

    # save the features in the training dataset
    dump(X_train.columns, FEATURES_FILENAME)

    # scale the training data
    scaler = StandardScaler().fit(X_train)
    dump(scaler, SCALER_FILENAME)
    
    scaler.transform(X_train)

    # SVM classifier
    # classifier = svm.SVC(class_weight={1: 10}) # compensate for imbalance
    classifier = svm.SVC(gamma=0.2) # alternative
    classifier.fit(X_train, y_train)
    dump(classifier, CLASSIFIER_FILENAME)

    score = classifier.score(X_train, y_train)
    print("Training score: %f" % score)


def predict():
    X_test = pd.read_csv(TESTING_FILENAME)
    y_test = get_labels(X_test)

    # make sure to use the same features as for training
    training_features = load(FEATURES_FILENAME)
    test_features = X_test.columns
    # drop new features
    X_test.drop(columns=[f for f in test_features if f not in training_features], inplace=True)
    # add missing features
    for f in training_features:
        if f not in test_features:
            X_test[f] = 0

    # scale the test data
    scaler = load(SCALER_FILENAME)
    scaler.transform(X_test)

    # predict with the previously trained classifier
    classifier = load(CLASSIFIER_FILENAME)

    score = classifier.score(X_test, y_test)
    print("Testing score: %f" % score)

    # confusion matrix
    cm_display = ConfusionMatrixDisplay.from_estimator(classifier, X_test, y_test)

    # ROC Curve
    ax = plt.gca()
    roc_display = RocCurveDisplay.from_estimator(classifier, X_test, y_test)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    cm_display.plot(ax=ax1)
    roc_display.plot(ax=ax2)
    plt.savefig(DISPLAY_FILENAME)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='predict', choices=['train', 'predict'], help='either train a new model or predict with the existing one')
    parser.add_argument('--labels', help='?? provide labels via file or formula ??')
    args = parser.parse_args()
    
    if args.mode == "train":
        train()
        predict()
    elif args.mode == "predict":
        predict()


if __name__ == '__main__':
    main()
