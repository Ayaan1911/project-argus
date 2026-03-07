"""
ai_layer/ml_model/anomaly_detector.py
=======================================
Unsupervised anomaly detection using IsolationForest.

Risk thresholds are computed from score percentiles after training so
they automatically adapt to each dataset's score distribution:

    low_threshold  = np.percentile(scores, 15)  → bottom 15% = High Risk
    high_threshold = np.percentile(scores, 85)  → top 15%    = Likely Genuine
    in between                                  → Suspicious

CLI usage (from backend/):
    python -m ai_layer.ml_model.anomaly_detector
"""

import logging
import pathlib
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths (relative to backend/ where scripts are executed from)
# ---------------------------------------------------------------------------
_FEATURES_PATH = pathlib.Path("ai_layer/datasets/features_dataset.csv")
_SCORED_PATH   = pathlib.Path("ai_layer/datasets/scored_listings.csv")
_MODEL_PATH    = pathlib.Path("ai_layer/models/anomaly_model.pkl")

# Non-feature columns excluded from the model input
_NON_FEATURE_COLS = {"listing_id", "city"}


def _score_to_risk(score: float, low: float, high: float) -> str:
    """Assign risk level based on dataset-relative percentile thresholds."""
    if score <= low:
        return "High Risk"
    elif score >= high:
        return "Likely Genuine"
    return "Suspicious"


class AnomalyDetector:
    """
    Trains an IsolationForest on features_dataset.csv and scores every listing.

    Thresholds (low_threshold, high_threshold) are derived from the 15th and
    85th score percentiles so the distribution is always realistic regardless
    of absolute score values.

    Saved model payload includes:
        model, scaler, feature_cols, low_threshold, high_threshold
    """

    def __init__(
        self,
        n_estimators: int = 200,
        contamination: float = 0.1,
        random_state: int = 42,
    ):
        self.n_estimators  = n_estimators
        self.contamination = contamination
        self.random_state  = random_state

        self.model:          Optional[IsolationForest] = None
        self.scaler:         Optional[StandardScaler]  = None
        self.feature_cols:   list[str]                 = []
        self.low_threshold:  float                     = 0.0
        self.high_threshold: float                     = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def train(self, features_path: pathlib.Path = _FEATURES_PATH) -> pd.DataFrame:
        """
        Load feature CSV, fit IsolationForest, score all records.

        Returns:
            DataFrame with original columns + anomaly_score + risk_level.
        """
        logger.info(f"Loading features from {features_path} …")
        df = pd.read_csv(features_path)

        meta_cols = [c for c in df.columns if c in _NON_FEATURE_COLS]
        self.feature_cols = [c for c in df.columns if c not in _NON_FEATURE_COLS]

        X = df[self.feature_cols].fillna(0)

        # Scale
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Train
        logger.info(
            f"Training IsolationForest on {len(df)} samples "
            f"× {len(self.feature_cols)} features …"
        )
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.model.fit(X_scaled)

        # Raw scores (higher = more normal)
        scores = self.model.decision_function(X_scaled)

        # Compute adaptive percentile thresholds
        self.low_threshold  = float(np.percentile(scores, 15))
        self.high_threshold = float(np.percentile(scores, 85))

        logger.info(
            f"Score range: [{scores.min():.4f}, {scores.max():.4f}]  "
            f"| low_threshold={self.low_threshold:.4f}  "
            f"| high_threshold={self.high_threshold:.4f}"
        )

        df["anomaly_score"] = scores.round(6)
        df["risk_level"] = [
            _score_to_risk(s, self.low_threshold, self.high_threshold)
            for s in scores
        ]

        return df

    def save_model(self, path: pathlib.Path = _MODEL_PATH) -> None:
        """Persist model, scaler, feature columns, and thresholds."""
        if self.model is None:
            raise RuntimeError("Call train() before save_model().")
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model":          self.model,
            "scaler":         self.scaler,
            "feature_cols":   self.feature_cols,
            "low_threshold":  self.low_threshold,
            "high_threshold": self.high_threshold,
        }
        joblib.dump(payload, path)
        logger.info(f"Model saved → {path}")

    def load_model(self, path: pathlib.Path = _MODEL_PATH) -> None:
        """Load a previously saved model payload."""
        payload         = joblib.load(path)
        self.model          = payload["model"]
        self.scaler         = payload["scaler"]
        self.feature_cols   = payload["feature_cols"]
        self.low_threshold  = payload["low_threshold"]
        self.high_threshold = payload["high_threshold"]
        logger.info(f"Model loaded from {path}")

    def score_listing(self, listing_features: dict) -> dict:
        """Score a single listing dict (must contain the feature columns)."""
        if self.model is None:
            raise RuntimeError("Call train() or load_model() first.")
        row   = pd.DataFrame([listing_features])
        X     = row[self.feature_cols].fillna(0)
        X_s   = self.scaler.transform(X)
        score = float(self.model.decision_function(X_s)[0])
        return {
            "anomaly_score": round(score, 6),
            "risk_level":    _score_to_risk(score, self.low_threshold, self.high_threshold),
        }


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    )

    detector  = AnomalyDetector()
    scored_df = detector.train()
    detector.save_model()

    # Save scored listings
    _SCORED_PATH.parent.mkdir(parents=True, exist_ok=True)
    scored_df.to_csv(_SCORED_PATH, index=False)
    logger.info(f"Scored listings → {_SCORED_PATH}")

    scores = scored_df["anomaly_score"].values
    print("\n=== Score Distribution ===")
    print(f"min   : {scores.min():.4f}")
    print(f"max   : {scores.max():.4f}")
    print(f"p5    : {np.percentile(scores, 5):.4f}")
    print(f"p25   : {np.percentile(scores, 25):.4f}")
    print(f"p50   : {np.percentile(scores, 50):.4f}")
    print(f"p75   : {np.percentile(scores, 75):.4f}")
    print(f"p95   : {np.percentile(scores, 95):.4f}")
    print()
    print("=== Risk Level Distribution ===")
    print(scored_df["risk_level"].value_counts().to_string())
    print(f"\nModel  → {_MODEL_PATH.resolve()}")
    print(f"Scores → {_SCORED_PATH.resolve()}")


if __name__ == "__main__":
    main()
