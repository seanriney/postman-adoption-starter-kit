import os
import requests

"""
FINAL V10 TEST: Using exact v10 schema structure from SpecHub.txt
Lines 11-13: "files array containing: path (string) and content (string)"
"""

SPEC_FILE = "Documents/payment-refund-api-openapi.yaml"
BASE_URL = "https://api.getpostman.com"
WORKSPACE_ID = os.getenv('POSTMAN_WORKSPACE_ID')
API_KEY = os.getenv('POSTMAN_API_KEY')

if not API_KEY:
    print("❌ Set POSTMAN_API_KEY environment variable")
    exit(1)

headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

with open(SPEC_FILE, 'r') as f:
    spec_content = f.read()

print("="*80)
print("V10 PAYLOAD TEST: Using exact structure from SpecHub.txt documentation")
print("="*80)

# Test 1: Exact v10 structure - files array with path + content
print("\n[TEST 1] V10 format: files array with 'path' and 'content'")
v10_payload = {
    "files": [
        {
            "path": "openapi.yaml",
            "content": spec_content
        }
    ]
}

resp1 = requests.post(f"{BASE_URL}/specs?workspaceId={WORKSPACE_ID}", headers=headers, json=v10_payload)
print(f"Status: {resp1.status_code}")
print(f"Response: {resp1.text[:400]}")

if resp1.status_code in [200, 201]:
    print("\n✅ SUCCESS! V10 format works!")
else:
    print("\n[TEST 2] V10 format with root file designation")
    # SpecHub.txt Line 43: "One file must be designated as root"
    v10_payload_root = {
        "files": [
            {
                "path": "openapi.yaml",
                "content": spec_content,
                "root": True
            }
        ]
    }
    
    resp2 = requests.post(f"{BASE_URL}/specs?workspaceId={WORKSPACE_ID}", headers=headers, json=v10_payload_root)
    print(f"Status: {resp2.status_code}")
    print(f"Response: {resp2.text[:400]}")
    
    if resp2.status_code in [200, 201]:
        print("\n✅ SUCCESS! V10 format with root flag works!")
    else:
        print("\n[TEST 3] Maybe needs spec metadata too?")
        v10_payload_meta = {
            "spec": {
                "name": "Payment Refund API"
            },
            "files": [
                {
                    "path": "openapi.yaml",
                    "content": spec_content
                }
            ]
        }
        
        resp3 = requests.post(f"{BASE_URL}/specs?workspaceId={WORKSPACE_ID}", headers=headers, json=v10_payload_meta)
        print(f"Status: {resp3.status_code}")
        print(f"Response: {resp3.text[:400]}")
        
        if resp3.status_code not in [200, 201]:
            print("\n" + "="*80)
            print("CONCLUSION: Even v10 format doesn't work with /specs endpoint")
            print("="*80)
            print("Possible reasons:")
            print("1. /specs endpoint is fully deprecated (not just payload changed)")
            print("2. Multi-file specs require /apis workflow, not /specs")
            print("3. Schema creation must go through /apis/{id}/versions/{id}/schemas")
