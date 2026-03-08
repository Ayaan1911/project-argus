from fastapi import APIRouter, HTTPException
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import os

router = APIRouter(prefix="/submissions", tags=["submissions"])

def decimal_to_int(obj):
    """Convert DynamoDB Decimal types to int/float for JSON serialization"""
    if isinstance(obj, list):
        return [decimal_to_int(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_int(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj

@router.get("/{listing_id}")
def get_submission(listing_id: str):
    """
    Get a specific submission by listing ID
    
    Args:
        listing_id: Unique identifier for the listing
    
    Returns:
        Submission details including analysis results
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
        table = dynamodb.Table(os.getenv('DYNAMODB_TABLE', 'argus-submissions'))
        
        response = table.get_item(Key={'listing_id': listing_id})
        
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        item = decimal_to_int(response['Item'])
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching submission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch submission: {str(e)}")

@router.get("/")
def list_submissions(limit: int = 10):
    """
    List recent submissions (for demo dashboard)
    
    Args:
        limit: Maximum number of submissions to return (default 10)
    
    Returns:
        List of recent submissions with basic details
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
        table = dynamodb.Table(os.getenv('DYNAMODB_TABLE', 'argus-submissions'))
        
        # Scan table and get last N items (sorted by timestamp)
        response = table.scan(Limit=limit)
        
        items = response.get('Items', [])
        
        # Convert Decimal types and sort by timestamp (newest first)
        items = decimal_to_int(items)
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {
            "submissions": items[:limit],
            "total": len(items)
        }
        
    except Exception as e:
        print(f"Error listing submissions: {str(e)}")
        # Return empty list if DynamoDB is not available
        return {
            "submissions": [],
            "total": 0
        }
