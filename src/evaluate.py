"""
Trains/evaluates both detectors and reports the headline number: the gap in
false-negative rate between human-compromise detection and agent-compromise
detection, for both the baseline rules and the lightweight classifier.
"""

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score

import baseline_rules
import classifier as clf_module


def false_negative_rate(y_true, y_pred):
    fn = ((y_true == True) & (y_pred == False)).sum()
    positives = (y_true == True).sum()
    return fn / positives if positives else float("nan")


def evaluate_by_identity(df, y_pred_col):
    rows = []
    for identity in ["human", "agent"]:
        subset = df[df["identity_type"] == identity]
        y_true = subset["is_compromised"]
        y_pred = subset[y_pred_col]
        rows.append({
            "identity_type": identity,
            "precision": round(precision_score(y_true, y_pred, zero_division=0), 3),
            "recall": round(recall_score(y_true, y_pred, zero_division=0), 3),
            "f1": round(f1_score(y_true, y_pred, zero_division=0), 3),
            "false_negative_rate": round(false_negative_rate(y_true, y_pred), 3),
            "n": len(subset),
        })
    return rows


def main():
    root = Path(__file__).resolve().parent.parent
    data_path = root / "data" / "sessions.csv"
    if not data_path.exists():
        raise SystemExit("Run src/simulator.py first to generate data/sessions.csv")

    df = pd.read_csv(data_path)
    train_df, test_df = train_test_split(
        df, test_size=0.3, random_state=42, stratify=df["label"]
    )

    # --- Baseline (identity-agnostic SIEM-style rules) ---
    thresholds = baseline_rules.fit_thresholds(train_df)
    test_df = test_df.copy()
    test_df["baseline_pred"] = baseline_rules.predict(test_df, thresholds)

    # --- Lightweight classifier ---
    model = clf_module.build_model()
    clf_module.fit(model, train_df)
    test_df["classifier_pred"] = clf_module.predict(model, test_df)

    results = {
        "baseline_rules": evaluate_by_identity(test_df, "baseline_pred"),
        "lightweight_classifier": evaluate_by_identity(test_df, "classifier_pred"),
        "thresholds_used": thresholds,
        "note": "Synthetic data — see README limitations before citing these numbers.",
    }

    out_dir = root / "results"
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2))
    print(f"\nWrote results/metrics.json")


if __name__ == "__main__":
    main()
