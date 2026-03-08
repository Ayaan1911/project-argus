"""
ai_layer/pipeline.py
====================
Orchestrator for the Argus AI pipeline — all 5 stages.

Pipeline:
    Stage 1 — Scraper       → ai_layer/datasets/listings_dataset.json   ✅
    Stage 2 — Preprocessing → features_dataset.csv                      ✅
    Stage 3 — ML Model      → anomaly_model.pkl                         ✅
    Stage 4 — Predictor     → risk_score + risk_level                   ✅
    Stage 5 — LLM Explainer → human-readable explanation                ✅

Usage:
    # Train the model (once, after scraping)
    python -m ai_layer.ml_model.anomaly_detector

    # Analyze a URL
    pipeline = ArgusAIPipeline()
    result = asyncio.run(pipeline.analyze_url("https://..."))

    # Single listing dict (already extracted)
    result = pipeline.analyze_listing(listing_dict)
"""

import logging
import pathlib
from typing import Optional

from ai_layer.config import CITIES, LOG_PREFIX

logger = logging.getLogger(__name__)

_DATASET_PATH = pathlib.Path("ai_layer/datasets/listings_dataset.json")


class ArgusAIPipeline:
    """
    Top-level orchestrator for the Argus scam-detection AI pipeline.
    All 5 stages are implemented and wired end-to-end.
    """

    def __init__(
        self,
        cities: Optional[list[str]] = None,
        llm_provider: str = "bedrock",
    ):
        self.cities       = cities or CITIES
        self.llm_provider = llm_provider
        self._predictor   = None   # lazy-loaded
        self._explainer   = None   # lazy-loaded

    # ------------------------------------------------------------------
    # Lazy loaders
    # ------------------------------------------------------------------

    def _get_predictor(self):
        if self._predictor is None:
            from ai_layer.predictor.inference import ScamPredictor
            self._predictor = ScamPredictor()
            self._predictor.load()
        return self._predictor

    def _get_explainer(self):
        if self._explainer is None:
            from ai_layer.llm_explainer.explainer import LLMExplainer
            self._explainer = LLMExplainer(provider=self.llm_provider)
        return self._explainer

    # ------------------------------------------------------------------
    # Stage 1 — Scraper
    # ------------------------------------------------------------------

    async def run_scraper(self, cities: Optional[list[str]] = None) -> pathlib.Path:
        """Run the Playwright scraper and save listings_dataset.json."""
        from ai_layer.scraper.playwright_scraper import PlaywrightScraper
        from ai_layer.scraper.dataset_manager import DatasetManager

        target_cities = cities or self.cities
        dm = DatasetManager()
        scraper = PlaywrightScraper()
        await scraper.run(cities=target_cities, dataset_manager=dm)
        return dm.dataset_path

    # ------------------------------------------------------------------
    # Stage 2 — Preprocessing
    # ------------------------------------------------------------------

    def run_preprocessing(self, listings=None) -> pathlib.Path:
        """Run FeatureEngineer and save features_dataset.csv."""
        import json
        from ai_layer.preprocessing.feature_engineer import FeatureEngineer

        features_path = pathlib.Path("ai_layer/datasets/features_dataset.csv")

        if listings is None:
            with open(_DATASET_PATH, "r", encoding="utf-8") as f:
                listings = json.load(f)

        fe = FeatureEngineer()
        df = fe.transform(listings)
        features_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(features_path, index=False)
        logger.info(f"Features saved → {features_path} ({len(df)} rows)")
        return features_path

    # ------------------------------------------------------------------
    # Stage 3 — ML Model Training
    # ------------------------------------------------------------------

    def run_training(self) -> pathlib.Path:
        """Train IsolationForest and save anomaly_model.pkl."""
        from ai_layer.ml_model.anomaly_detector import AnomalyDetector

        detector = AnomalyDetector()
        detector.train()
        model_path = pathlib.Path("ai_layer/models/anomaly_model.pkl")
        detector.save_model(model_path)
        return model_path

    # ------------------------------------------------------------------
    # Stage 4+5 — Single Listing Analysis  (sync)
    # ------------------------------------------------------------------

    def analyze_listing(self, listing: dict) -> dict:
        """
        Run predictor + explainer on an already-extracted listing dict.

        Returns:
            {
                "listing_id", "risk_score", "risk_level",
                "explanation", "features_used", "data_source"
            }
        """
        predictor = self._get_predictor()
        explainer = self._get_explainer()

        prediction  = predictor.predict(listing)
        explanation = explainer.explain(listing, prediction)

        return {
            "listing_id":      prediction["listing_id"],
            "risk_score":      prediction["risk_score"],
            "confidence_score": prediction.get("confidence_score", 0.5),
            "risk_level":      prediction["risk_level"],
            "explanation":     explanation,
            "features_used":   prediction.get("features_used", {}),
            "data_source":     listing.get("data_source", "scraped"),
        }

    # ------------------------------------------------------------------
    # URL-based analysis  (async)
    # ------------------------------------------------------------------

    async def analyze_url(self, url: str) -> dict:
        """
        Full pipeline starting from a listing URL.

        Steps:
            1. ListingURLAnalyzer detects platform + extracts listing
               (falls back to synthetic if bot-blocked)
            2. ScamPredictor generates risk score
            3. LLMExplainer generates explanation

        Returns:
            {
                "url", "platform", "city", "price",
                "risk_score", "risk_level", "explanation",
                "data_source", "features_used"
            }
        """
        from ai_layer.input.url_analyzer import ListingURLAnalyzer

        analyzer = ListingURLAnalyzer()
        listing  = await analyzer.extract_listing(url)
        result   = self.analyze_listing(listing)

        out = {
            "url":              url,
            "platform":         listing.get("platform_source", "unknown"),
            "city":             listing.get("city", "unknown"),
            "price":            listing.get("price"),
            "risk_score":       result["risk_score"],
            "confidence_score": result["confidence_score"],
            "risk_level":       result["risk_level"],
            "explanation":      result["explanation"],
            "data_source":      result["data_source"],
            "features_used":    result["features_used"],
        }
        
        if "override_risk_level" in listing:
            out["override_risk_level"] = listing["override_risk_level"]
            out["override_risk_score"] = listing["override_risk_score"]
            # Fix explanation using raw mock scores
            if "override_risk_level" == "Likely Genuine" and "explanation" in out:
                out["explanation"] = "This listing appears legitimate based on current analysis. Verified broker and reasonable market rates."
                
        return out

    # ------------------------------------------------------------------
    # Backward compat alias
    # ------------------------------------------------------------------

    async def run_full(self, listing_url: str) -> dict:
        """Alias for analyze_url()."""
        return await self.analyze_url(listing_url)
