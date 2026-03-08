from pydantic import BaseModel
from typing import Optional
from enum import Enum

class PropertyType(str, Enum):
    ONE_BHK = "1BHK"
    TWO_BHK = "2BHK"
    THREE_BHK = "3BHK"
    PG = "PG"

class ListingInput(BaseModel):
    title: str
    description: str
    price: int
    locality: str
    city: str
    property_type: PropertyType
    contact_number: Optional[str] = None

class AnalysisResult(BaseModel):
    risk_score: int
    verdict: str
    price_analysis: dict
    text_analysis: dict
    image_analysis: dict
    recommendations: list[str]
    listing_id: str
