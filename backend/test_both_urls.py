"""
test_both_urls.py - Test both demo URLs through the full Argus pipeline
"""
import sys
import json
import urllib.request
import urllib.error
import urllib.parse

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

API_URL = "http://localhost:8080"
URLS = {
    "LOW_RISK": "https://www.99acres.com/4-bhk-bedroom-independent-house-villa-for-rent-in-dodsworth-layout-bangalore-east-6500-sq-ft-spid-R88345030",
    "HIGH_RISK": "https://www.99acres.com/3-bhk-bedroom-apartment-flat-for-rent-in-total-environment-pursuit-of-a-radical-rhapsody-hoodi-bangalore-east-4303-sq-ft-spid-H89314277",
}

lines = []
def log(msg=""):
    lines.append(msg)
    print(msg)

log("=" * 60)
log("  Project Argus -- Full Pipeline Test (Both URLs)")
log("  OpenRouter AI + DynamoDB Storage")
log("=" * 60)

results = {}

for label, url in URLS.items():
    log(f"\n{'─' * 60}")
    log(f"[TEST] {label}")
    log(f"  URL: ...{url.split('/')[-1][:50]}")
    log(f"  Sending to {API_URL}/analyze/url ...")
    
    try:
        payload = urllib.parse.urlencode({"url": url}).encode("utf-8")
        req = urllib.request.Request(
            f"{API_URL}/analyze/url",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        
        results[label] = result
        log(f"\n  [OK] Response received!")
        log(f"\n  --- JSON ---")
        log(json.dumps(result, indent=2, ensure_ascii=False))
        
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        log(f"  [FAIL] HTTP {e.code}: {body}")
    except Exception as e:
        log(f"  [FAIL] {type(e).__name__}: {e}")

# DynamoDB check
log(f"\n{'─' * 60}")
log("[CHECK] DynamoDB submissions...")
try:
    req2 = urllib.request.Request(f"{API_URL}/submissions/?limit=5")
    with urllib.request.urlopen(req2, timeout=10) as resp2:
        subs = json.loads(resp2.read().decode("utf-8"))
    log(f"  Total in DB: {subs.get('total', 0)}")
    for s in subs.get('submissions', [])[:5]:
        log(f"    - {s.get('listing_id', '?')} | score={s.get('final_score','?')} | {s.get('risk_level','?')}")
    log("  [OK]")
except Exception as e:
    log(f"  [FAIL] {e}")

# Comparison
if len(results) == 2:
    log(f"\n{'=' * 60}")
    log("  COMPARISON")
    log(f"{'=' * 60}")
    for label, r in results.items():
        log(f"  {label:10s} | risk_score={r.get('risk_score'):>3} | level={r.get('risk_level')}")
    
    s1 = results.get("LOW_RISK", {}).get("risk_score")
    s2 = results.get("HIGH_RISK", {}).get("risk_score")
    if s1 is not None and s2 is not None:
        if isinstance(s1, int) and isinstance(s2, int) and s1 != s2:
            log(f"\n  [PASS] Scores are different integers! ({s1} vs {s2})")
        elif s1 == s2:
            log(f"\n  [WARN] Scores are identical ({s1}) -- check pipeline")
        else:
            log(f"\n  [INFO] Scores: {s1} ({type(s1).__name__}) vs {s2} ({type(s2).__name__})")

log(f"\n{'=' * 60}")
log("  Test completed!")
log(f"{'=' * 60}")

with open("test_both_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

with open("test_both_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
