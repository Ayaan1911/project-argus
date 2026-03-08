"""
ai_layer/preprocessing/feature_engineer.py
============================================
Stage 2 of the Argus AI Pipeline.

Converts raw scraped listings into a structured feature
matrix suitable for training the scam detection ML model.
"""

import json
import logging
from pathlib import Path
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """
    Converts raw listing dicts into an ML-ready feature matrix.
    """
    
    def __init__(self):
        self.urgency_words = [
            "urgent", "token", "advance", "immediate", "limited offer"
        ]

    def transform(self, listings: list[dict]) -> pd.DataFrame:
        """
        Transform raw listings into a feature matrix.
        """
        if not listings:
            return pd.DataFrame()
            
        df = pd.DataFrame(listings)
        
        # --- DATA CLEANING ---
        # 1. Drop records where price == 0
        df = df[df['price'].notna() & (df['price'] > 0)]
        
        # 2. Drop records where description is empty
        df = df[df['description'].notna() & (df['description'].str.strip() != '')]
        
        # 3. Drop records where listing_url is missing
        df = df[df['listing_url'].notna() & (df['listing_url'].str.strip() != '')]
        
        # 4. Fill missing phone_number values with "unknown"
        df['phone_number'] = df['phone_number'].fillna('unknown')
        
        # Ensure we still have data
        if df.empty:
            return pd.DataFrame()
            
        # --- FEATURE ENGINEERING ---
        
        # Feature: price_vs_city_median
        # Compute median price for each city
        city_medians = df.groupby('city')['price'].transform('median')
        df['price_vs_city_median'] = df['price'] / city_medians
        
        # Feature: description_length
        df['description_length'] = df['description'].str.len()
        
        # Feature: urgency_keyword_count
        def count_urgency(text: str) -> int:
            if not isinstance(text, str): return 0
            text_lower = text.lower()
            return sum(text_lower.count(word) for word in self.urgency_words)
            
        df['urgency_keyword_count'] = df['description'].apply(count_urgency)
        
        # Feature: image_count
        df['image_count'] = df['image_count'].fillna(0).astype(int)
        
        # Feature: phone_reuse_count
        phone_counts = df.groupby('phone_number')['listing_id'].transform('count')
        df['phone_reuse_count'] = phone_counts
        
        # Feature: listings_per_day_per_phone
        if 'timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df['date'] = df['datetime'].dt.date
            daily_phone_counts = df.groupby(['phone_number', 'date'])['listing_id'].transform('count')
            df['listings_per_day_per_phone'] = daily_phone_counts.fillna(0).astype(int)
        else:
            df['listings_per_day_per_phone'] = 0
            
        # Select required columns
        final_columns = [
            'listing_id',
            'city',
            'price_vs_city_median',
            'description_length',
            'urgency_keyword_count',
            'image_count',
            'phone_reuse_count',
            'listings_per_day_per_phone'
        ]
        
        for col in final_columns:
            if col not in df.columns:
                df[col] = None
                
        return df[final_columns].copy()

    def fit_transform(self, listings: list[dict], labels: Optional[list[int]] = None) -> pd.DataFrame:
        """
        Fit any stateful transformers and transform in one step.
        """
        return self.transform(listings)

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s")
    
    # Run from backend directory
    dataset_file = Path("ai_layer/datasets/listings_dataset.json").resolve()
    features_file = Path("ai_layer/datasets/features_dataset.csv").resolve()
    
    if not dataset_file.exists():
        logger.error(f"Dataset file not found: {dataset_file}")
        return
        
    logger.info(f"Loading raw listings from {dataset_file}...")
    with open(dataset_file, "r", encoding="utf-8") as f:
        listings = json.load(f)
        
    logger.info(f"Loaded {len(listings)} raw listings. Generating features...")
    
    engineer = FeatureEngineer()
    features_df = engineer.transform(listings)
    
    if features_df.empty:
        logger.warning("Feature engineering resulted in an empty dataset after cleaning.")
        return
        
    # Ensure parent directory exists
    features_file.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(features_file, index=False)
    
    logger.info(f"Feature engineering complete. Saved to: {features_file}")
    logger.info(f"Final feature matrix shape: {features_df.shape}")

if __name__ == "__main__":
    main()
