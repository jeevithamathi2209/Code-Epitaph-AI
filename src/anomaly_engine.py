import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(df):
    """
    Detect structurally unusual components using
    an unsupervised Isolation Forest model.
    """

    features = [
        "risk_score",
        "dependency_count",
        "failure_impact",
        "centrality",
        "priority_score"
    ]

    model_data = df[features].copy()

    model = IsolationForest(
        n_estimators=150,
        contamination="auto",
        random_state=42
    )

    predictions = model.fit_predict(model_data)
    anomaly_scores = model.decision_function(model_data)

    result = df.copy()

    result["anomaly_prediction"] = predictions
    result["anomaly_score"] = anomaly_scores.round(4)

    result["anomaly_status"] = result[
        "anomaly_prediction"
    ].map({
        1: "NORMAL",
        -1: "ANOMALOUS"
    })

    return result


def get_anomaly_summary(df):
    """
    Generate anomaly detection summary.
    """

    anomalous = int(
        (df["anomaly_status"] == "ANOMALOUS").sum()
    )

    normal = int(
        (df["anomaly_status"] == "NORMAL").sum()
    )

    total = len(df)

    anomaly_rate = (
        round((anomalous / total) * 100, 1)
        if total > 0
        else 0
    )

    return {
        "total_components": total,
        "anomalous_components": anomalous,
        "normal_components": normal,
        "anomaly_rate": anomaly_rate
    }