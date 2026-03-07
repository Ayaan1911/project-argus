"""
ai_layer/ml_model/trainer.py
==============================
STUB — Stage 3 of the Argus AI Pipeline.

Trains a scam detection classifier on the feature matrix produced by
FeatureEngineer. Uses scikit-learn models and saves the trained artifact
to ai_layer/ml_model/scam_detector.pkl.

─────────────────────────────────────────────────
LABELS
─────────────────────────────────────────────────
    0 = genuine rental listing
    1 = scam / suspicious listing

─────────────────────────────────────────────────
RECOMMENDED MODELS (try in this order)
─────────────────────────────────────────────────
    1. RandomForestClassifier   — good baseline, interpretable feature importances
    2. GradientBoostingClassifier — usually better recall on imbalanced data
    3. LogisticRegression       — fast, explainable, useful as a sanity check

─────────────────────────────────────────────────
IMPLEMENTATION GUIDE
─────────────────────────────────────────────────

1. Install: pip install scikit-learn joblib imbalanced-learn

2. Load features:
       from ai_layer.preprocessing.feature_engineer import FeatureEngineer
       fe = FeatureEngineer()
       X, y = fe.fit_transform(listings, labels)

3. Handle class imbalance (scam listings will be rare at first):
       from imblearn.over_sampling import SMOTE
       X_res, y_res = SMOTE().fit_resample(X, y)

4. Train:
       from sklearn.ensemble import RandomForestClassifier
       from sklearn.model_selection import train_test_split, cross_val_score
       X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2)
       model = RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42)
       model.fit(X_train, y_train)

5. Evaluate:
       from sklearn.metrics import classification_report
       print(classification_report(y_test, model.predict(X_test)))

6. Save:
       import joblib
       joblib.dump(model, "ai_layer/ml_model/scam_detector.pkl")

─────────────────────────────────────────────────
"""

from pathlib import Path

MODEL_PATH = Path(__file__).parent / "scam_detector.pkl"


class ScamDetectorTrainer:
    """
    STUB — trains and persists the scam detection classifier.

    Expected input:  Feature DataFrame from FeatureEngineer + label Series
    Expected output: Trained model saved to ai_layer/ml_model/scam_detector.pkl

    See module docstring for a step-by-step implementation guide.
    """

    def train(self, X, y):
        """
        Train the scam detection model and save the artifact.

        TODO (Stage 3): Implement this method.

        Args:
            X: pandas.DataFrame of numeric features from FeatureEngineer.transform().
            y: pandas.Series of integer labels (0 = genuine, 1 = scam).

        Returns:
            Trained scikit-learn model object.

        Raises:
            NotImplementedError: Until Stage 3 is implemented.
        """
        raise NotImplementedError(
            "ScamDetectorTrainer.train() is not yet implemented. "
            "See the module docstring for a complete implementation guide."
        )

    def evaluate(self, X_test, y_test) -> dict:
        """
        TODO (Stage 3): Load the saved model and evaluate on held-out test data.

        Returns:
            Dict with keys: accuracy, precision, recall, f1, roc_auc.
        """
        raise NotImplementedError(
            "ScamDetectorTrainer.evaluate() is not yet implemented."
        )

    def load(self, path: Path = MODEL_PATH):
        """
        TODO (Stage 3): Load a previously saved model artifact.

        Args:
            path: Path to the .pkl file.

        Returns:
            Loaded scikit-learn model object.
        """
        raise NotImplementedError(
            "ScamDetectorTrainer.load() is not yet implemented."
        )
