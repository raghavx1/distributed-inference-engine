from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
import numpy as np
import pickle, os

MODEL_PATH = "model.pkl"

def train_and_save():
    X, y = load_iris(return_X_y=True)
    clf = RandomForestClassifier(n_estimators=50)
    clf.fit(X, y)
    # Write to temp file first, then rename — atomic on all OS
    tmp_path = MODEL_PATH + ".tmp"
    with open(tmp_path, "wb") as f:
        pickle.dump(clf, f)
    os.replace(tmp_path, MODEL_PATH)
    print("Model trained and saved.")

def load_model():
    if not os.path.exists(MODEL_PATH):
        train_and_save()
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def predict(model, features: list):
    arr = np.array(features).reshape(1, -1)
    return int(model.predict(arr)[0])

if __name__ == "__main__":
    train_and_save()