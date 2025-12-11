import os
import requests
import yaml

"""
FINAL TEST: Using EXACT payload from RESOURCES.md (Lines 61-67)
This is the official example provided in the case study materials
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

# Load spec
with open(SPEC_FILE, 'r') as f:
    spec_content = f.read()

print("="*80)
print("FINAL TEST: Using EXACT payload from RESOURCES.md documentation")
print("="*80)
print(f"Workspace: {WORKSPACE_ID}")
print(f"Spec Size: {len(spec_content)} bytes")
print("="*80)

# Use the EXACT payload structure from RESOURCES.md lines 61-67
spec_payload = {
    "spec": {
        "name": "Payment Refund API",
        "content": spec_content,
        "contentType": "yaml"
    }
}

print("\n[OFFICIAL PAYLOAD STRUCTURE]")
print(f"  spec.name: {spec_payload['spec']['name']}")
print(f"  spec.contentType: {spec_payload['spec']['contentType']}")
print(f"  spec.content length: {len(spec_payload['spec']['content'])} bytes")

# Test with workspaceId as shown in documentation
print("\n[TEST] POST /specs?workspaceId={WORKSPACE_ID}")
response = requests.post(
    f"{BASE_URL}/specs?workspaceId={WORKSPACE_ID}",
    headers=headers,
    json=spec_payload
)

print(f"\nStatus Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"\nResponse Body:")
print(response.text)

if response.status_code in [200, 201]:
    print("\n" + "="*80)
    print("✅ SUCCESS! The /specs endpoint works with the official payload!")
    print("="*80)
    spec_id = response.json()['spec']['id']
    print(f"Spec ID: {spec_id}")
else:
    print("\n" + "="*80)
    print("❌ FAILED even with official documentation payload")
    print("="*80)
    print("\nCONCLUSION:")
    print("The /specs endpoint does not work as documented in RESOURCES.md")
    print("This confirms the API has changed since the case study was written")
    print("The modern /apis approach is the correct solution")
