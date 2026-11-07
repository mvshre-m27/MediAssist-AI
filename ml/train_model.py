import json
import joblib
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

from preprocessing import get_preprocessor, load_data, ALL_FEATURE_COLUMNS

def train_and_evaluate():
    print("=" * 60)
    print("MediAssist-AI: Medication Adherence Risk Model Training")
    print("Dataset: Mendeley Data (Diabetes & Hypertension Adherence)")
    print("=" * 60)

    # 1. Load Data
    X, y = load_data('ml/dataset.csv')
    print(f"Total Records: {len(X)} | Features: {len(ALL_FEATURE_COLUMNS)}")
    print(f"Class Distribution: Non-Adherent (Risk=1): {y.sum()} ({y.mean()*100:.1f}%), Adherent (0): {(1-y).sum()} ({(1-y.mean())*100:.1f}%)")

    # 2. Stratified Train-Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
    print(f"Training set: {len(X_train)} samples | Testing set: {len(X_test)} samples\n")

    # 3. Models to Benchmark
    preprocessor = get_preprocessor()

    candidate_models = {
        "Logistic_Regression": Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                random_state=42
            ))
        ]),
        "Decision_Tree": Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', DecisionTreeClassifier(
                max_depth=7,
                class_weight='balanced',
                random_state=42
            ))
        ]),
        "Random_Forest": Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(
                n_estimators=150,
                max_depth=12,
                min_samples_split=5,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            ))
        ])
    }

    results = {}
    best_model_name = None
    best_f1 = -1.0

    for name, pipeline in candidate_models.items():
        print(f"--- Training {name.replace('_', ' ')} ---")
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        cm = confusion_matrix(y_test, y_pred).tolist()

        print(f"  Accuracy : {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall   : {rec:.4f}")
        print(f"  F1-Score : {f1:.4f}")
        print(f"  ROC-AUC  : {auc:.4f}")
        print(f"  Confusion Matrix: {cm}\n")

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": cm
        }

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name

    print(f"Selected Best Model: {best_model_name} (F1: {best_f1:.4f})")

    # 4. Save the Best Pipeline
    best_pipeline = candidate_models[best_model_name]
    model_path = Path("ml/adherence_model.pkl")
    joblib.dump(best_pipeline, model_path)
    print(f"Serialized trained pipeline saved to: {model_path}")

    # 5. Save Evaluation Report for Capstone Documentation
    report_path = Path("ml/evaluation_report.json")
    with open(report_path, "w") as f:
        json.dump({
            "selected_model": best_model_name,
            "feature_columns": ALL_FEATURE_COLUMNS,
            "models_comparison": results
        }, f, indent=4)
    print(f"Model evaluation report saved to: {report_path}")

if __name__ == '__main__':
    train_and_evaluate()
