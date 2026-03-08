import boto3
import json
import os
from typing import Optional

def analyze_text(title: str, description: str, contact_number: Optional[str] = None) -> dict:
    """
    Analyze rental listing text for scam indicators using Amazon Bedrock
    
    Args:
        title: Listing title
        description: Listing description
        contact_number: Optional contact number
    
    Returns:
        dict with score, verdict, flags, reasoning
    """
    try:
        # Check for demo/mock mode (no AWS credentials)
        if not os.getenv('AWS_ACCESS_KEY_ID') and not os.getenv('AWS_REGION'):
            return _mock_text_analysis(title, description, contact_number)
        
        # Initialize Bedrock client
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'ap-south-1')
        )
        
        # Prepare the listing text
        listing_text = f"Title: {title}\n\nDescription: {description}"
        if contact_number:
            listing_text += f"\n\nContact: {contact_number}"
        
        # System prompt for fraud detection with cross-signal reasoning
        system_prompt = """You are an expert fraud detection system for Indian rental listings. You will receive BOTH the listing description AND a price analysis observation together.

Use CROSS-SIGNAL REASONING: if the price is already flagged as suspiciously low AND the description contains urgency tactics, that combination is a much stronger scam indicator than either signal alone. Your reasoning must explicitly connect these signals.

Look for these red flags in Indian rental scams:
- Urgency tactics: urgent, only today, limited time, hurry
- Advance payment pressure: token amount, advance, pay now
- Suspicious contact: WhatsApp only, no calls
- Vague descriptions with no specifics
- Too good to be true language with low prices
- Hinglish scam patterns: jaldi karo, sirf aaj, abhi contact
- Owner going abroad narrative
- Multiple people interested pressure tactics

Return ONLY a valid JSON object:
{
  'score': <0-100, where 100 is highest scam risk>,
  'verdict': <'Likely Genuine' or 'Suspicious' or 'High Scam Risk'>,
  'flags': [<max 4 specific red flags found with exact evidence>],
  'reasoning': <2 sentences explicitly connecting price signals and text signals together>
}"""
        
        # Prepare the request body
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.1,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": listing_text
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
        # Handle cases where Claude might wrap JSON in markdown code blocks
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
        print(f"Error in text analysis: {str(e)}")
        return {
            "score": 50,
            "verdict": "Unable to analyze",
            "flags": ["Analysis service temporarily unavailable"],
            "reasoning": "Could not complete text analysis due to technical error"
        }


def _mock_text_analysis(title: str, description: str, contact_number: Optional[str] = None) -> dict:
    """Mock text analysis for demo mode without AWS credentials"""
    score = 50
    flags = []
    
    # Check for urgency keywords
    urgency_words = ['urgent', 'hurry', 'today only', 'jaldi', 'limited time']
    if any(word in title.lower() or word in description.lower() for word in urgency_words):
        score += 20
        flags.append("Urgency tactics detected")
    
    # Check for payment pressure
    payment_words = ['token', 'advance', 'pay now', 'whatsapp only']
    if any(word in description.lower() for word in payment_words):
        score += 15
        flags.append("Advance payment pressure detected")
    
    # Check for vague language
    vague_words = ['nice', 'good', 'best']
    vague_count = sum(1 for word in vague_words if word in description.lower())
    if vague_count > 3:
        score += 10
        flags.append("Vague description with minimal details")
    
    # Check for WhatsApp only contact
    if contact_number and 'whatsapp' in description.lower():
        score += 10
        flags.append("WhatsApp-only contact (suspicious)")
    
    # Determine verdict
    if score >= 70:
        verdict = "High Scam Risk"
    elif score >= 50:
        verdict = "Suspicious"
    else:
        verdict = "Likely Genuine"
    
    reasoning = f"Text analysis detected {len(flags)} red flags in the listing description."
    
    return {
        "score": min(score, 100),
        "verdict": verdict,
        "flags": flags,
        "reasoning": reasoning
    }
