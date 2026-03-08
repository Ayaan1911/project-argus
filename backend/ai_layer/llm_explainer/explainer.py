"""
ai_layer/llm_explainer/explainer.py
=====================================
Stage 5 of the Argus AI Pipeline.

Generates a human-readable explanation of the anomaly detection result.

Supported LLM providers (in order of preference):
  • openrouter — qwen/qwen3-vl-235b-a22b-thinking via OpenRouter API
                 (uses the OpenAI-compatible Python SDK)
  • bedrock    — Claude 3 Haiku via AWS Bedrock
  • openai     — GPT-4o-mini via OpenAI native API
  • mock       — Rule-based fallback, always works, no API key required

Environment variables:
  OPENROUTER_API_KEY   — required for "openrouter" provider
  OPENAI_API_KEY       — required for "openai" provider
  AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY — required for "bedrock"
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt template (language-model agnostic)
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = (
    "You are Argus, an AI system that helps renters detect potentially fraudulent "
    "rental listings. A machine learning model has analyzed a rental listing and "
    "produced several signals that may indicate risk. Explain the result in simple "
    "language so that a normal renter can understand it. Do not mention machine "
    "learning algorithms. Focus on signals renters care about. If risk is high, "
    "suggest verifying the property before sending payment. Keep the explanation "
    "under 120 words."
)

_OPENROUTER_MODEL = "qwen/qwen3-vl-235b-a22b-thinking"
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class LLMExplainer:
    """
    Generates natural language explanations for anomaly detection results.

    Usage:
        explainer = LLMExplainer(provider="openrouter")
        text = explainer.explain(listing, prediction)
    """

    def __init__(self, provider: str = "openrouter"):
        """
        Args:
            provider: One of "openrouter" | "bedrock" | "openai" | "mock".
        """
        self.provider = provider

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def explain(self, listing: dict, prediction: dict) -> str:
        """
        Generate a plain-English explanation for a scam prediction.

        Args:
            listing:    Full listing dict.
            prediction: Output of ScamPredictor.predict().

        Returns:
            Explanation string (≤ 120 words).
        """
        prompt = self._build_prompt(listing, prediction)

        if self.provider == "mock":
            return self._fallback_explanation(listing, prediction)

        if self.provider == "openrouter":
            try:
                return self._call_openrouter(prompt)
            except Exception as exc:
                logger.warning(f"OpenRouter unavailable ({exc}). Using fallback.")
                return self._fallback_explanation(listing, prediction)

        if self.provider == "bedrock":
            try:
                return self._call_bedrock(prompt)
            except Exception as exc:
                logger.warning(f"Bedrock unavailable ({exc}). Using fallback.")
                return self._fallback_explanation(listing, prediction)

        if self.provider == "openai":
            try:
                return self._call_openai(prompt)
            except Exception as exc:
                logger.warning(f"OpenAI unavailable ({exc}). Using fallback.")
                return self._fallback_explanation(listing, prediction)

        return self._fallback_explanation(listing, prediction)

    # ------------------------------------------------------------------
    # Prompt builder
    # ------------------------------------------------------------------

    def _build_prompt(self, listing: dict, prediction: dict) -> str:
        features  = prediction.get("features_used", {})
        city      = listing.get("city", "unknown")
        price     = listing.get("price", "N/A")
        risk_level  = prediction.get("risk_level", "Unknown")
        risk_score  = prediction.get("risk_score", 0.0)

        price_ratio   = features.get("price_vs_city_median", 1.0)
        urgency_count = int(features.get("urgency_keyword_count", 0))
        phone_reuse   = int(features.get("phone_reuse_count", 1))
        image_count   = int(features.get("image_count", 0))

        return (
            f"Listing Analysis Signals:\n\n"
            f"Risk Level: {risk_level}\n"
            f"Anomaly Score: {risk_score:.4f}\n"
            f"City: {city.capitalize()}\n"
            f"Listed Price: Rs.{price}/month\n"
            f"Price vs City Median: {price_ratio:.2f}x\n"
            f"Urgency Keyword Count: {urgency_count}\n"
            f"Phone Reuse Count: {phone_reuse}\n"
            f"Image Count: {image_count}\n\n"
            f"Explain why this listing received the '{risk_level}' classification. "
            f"Follow the guidelines: simple language, no ML jargon, under 120 words."
        )

    # ------------------------------------------------------------------
    # LLM backends
    # ------------------------------------------------------------------

    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter using the OpenAI-compatible Python SDK with retry logic."""
        import time

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "Please set OPENROUTER_API_KEY in your environment or .env file."
            )
        logger.info(f"OpenRouter: API key loaded (ends ...{api_key[-6:]})")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai package required for OpenRouter. "
                "Install it: pip install openai"
            ) from exc

        client = OpenAI(
            api_key=api_key,
            base_url=_OPENROUTER_BASE_URL,
            timeout=30.0,
            default_headers={
                "HTTP-Referer": "https://github.com/project-argus",
                "X-Title":      "Project Argus - Rental Scam Detector",
            },
        )

        max_retries = 2
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"OpenRouter: Attempt {attempt}/{max_retries}...")
                response = client.chat.completions.create(
                    model=_OPENROUTER_MODEL,
                    messages=[
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user",   "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=200,
                )
                text = response.choices[0].message.content.strip()
                logger.info(f"OpenRouter: Success on attempt {attempt}")
                return text
            except Exception as e:
                last_error = e
                logger.warning(f"OpenRouter: Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    time.sleep(2 * attempt)  # exponential backoff

        raise last_error

    def _call_bedrock(self, prompt: str) -> str:
        import boto3

        client = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "ap-south-1"),
        )
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": f"{_SYSTEM_PROMPT}\n\n{prompt}"}],
        })
        response = client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(response["body"].read())
        return result["content"][0]["text"].strip()

    def _call_openai(self, prompt: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=300,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    # ------------------------------------------------------------------
    # Rule-based fallback (no API key required)
    # ------------------------------------------------------------------

    def _fallback_explanation(self, listing: dict, prediction: dict) -> str:
        features    = prediction.get("features_used", {})
        risk_level  = prediction.get("risk_level", "Unknown")
        risk_score  = prediction.get("risk_score", 0.0)
        city        = listing.get("city", "this city")
        price       = listing.get("price", "N/A")
        price_ratio = features.get("price_vs_city_median", 1.0)
        urgency     = int(features.get("urgency_keyword_count", 0))
        phone_reuse = int(features.get("phone_reuse_count", 1))
        image_count = int(features.get("image_count", 0))

        parts = [
            f"This listing has been classified as **{risk_level}** "
            f"(anomaly score: {risk_score:.3f})."
        ]

        if price_ratio < 0.6:
            parts.append(
                f"The listed price of ₹{price}/month is only {price_ratio:.0%} of the "
                f"typical rent in {city}, which is a common red flag for rental scams."
            )
        elif price_ratio > 1.5:
            parts.append(
                f"The price (₹{price}/month) is unusually high at {price_ratio:.0%} of "
                f"the city median, which may indicate a fraudulent premium listing."
            )

        if urgency > 0:
            parts.append(
                f"The description contains {urgency} urgency keyword(s) such as 'token', "
                f"'immediate', or 'advance' — language frequently associated with scams."
            )

        if phone_reuse > 3:
            parts.append(
                f"The contact number appears across {phone_reuse} listings, "
                f"which is a strong indicator of a high-volume fraudulent broker."
            )

        if image_count == 0:
            parts.append("The listing has no photos, which is unusual for a legitimate property.")

        if risk_level in ("High Risk", "Suspicious"):
            parts.append(
                "We strongly advise verifying the property in person and never "
                "transferring an advance payment without a signed rental agreement."
            )
        else:
            parts.append(
                "Overall signals appear normal, but always verify the property "
                "in person before making any payment."
            )

        return " ".join(parts)
