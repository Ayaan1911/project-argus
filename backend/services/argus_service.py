"""
backend/services/argus_service.py
==================================
Production service layer for Project Argus AI.
Wraps the ai_layer pipeline for consumption by FastAPI routers.
"""

import logging
from ai_layer.pipeline import ArgusAIPipeline

logger = logging.getLogger(__name__)

# Singleton pipeline instance for efficiency (lazy loads models)
_pipeline = ArgusAIPipeline()

async def analyze_listing_url(url: str) -> dict:
    """
    Analyzes a listing URL through the full Argus AI pipeline.
    
    Returns structured result including confidence scores and signal breakdown.
    """
    logger.info(f"ArgusService: Analyzing URL -> {url}")
    
    # --- DEMO OVERRIDE LAYER REMOVED ---

    try:
        # Run the full pipeline (Scrape/Synthetic -> Preprocess -> Predict -> Explain)
        result = await _pipeline.analyze_url(url)
        
        # Format response for frontend consumption
        # Compute confidence label
        score_percentage = result.get("confidence_score", 0.5) * 100
        if score_percentage >= 70:
            confidence_label = "High Confidence"
        elif score_percentage >= 40:
            confidence_label = "Moderate Confidence"
        else:
            confidence_label = "Low Confidence"

        # Default recommendations if missing
        recommendations = result.get("recommendations") or [
            "Verify the property and owner ID in person.",
            "Never pay a 'visiting fee' or 'token amount' before seeing the property.",
            "Compare the price with other listings in the same locality.",
            "Request a live video call if you cannot visit immediately."
        ]

        # Normalize risk_score to a 0-100 integer for the frontend.
        # Formula: normalized = int((1 - (raw_score + 0.5)) * 100), clamped 0-100
        raw_score = result.get("risk_score", 0)
        risk_level = result.get("risk_level", "Suspicious")
        
        normalized = int((1 - (raw_score + 0.5)) * 100)
        ui_score = max(0, min(100, normalized))
        
        # Allow explicit overrides from demo/test fallbacks
        final_risk_level = result.get("override_risk_level") or risk_level
        final_risk_score = result.get("override_risk_score") or ui_score

        return {
            "listing_id":       result.get("listing_id", "unknown"),
            "url":              result.get("url"),
            "risk_level":       final_risk_level,
            "risk_score":       final_risk_score,
            "confidence_score": result.get("confidence_score", 0.5),
            "explanation":      result.get("explanation", ""),
            "recommendations":  recommendations,
            "signals": {
                "Price vs Market":    result.get("features_used", {}).get("price_vs_city_median"),
                "Urgency Language":   result.get("features_used", {}).get("urgency_keyword_count"),
                "Phone Reuse":        result.get("features_used", {}).get("phone_reuse_count"),
                "Image Count":        result.get("features_used", {}).get("image_count", 0),
            }
        }
    except Exception as e:
        logger.error(f"ArgusService Error: {str(e)}")
        raise e
