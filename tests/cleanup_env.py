import os
import requests

BASE_URL = "https://api.getpostman.com"
API_KEY = os.getenv('POSTMAN_API_KEY')

if not API_KEY:
    print("❌ Set POSTMAN_API_KEY environment variable")
    exit(1)

headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

# Delete the empty environment
ENV_ID = os.getenv('ENV_ID')
if not ENV_ID:
    print("❌ Set ENV_ID environment variable to delete")
    exit(1)

print(f"🗑️  Deleting environment {ENV_ID}...")
del_resp = requests.delete(f"{BASE_URL}/environments/{ENV_ID}", headers=headers)

if del_resp.status_code == 200:
    print("   ✅ Environment deleted successfully")
else:
    print(f"   ⚠️  Status: {del_resp.status_code} - {del_resp.text}")
