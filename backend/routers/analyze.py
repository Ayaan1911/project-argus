from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.schemas import AnalysisResult
from services import price_engine, text_engine, image_engine, risk_scorer
import uuid
import boto3
from datetime import datetime
import json
import os

router = APIRouter(prefix="/analyze", tags=["analyze"])

def save_to_dynamodb(listing_id: str, input_data: dict, result: dict):
    """Save analysis result to DynamoDB"""
    from decimal import Decimal
    
    try:
        # Skip if no AWS credentials (demo mode)
        if not os.getenv('AWS_ACCESS_KEY_ID') and not os.getenv('AWS_REGION'):
            print("Demo mode: Skipping DynamoDB save")
            return
            
        dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
        table = dynamodb.Table(os.getenv('DYNAMODB_TABLE', 'argus-submissions'))
        
        # Convert all values to DynamoDB-compatible types (no raw floats)
        def to_dynamo(val):
            if isinstance(val, float):
                return Decimal(str(val))
            if isinstance(val, dict):
                return {k: to_dynamo(v) for k, v in val.items() if v is not None}
            if isinstance(val, list):
                return [to_dynamo(v) for v in val]
            return val
        
        item = {
            'listing_id': listing_id,
            'timestamp': datetime.utcnow().isoformat(),
            'city': input_data.get('city', 'unknown'),
            'locality': input_data.get('locality', 'unknown'),
            'price': to_dynamo(input_data.get('price', 0)),
            'property_type': input_data.get('property_type', 'unknown'),
            'final_score': to_dynamo(result.get('risk_score', 0)),
            'risk_level': result.get('risk_level', 'unknown'),
            'verdict': result.get('verdict', result.get('risk_level', 'unknown')),
            'title': input_data.get('title', ''),
            'description': input_data.get('description', '')[:500],  # truncate long descriptions
        }
        
        # Remove any None values (DynamoDB rejects them)
        item = {k: v for k, v in item.items() if v is not None}
        
        table.put_item(Item=item)
        print(f"DynamoDB save OK: listing_id={listing_id}")
    except Exception as e:
        print(f"DynamoDB save failed: {e}")
        # Don't fail the request if DynamoDB save fails

@router.post("/", response_model=AnalysisResult)
async def analyze_listing(
    title: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    locality: str = Form(...),
    city: str = Form(...),
    property_type: str = Form(...),
    contact_number: str = Form(None),
    images: list[UploadFile] = File(None)
):
    """
    Analyze a rental listing for scam indicators
    
    Accepts multipart form data with listing details and optional images.
    Returns comprehensive risk analysis with score, verdict, and recommendations.
    """
    try:
        # Generate unique listing ID
        listing_id = str(uuid.uuid4())
        
        # Run price analysis
        try:
            price_result = price_engine.analyze_price(
                price=price,
                city=city,
                locality=locality,
                property_type=property_type
            )
        except Exception as e:
            print(f"Price analysis error: {str(e)}")
            price_result = {
                "score": 50,
                "verdict": "Unable to verify",
                "market_median": None,
                "percentage_below_market": None,
                "reasoning": "Price analysis unavailable"
            }
        
        # Run text analysis
        try:
            text_result = text_engine.analyze_text(
                title=title,
                description=description,
                contact_number=contact_number
            )
        except Exception as e:
            print(f"Text analysis error: {str(e)}")
            text_result = {
                "score": 50,
                "verdict": "Unable to analyze",
                "flags": [],
                "reasoning": "Text analysis unavailable"
            }
        
        # Run image analysis
        try:
            if images and len(images) > 0:
                image_result = await image_engine.analyze_images(images)
            else:
                image_result = {
                    "score": 20,
                    "verdict": "No image provided",
                    "flags": [],
                    "reasoning": "No images were provided for analysis"
                }
        except Exception as e:
            print(f"Image analysis error: {str(e)}")
            image_result = {
                "score": 50,
                "verdict": "Unable to analyze",
                "flags": [],
                "reasoning": "Image analysis unavailable"
            }
        
        # Calculate final risk score
        final_result = risk_scorer.calculate_final_score(
            price_result=price_result,
            text_result=text_result,
            image_result=image_result
        )
        
        # Prepare response
        analysis_result = AnalysisResult(
            risk_score=final_result["final_score"],
            verdict=final_result["verdict"],
            price_analysis=price_result,
            text_analysis=text_result,
            image_analysis=image_result,
            recommendations=final_result["recommendations"],
            listing_id=listing_id
        )
        
        # Save to DynamoDB (non-blocking)
        input_data = {
            "title": title,
            "description": description,
            "price": price,
            "locality": locality,
            "city": city,
            "property_type": property_type
        }
        save_to_dynamodb(listing_id, input_data, analysis_result.dict())
        
        return analysis_result
        
    except Exception as e:
        print(f"Analysis endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/url")
async def analyze_listing_url(url: str = Form(...)):
    """
    Analyze a rental listing from URL with intelligent scraping and fallback
    """
    try:
        if not url or "http" not in url:
            return {"error": "Unable to analyze the provided listing URL."}

        from services.argus_service import analyze_listing_url as run_argus_analysis
        
        # Run the full production pipeline
        result = await run_argus_analysis(url)
        
        # Save to DynamoDB
        save_to_dynamodb(
            listing_id=result.get("listing_id", str(uuid.uuid4())),
            input_data={"url": url, "city": result.get("city", ""), "title": url.split("/")[-1]},
            result=result,
        )
        
        # Return the normalized service result directly
        return result
        
    except Exception as e:
        print(f"URL analysis error: {str(e)}")
        return {"error": "Unable to analyze the provided listing URL."}

@router.post("/listing")
async def analyze_listing_api(url: str = Form(...)):
    """API endpoint for listing analysis by URL."""
    return await analyze_listing_url(url)
