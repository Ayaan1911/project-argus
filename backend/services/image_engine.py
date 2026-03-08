import boto3
import json
import base64
from typing import Optional
import os

def analyze_image(image_bytes: bytes, image_type: str) -> dict:
    """
    Analyze rental property image for scam indicators using Amazon Bedrock
    
    Args:
        image_bytes: Image file bytes
        image_type: MIME type (e.g., 'image/jpeg', 'image/png')
    
    Returns:
        dict with score, verdict, flags, reasoning
    """
    if not image_bytes:
        return {
            "score": 20,
            "verdict": "No image provided",
            "flags": [],
            "reasoning": "No image was provided for analysis"
        }
    
    # Check for demo/mock mode (no AWS credentials)
    if not os.getenv('AWS_ACCESS_KEY_ID') and not os.getenv('AWS_REGION'):
        return _mock_image_analysis()
    
    try:
        # Initialize Bedrock client
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'ap-south-1')
        )
        
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # System prompt for image fraud detection
        system_prompt = """You are a fraud detection expert analyzing rental property images for an Indian rental scam detection system.

Analyze this image and look for:
- Stock photos or hotel/resort style photography (too professional)
- Non-Indian interior design (Western furniture, non-Indian architecture)
- Watermarks from other websites or stock photo sites
- Inconsistent lighting suggesting photo manipulation
- Images that look like they belong to a different property type
- Generic lifestyle photos not showing actual property

Return ONLY a valid JSON object:
{
  'score': <integer 0-100 where 100 is highest scam risk>,
  'verdict': <'Looks Genuine' or 'Suspicious' or 'Likely Stolen'>,
  'flags': [<specific issues found, max 3>],
  'reasoning': <one sentence explanation>
}"""
        
        # Prepare the request body with image
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.1,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": "Analyze this rental property image for scam indicators."
                        }
                    ]
                }
            ]
        }
        
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0'),
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        response_text = response_body['content'][0]['text']
        
        # Extract JSON from response
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Parse the JSON response
        result = json.loads(response_text)
        
        return {
            "score": result.get("score", 50),
            "verdict": result.get("verdict", "Unable to analyze"),
            "flags": result.get("flags", []),
            "reasoning": result.get("reasoning", "Analysis completed")
        }
        
    except Exception as e:
        # Handle errors gracefully
        print(f"Error in image analysis: {str(e)}")
        return {
            "score": 50,
            "verdict": "Unable to analyze",
            "flags": ["Analysis service temporarily unavailable"],
            "reasoning": "Could not complete image analysis due to technical error"
        }

async def analyze_images(images: list) -> dict:
    """
    Analyze multiple images and aggregate results
    
    Args:
        images: List of image file objects
    
    Returns:
        dict with aggregated analysis results
    """
    if not images or len(images) == 0:
        return {
            "score": 20,
            "verdict": "No images provided",
            "flags": [],
            "reasoning": "No images were provided for analysis"
        }
    
    # Analyze first image (can be extended to analyze multiple)
    first_image = images[0]
    image_bytes = await first_image.read()
    image_type = first_image.content_type or "image/jpeg"
    
    return analyze_image(image_bytes, image_type)


def _mock_image_analysis() -> dict:
    """Mock image analysis for demo mode without AWS credentials"""
    return {
        "score": 30,
        "verdict": "Unable to analyze (Demo Mode)",
        "flags": ["Image analysis requires AWS Bedrock access"],
        "reasoning": "Running in demo mode without AWS credentials. Deploy to AWS for full image analysis."
    }
