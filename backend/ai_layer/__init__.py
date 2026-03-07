"""
Project Argus — AI Layer
========================
Entry point for the full scam-detection AI pipeline.

Pipeline stages (in order):
    1. scraper/          → collect rental listings → datasets/listings_dataset.json
    2. preprocessing/    → feature engineering (STUB — not yet implemented)
    3. ml_model/         → train scam classifier (STUB — not yet implemented)
    4. predictor/        → run inference on new listing (STUB — not yet implemented)
    5. llm_explainer/    → generate human-readable explanation (STUB — not yet implemented)

Usage:
    from ai_layer.pipeline import ArgusAIPipeline
    pipeline = ArgusAIPipeline()
    pipeline.run_scraper()
"""

from ai_layer.pipeline import ArgusAIPipeline

__all__ = ["ArgusAIPipeline"]
