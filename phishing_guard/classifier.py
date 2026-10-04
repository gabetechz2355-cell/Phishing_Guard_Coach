"""Train, save, and load the TF-IDF + logistic regression phishing classifier.

Think of a mail clerk who never reads for meaning and only keeps a tally
sheet. TF-IDF decides which words stand out in an email; logistic regression
learns how many points each word is worth and turns the total into a
probability. The pipeline and metrics follow PLAN.md's Classifier section.
"""

import json
import random
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

from .config import DATA_DIR, MODEL_PATH

CSV_PATH = DATA_DIR / "phishing_email.csv"
HOLDOUT_PATH = DATA_DIR / "kaggle_holdout.json"


def train_and_save(csv_path: Path = CSV_PATH, model_path: Path = MODEL_PATH,
                   holdout_path: Path = HOLDOUT_PATH, seed: int = 42) -> dict:
    """Fit the pipeline on 80% of the Kaggle corpus, score the held-out 20%,
    save the model, and save six held-out rows to reuse as test emails.

    Returns a dict of the held-out metrics so the notebook and PROGRESS.md can
    record them without re-parsing printed text.
    """
    df = pd.read_csv(csv_path)   # columns confirmed: text_combined, label
    df = df.dropna().drop_duplicates()
    X_train, X_test, y_train, y_test = train_test_split(
        df["text_combined"], df["label"],
        test_size=0.2, stratify=df["label"], random_state=seed)

    clf = make_pipeline(
        TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=5,
                        max_features=50000, sublinear_tf=True),
        LogisticRegression(max_iter=1000, class_weight="balanced"),
    )
    clf.fit(X_train, y_train)

    probs = clf.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)
    print(classification_report(y_test, preds, digits=3))
    print("ROC-AUC:", round(roc_auc_score(y_test, probs), 3))
    print(confusion_matrix(y_test, preds))
    joblib.dump(clf, model_path)

    report = classification_report(y_test, preds, digits=3, output_dict=True)
    cm = confusion_matrix(y_test, preds)
    metrics = {
        "rows_after_cleaning": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "precision_phishing": round(report["1"]["precision"], 3),
        "recall_phishing": round(report["1"]["recall"], 3),
        "f1_phishing": round(report["1"]["f1-score"], 3),
        "roc_auc": round(float(roc_auc_score(y_test, probs)), 3),
        "confusion_matrix": {"tn": int(cm[0, 0]), "fp": int(cm[0, 1]),
                             "fn": int(cm[1, 0]), "tp": int(cm[1, 1])},
    }

    _save_holdout_rows(X_test, y_test, probs, holdout_path, seed)
    return metrics


def _save_holdout_rows(X_test, y_test, probs, holdout_path: Path, seed: int,
                       per_class: int = 3, min_len: int = 200, max_len: int = 1500):
    """Save three held-out phishing rows and three held-out legitimate rows.

    Rows are sampled from the held-out split only, so they were never seen in
    training. The length filter keeps rows short enough to read as one email.
    """
    rng = random.Random(seed)
    rows = []
    for label in (1, 0):
        pool = [(t, p) for t, y, p in zip(X_test, y_test, probs)
                if y == label and min_len <= len(t) <= max_len]
        for text, prob in rng.sample(pool, per_class):
            rows.append({"label": int(label),
                         "true_label": "phishing" if label == 1 else "legitimate",
                         "classifier_prob": round(float(prob), 3),
                         "text": text})
    holdout_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


# ---- loading and explanation, used by the classify_email_text tool ----------

_MODEL = None
_PARTS = None


def load_classifier(model_path: Path = MODEL_PATH):
    """Load the saved pipeline once and cache it."""
    global _MODEL, _PARTS
    if _MODEL is None:
        clf = joblib.load(model_path)
        vec = clf.named_steps["tfidfvectorizer"]
        lr = clf.named_steps["logisticregression"]
        vocab = vec.get_feature_names_out()
        _MODEL, _PARTS = clf, (vec, lr, vocab)
    return _MODEL


def top_words(text, k=5):
    """Words in this email that pushed the score toward phishing the most."""
    load_classifier()
    vec, lr, vocab = _PARTS
    contrib = vec.transform([text]).multiply(lr.coef_[0]).toarray()[0]
    best = contrib.argsort()[::-1][:k]
    return [str(vocab[i]) for i in best if contrib[i] > 0]
