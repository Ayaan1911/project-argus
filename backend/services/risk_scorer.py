def calculate_final_score(price_result: dict, text_result: dict, image_result: dict) -> dict:
    """
    Calculate final risk score using weighted average of all analysis engines
    
    Args:
        price_result: Result from price_engine.analyze_price()
        text_result: Result from text_engine.analyze_text()
        image_result: Result from image_engine.analyze_image()
    
    Returns:
        dict with final_score, verdict, recommendations
    """
    # Extract scores from each engine
    price_score = price_result.get("score", 50)
    text_score = text_result.get("score", 50)
    image_score = image_result.get("score", 50)
    
    # Weighted scoring: Price 40%, Text 40%, Image 20%
    final_score = (price_score * 0.4) + (text_score * 0.4) + (image_score * 0.2)
    final_score = round(final_score)
    
    # Determine verdict based on final score
    if final_score <= 30:
        verdict = "✅ Likely Genuine"
    elif final_score <= 65:
        verdict = "⚠️ Suspicious"
    else:
        verdict = "🚨 High Scam Risk"
    
    # Generate recommendations based on score
    recommendations = generate_recommendations(final_score)
    
    return {
        "final_score": final_score,
        "verdict": verdict,
        "recommendations": recommendations
    }

def generate_recommendations(risk_score: int) -> list[str]:
    """
    Generate actionable recommendations based on risk score
    
    Args:
        risk_score: Final calculated risk score (0-100)
    
    Returns:
        List of recommendation strings
    """
    if risk_score > 65:
        return [
            "Do not pay any advance",
            "Verify property exists in person before any payment",
            "Video call the landlord and ask them to show the property live",
            "Report this listing if confirmed scam"
        ]
    elif risk_score > 30:
        return [
            "Visit property before paying token amount",
            "Verify broker identity with a government ID",
            "Check if price matches nearby listings"
        ]
    else:
        return [
            "Listing appears genuine - proceed with normal caution",
            "Always visit before paying"
        ]
