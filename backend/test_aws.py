#!/usr/bin/env python3
"""
test_aws.py - Verify all AWS connections for Project Argus
Tests: DynamoDB (argus-submissions) + Bedrock (Claude Sonnet)
"""

import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

# Write output to file to avoid Windows encoding issues
output_lines = []
def log(msg=""):
    output_lines.append(msg)
    print(msg)

log("=" * 60)
log("  Project Argus -- AWS Connection Test")
log("=" * 60)

# --- 1. Check env vars ---
log("\n[1/4] Checking environment variables...")
region = os.getenv("AWS_REGION")
table_name = os.getenv("DYNAMODB_TABLE")
model_id = os.getenv("BEDROCK_MODEL_ID")
has_key = bool(os.getenv("AWS_ACCESS_KEY_ID"))
has_secret = bool(os.getenv("AWS_SECRET_ACCESS_KEY"))

log(f"  AWS_REGION            = {region}")
log(f"  DYNAMODB_TABLE        = {table_name}")
log(f"  BEDROCK_MODEL_ID      = {model_id}")
log(f"  AWS_ACCESS_KEY_ID     = {'[OK]' if has_key else '[FAIL] MISSING'}")
log(f"  AWS_SECRET_ACCESS_KEY = {'[OK]' if has_secret else '[FAIL] MISSING'}")

if not all([region, table_name, model_id, has_key, has_secret]):
    log("\n[FAIL] One or more env vars are missing.")
    with open("test_aws_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    exit(1)
log("  -> All env vars loaded [OK]")

# --- 2. Test DynamoDB ---
log(f"\n[2/4] Testing DynamoDB connection to '{table_name}'...")
import boto3
try:
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(table_name)
    status = table.table_status
    item_count = table.item_count
    log(f"  Table status : {status}")
    log(f"  Item count   : {item_count}")
    log(f"  Key schema   : {table.key_schema}")
    log("  -> DynamoDB connection [OK]")
except Exception as e:
    log(f"  [FAIL] DynamoDB error: {e}")

# --- 3. Test Bedrock ---
log(f"\n[3/4] Testing Bedrock with model '{model_id}'...")
try:
    bedrock = boto3.client("bedrock-runtime", region_name=region)
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 50,
        "temperature": 0.0,
        "messages": [
            {"role": "user", "content": "Reply with exactly: ARGUS_CONNECTION_OK"}
        ],
    }
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    reply = result["content"][0]["text"].strip()
    log(f"  Model response: {reply}")
    log("  -> Bedrock connection [OK]")
except Exception as e:
    log(f"  [FAIL] Bedrock error: {e}")

# --- 4. DynamoDB write/read ---
log(f"\n[4/4] Testing DynamoDB write/read cycle...")
try:
    from datetime import datetime
    test_id = f"_argus_test_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    table.put_item(Item={"listing_id": test_id, "test": True, "timestamp": datetime.utcnow().isoformat()})
    log(f"  Write test item '{test_id}' [OK]")
    resp = table.get_item(Key={"listing_id": test_id})
    if "Item" in resp:
        log(f"  Read back item  [OK]")
    table.delete_item(Key={"listing_id": test_id})
    log(f"  Cleanup deleted [OK]")
    log("  -> DynamoDB read/write cycle [OK]")
except Exception as e:
    log(f"  [FAIL] DynamoDB read/write error: {e}")

log("\n" + "=" * 60)
log("  All AWS connection tests completed!")
log("=" * 60)

# Save full output
with open("test_aws_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))
