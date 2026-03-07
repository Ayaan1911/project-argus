"""
ai_layer/predictor/inference.py
=================================
Stage 4 of the Argus AI Pipeline.

Loads the trained anomaly_model.pkl and runs inference on a single listing.
Full pipeline: raw listing dict → FeatureEngineer → scaler → IsolationForest → risk result.
"""

import json
import logging
import pathlib
from typing import Optional

import joblib
import pandas as pd

from ai_layer.preprocessing.feature_engineer import FeatureEngineer

logger = logging.getLogger(__name__)

_MODEL_PATH = pathlib.Path("ai_layer/models/anomaly_model.pkl")


class ScamPredictor:
    """
    Runs anomaly-detection inference on a single listing.

    Usage:
        predictor = ScamPredictor()
        predictor.load()
        result = predictor.predict(listing_dict)
        # result → {"listing_id": "…", "risk_score": -0.23, "risk_level": "High Risk", "features_used": {…}}
    """

    def __init__(self, model_path: pathlib.Path = _MODEL_PATH):
        self.model_path      = model_path
        self._model          = None
        self._scaler         = None
        self._feature_cols:  list[str] = []
        self._low_threshold:  float = -0.1
        self._high_threshold: float =  0.1
        self._engineer       = FeatureEngineer()

    def load(self) -> None:
        """Load the persisted model payload from disk."""
        payload              = joblib.load(self.model_path)
        self._model          = payload["model"]
        self._scaler         = payload["scaler"]
        self._feature_cols   = payload["feature_cols"]
        self._low_threshold  = payload.get("low_threshold",  -0.1)
        self._high_threshold = payload.get("high_threshold",  0.1)
        logger.info(
            f"ScamPredictor: model loaded from {self.model_path}  "
            f"(low={self._low_threshold:.4f}, high={self._high_threshold:.4f})"
        )

    def predict(self, listing: dict) -> dict:
        """
        Predict anomaly score for a single listing dict.

        Args:
            listing: Raw listing dict (same schema as listings_dataset.json).

        Returns:
            {
                "listing_id":   str,
                "risk_score":   float,   # decision_function value: positive = genuine
                "risk_level":   str,     # "Likely Genuine" | "Suspicious" | "High Risk"
                "features_used": dict,
            }
        """
        if self._model is None:
            self.load()

        features_df = self._engineer.transform([listing])

        if features_df.empty:
            logger.warning("Feature engineering returned no rows — using zero-vector fallback.")
            listing_id = listing.get("listing_id", "unknown")
            zero_feat = {col: 0 for col in self._feature_cols}
            features_df = pd.DataFrame([zero_feat])
            features_df["listing_id"] = listing_id

        # Keep listing_id for output, drop non-feature cols for model input
        listing_id = features_df["listing_id"].iloc[0] if "listing_id" in features_df.columns else listing.get("listing_id", "unknown")
        X = features_df[[c for c in self._feature_cols]].fillna(0)
        X_scaled = self._scaler.transform(X)

        score = float(self._model.decision_function(X_scaled)[0])
        # Confidence logic: further from zero means more certain decision
        # isolation forest decision_function scores typically range from -0.5 to 0.5
        # we scale abs(score) to a 0-1 range
        confidence = min(abs(score) * 2.5, 1.0)
        risk_level = self._score_to_risk(score)

        return {
            "listing_id":      listing_id,
            "risk_score":      round(score, 6),
            "confidence_score": round(confidence, 4),
            "risk_level":      risk_level,
            "features_used":   X.iloc[0].to_dict(),
        }

    def predict_batch(self, listings: list[dict]) -> list[dict]:
        """Run predict() on a list of listings."""
        return [self.predict(lst) for lst in listings]

    def _score_to_risk(self, score: float) -> str:
        """Use dataset-calibrated percentile thresholds loaded from the model."""
        if score <= self._low_threshold:
            return "High Risk"
        elif score >= self._high_threshold:
            return "Likely Genuine"
        return "Suspicious"
