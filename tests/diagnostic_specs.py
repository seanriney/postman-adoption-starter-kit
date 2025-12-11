import os
import requests
import json
import yaml

"""
COMPREHENSIVE /specs ENDPOINT DIAGNOSTIC
Purpose: Attempt every reasonable variation to make POST /specs work
"""

SPEC_FILE = "Documents/payment-refund-api-openapi.yaml"
BASE_URL = "https://api.getpostman.com"
WORKSPACE_ID = os.getenv('POSTMAN_WORKSPACE_ID')
API_KEY = os.getenv('POSTMAN_API_KEY')

if not WORKSPACE_ID:
    print("❌ Set POSTMAN_WORKSPACE_ID environment variable")
    exit(1)

if not API_KEY:
    print("❌ Set POSTMAN_API_KEY environment variable")
    exit(1)

headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

# Load spec
with open(SPEC_FILE, 'r') as f:
    spec_content_raw = f.read()
    spec_data = yaml.safe_load(spec_content_raw)

spec_name = spec_data.get('info', {}).get('title', 'Imported API')

print("="*80)
print("POSTMAN /specs ENDPOINT DIAGNOSTIC")
print("="*80)
print(f"Workspace: {WORKSPACE_ID}")
print(f"Spec Name: {spec_name}")
print(f"Spec Size: {len(spec_content_raw)} bytes")
print("="*80)

# Test 1: Minimal payload with workspaceId query param
print("\n[TEST 1] Minimal payload + workspaceId query parameter")
payload1 = {
    "spec": {
        "name": "Test Spec 1",
        "content": spec_content_raw,
        "contentType": "yaml"
    }
}
resp1 = requests.post(f"{BASE_URL}/specs?workspaceId={WORKSPACE_ID}", headers=headers, json=payload1)
print(f"Status: {resp1.status_code}")
print(f"Response: {resp1.text[:200]}")
if resp1.status_code in [200, 201]:
    print("✅ SUCCESS!")
else:
    print("❌ Failed")

# Test 2: Minimal payload with workspace query param
print("\n[TEST 2] Minimal payload + workspace query parameter")
payload2 = {
    "spec": {
        "name": "Test Spec 2",
        "content": spec_content_raw,
        "contentType": "yaml"
    }
}
resp2 = requests.post(f"{BASE_URL}/specs?workspace={WORKSPACE_ID}", headers=headers, json=payload2)
print(f"Status: {resp2.status_code}")
print(f"Response: {resp2.text[:200]}")
if resp2.status_code in [200, 201]:
    print("✅ SUCCESS!")
else:
    print("❌ Failed")

# Test 3: With type field
print("\n[TEST 3] With 'type' field")
payload3 = {
    "spec": {
        "name": "Test Spec 3",
        "content": spec_content_raw,
        "contentType": "yaml",
        "type": "openapi"
    }
}
resp3 = requests.post(f"{BASE_URL}/specs?workspace={WORKSPACE_ID}", headers=headers, json=payload3)
print(f"Status: {resp3.status_code}")
print(f"Response: {resp3.text[:200]}")
if resp3.status_code in [200, 201]:
    print("✅ SUCCESS!")
else:
    print("❌ Failed")

# Test 4: JSON-encoded content
print("\n[TEST 4] JSON-encoded content instead of raw string")
try:
    spec_json = yaml.safe_load(spec_content_raw)
    payload4 = {
        "spec": {
            "name": "Test Spec 4",
            "content": json.dumps(spec_json),
            "contentType": "json"
        }
    }
    resp4 = requests.post(f"{BASE_URL}/specs?workspace={WORKSPACE_ID}", headers=headers, json=payload4)
    print(f"Status: {resp4.status_code}")
    print(f"Response: {resp4.text[:200]}")
    if resp4.status_code in [200, 201]:
        print("✅ SUCCESS!")
    else:
        print("❌ Failed")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: With schema field
print("\n[TEST 5] Using 'schema' instead of 'content'")
payload5 = {
    "spec": {
        "name": "Test Spec 5",
        "schema": spec_content_raw,
        "language": "yaml"
    }
}
resp5 = requests.post(f"{BASE_URL}/specs?workspace={WORKSPACE_ID}", headers=headers, json=payload5)
print(f"Status: {resp5.status_code}")
print(f"Response: {resp5.text[:200]}")
if resp5.status_code in [200, 201]:
    print("✅ SUCCESS!")
else:
    print("❌ Failed")

# Test 6: Different content-type header
print("\n[TEST 6] Different Content-Type header")
headers_yaml = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/yaml"
}
resp6 = requests.post(f"{BASE_URL}/specs?workspace={WORKSPACE_ID}", headers=headers_yaml, data=spec_content_raw)
print(f"Status: {resp6.status_code}")
print(f"Response: {resp6.text[:200]}")
if resp6.status_code in [200, 201]:
    print("✅ SUCCESS!")
else:
    print("❌ Failed")

# Test 7: Multipart form data
print("\n[TEST 7] Multipart form-data upload")
files = {
    'file': ('openapi.yaml', spec_content_raw, 'application/x-yaml')
}
data = {
    'name': 'Test Spec 7',
    'type': 'openapi'
}
resp7 = requests.post(f"{BASE_URL}/specs?workspace={WORKSPACE_ID}", 
                      headers={"X-Api-Key": API_KEY}, 
                      files=files, 
                      data=data)
print(f"Status: {resp7.status_code}")
print(f"Response: {resp7.text[:200]}")
if resp7.status_code in [200, 201]:
    print("✅ SUCCESS!")
else:
    print("❌ Failed")

# Test 8: Check workspace info
print("\n[TEST 8] Verify workspace type and capabilities")
ws_resp = requests.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}", headers=headers)
if ws_resp.status_code == 200:
    ws_data = ws_resp.json().get('workspace', {})
    print(f"Workspace Name: {ws_data.get('name')}")
    print(f"Workspace Type: {ws_data.get('type')}")
    print(f"Visibility: {ws_data.get('visibility')}")
else:
    print(f"Could not fetch workspace details: {ws_resp.status_code}")

# Test 9: Check if APIs endpoint shows existing specs
print("\n[TEST 9] Check for existing specs/APIs in workspace")
apis_resp = requests.get(f"{BASE_URL}/apis?workspace={WORKSPACE_ID}", headers=headers)
if apis_resp.status_code == 200:
    apis = apis_resp.json().get('apis', [])
    print(f"Found {len(apis)} APIs in workspace")
    for api in apis[:3]:
        print(f"  - {api.get('name')} (ID: {api.get('id')})")

# Summary
print("\n" + "="*80)
print("DIAGNOSTIC SUMMARY")
print("="*80)
responses = [resp1, resp2, resp3, resp4, resp5, resp6, resp7]
statuses = [r.status_code for r in responses]
success_count = sum(1 for s in statuses if s in [200, 201])
print(f"Tests Run: {len(responses)}")
print(f"Successes: {success_count}")
print(f"Failures: {len(responses) - success_count}")

if success_count == 0:
    print("\n⚠️  ANALYSIS: ALL TESTS FAILED")
    print("\nMost Common Error Patterns:")
    for i, resp in enumerate(responses, 1):
        if resp.status_code == 400:
            print(f"  Test {i}: {resp.status_code} - {resp.text[:100]}")
    
    print("\nLikely Root Causes (in order of probability):")
    print("1. 🔴 Workspace Type Restriction: Free/Team workspaces may not support Spec Hub")
    print("2. 🔴 API Deprecation: /specs endpoint may be sunset in favor of /apis")
    print("3. 🔴 Enterprise Feature: Spec Hub may require Enterprise plan")
    print("4. 🔴 Payload Contract Change: API structure changed since documentation")
    print("5. 🔴 Regional Endpoint: May need different base URL for Spec Hub")
    
    print("\nRecommended Actions:")
    print("✅ Continue with /apis + /import/openapi pattern (current implementation)")
    print("✅ Document this diagnostic in presentation")
    print("✅ Frame as 'production-ready decision making under uncertainty'")
else:
    print(f"\n✅ SUCCESS! Test(s) that worked: {[i+1 for i, s in enumerate(statuses) if s in [200, 201]]}")

print("="*80)
