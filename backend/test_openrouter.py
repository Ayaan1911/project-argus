"""
test_openrouter.py - Test the full Argus pipeline via the running backend API
Tests: OpenRouter (AI explanation) + DynamoDB (storage) with the scam demo URL
"""
import sys
import json
import urllib.request
import urllib.error
import urllib.parse

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

API_URL = "http://localhost:8080"
SCAM_URL = "https://www.99acres.com/3-bhk-bedroom-apartment-flat-for-rent-in-total-environment-pursuit-of-a-radical-rhapsody-hoodi-bangalore-east-4303-sq-ft-spid-H89314277"

lines = []
def log(msg=""):
    lines.append(msg)
    print(msg)

log("=" * 60)
log("  Project Argus -- Full Pipeline Test")
log("  (OpenRouter for AI + DynamoDB for storage)")
log("=" * 60)

# 1. Test the /analyze/url endpoint
log(f"\n[1/2] Sending scam URL to {API_URL}/analyze/url ...")
log(f"  URL: ...spid-H89314277 (High Risk demo)")

try:
    payload = urllib.parse.urlencode({"url": SCAM_URL}).encode("utf-8")
    req = urllib.request.Request(
        f"{API_URL}/analyze/url",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("utf-8")
        result = json.loads(raw)

    log("\n  [OK] Response received!")
    log("\n  --- FULL JSON RESPONSE ---")
    pretty = json.dumps(result, indent=2, ensure_ascii=False)
    log(pretty)

    # Save JSON to file
    with open("test_openrouter_output.json", "w", encoding="utf-8") as f:
        f.write(pretty)

    # Summary
    log("\n  --- SUMMARY ---")
    log(f"  Risk Level  : {result.get('risk_level', 'N/A')}")
    log(f"  Risk Score  : {result.get('risk_score', 'N/A')}")
    log(f"  Confidence  : {result.get('confidence_score', 'N/A')}")
    exp = result.get('explanation', 'N/A') or 'N/A'
    log(f"  Explanation : {exp[:150]}...")

except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    log(f"\n  [FAIL] HTTP {e.code}: {body}")
except urllib.error.URLError as e:
    log(f"\n  [FAIL] Could not reach backend: {e}")
    log("  Make sure backend is running: python -m uvicorn main:app --port 8080")
except Exception as e:
    log(f"\n  [FAIL] Error: {type(e).__name__}: {e}")

# 2. Check DynamoDB for stored result
log(f"\n[2/2] Checking DynamoDB for stored submissions...")
try:
    req2 = urllib.request.Request(f"{API_URL}/submissions/?limit=3")
    with urllib.request.urlopen(req2, timeout=10) as resp2:
        subs = json.loads(resp2.read().decode("utf-8"))
    log(f"  Total submissions in DB: {subs.get('total', 0)}")
    if subs.get('submissions'):
        for s in subs['submissions'][:3]:
            log(f"    - {s.get('listing_id', '?')} | {s.get('timestamp', '?')}")
    else:
        log("  (No submissions yet)")
    log("  [OK] DynamoDB query succeeded")
except Exception as e:
    log(f"  [FAIL] DynamoDB check: {e}")

log("\n" + "=" * 60)
log("  Test completed!")
log("=" * 60)

# Save full log
with open("test_openrouter_log.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
