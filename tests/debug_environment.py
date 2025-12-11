import os
import requests

# Debug script to verify environment creation
BASE_URL = "https://api.getpostman.com"
API_KEY = os.getenv('POSTMAN_API_KEY')
WORKSPACE_ID = os.getenv('POSTMAN_WORKSPACE_ID')

if not API_KEY:
    print("❌ Set POSTMAN_API_KEY environment variable")
    exit(1)

headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

print("🔍 Checking existing environments...\n")

env_resp = requests.get(f"{BASE_URL}/environments?workspace={WORKSPACE_ID}", headers=headers)
if env_resp.status_code == 200:
    envs = env_resp.json().get('environments', [])
    print(f"Found {len(envs)} environments:")
    for env in envs:
        print(f"  - {env['name']} (ID: {env['id']})")
        
        detail_resp = requests.get(f"{BASE_URL}/environments/{env['id']}", headers=headers)
        if detail_resp.status_code == 200:
            env_data = detail_resp.json().get('environment', {})
            values = env_data.get('values', [])
            print(f"    Variables: {len(values)}")
            for val in values:
                print(f"      - {val.get('key')}: {val.get('value', '(empty)')[:50]}")
        print()
else:
    print(f"Error: {env_resp.status_code} - {env_resp.text}")
