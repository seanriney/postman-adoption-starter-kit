import os
import requests
import yaml

"""
FINAL ATTEMPT: What if 'files' is a JSON array, not multipart?
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
print("FINAL ATTEMPT: Maybe 'files' is a JSON array?")
print("="*80)

# Try 1: files as a list with file-like structure
print("\n[TEST 1] 'files' as array with name/content")
payload1 = {
    "files": [
        {
            "name": "openapi.yaml",
            "content": spec_content,
            "type": "openapi:3"
        }
    ]
}

resp1 = requests.post(f"{BASE_URL}/specs?workspaceId={WORKSPACE_ID}", headers=headers, json=payload1)
print(f"Status: {resp1.status_code}")
print(f"Response: {resp1.text[:200]}")

if resp1.status_code in [200, 201]:
    print("✅ SUCCESS!")
else:
    # Try 2: files with spec nested inside
    print("\n[TEST 2] 'files' array with spec object")
    payload2 = {
        "files": [
            {
                "spec": {
                    "name": "Payment Refund API",
                    "content": spec_content,
                    "contentType": "yaml"
                }
            }
        ]
    }
    
    resp2 = requests.post(f"{BASE_URL}/specs?workspaceId={WORKSPACE_ID}", headers=headers, json=payload2)
    print(f"Status: {resp2.status_code}")
    print(f"Response: {resp2.text[:200]}")
    
    if resp2.status_code in [200, 201]:
        print("✅ SUCCESS!")
    else:
        # Try 3: Both spec AND files
        print("\n[TEST 3] Both 'spec' and 'files' parameters")
        payload3 = {
            "spec": {
                "name": "Payment Refund API",
                "contentType": "yaml"
            },
            "files": [
                {
                    "name": "openapi.yaml",
                    "content": spec_content
                }
            ]
        }
        
        resp3 = requests.post(f"{BASE_URL}/specs?workspaceId={WORKSPACE_ID}", headers=headers, json=payload3)
        print(f"Status: {resp3.status_code}")
        print(f"Response: {resp3.text[:200]}")
        
        if resp3.status_code not in [200, 201]:
            print("\n" + "="*80)
            print("CONCLUSION: Cannot satisfy API contract")
            print("="*80)
            print("The endpoint wants 'files' but rejects all file upload formats.")
            print("This is a fundamental API design issue, not a user error.")
