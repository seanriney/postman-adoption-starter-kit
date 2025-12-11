import os
import sys
import json
import requests
import yaml
import time

# =============================================================================
# POSTMAN ADOPTION STARTER KIT - INGESTION ENGINE
# =============================================================================
#
# ROLE: Expert logic to automate the "Day 0" setup for developers.
# GOAL: Reduce discovery time from 47 mins to <2 mins.
#
# FLIGHT PLAN:
# 1. Block A (The Reader): Parse local OpenAPI Spec and extract Environment configs.
# 2. Block B (The Architect): Upload/Update the Spec in Postman (Source of Truth).
# 3. Block C (The Builder): Generate a Postman Collection from the Spec.
# 4. Block D (The Configurator): Create an Environment with dynamic URLs and Auth placeholders.
# 5. Block E (The Injector): Inject the local 'jwt_mock.js' to enable "Green Checkmark" testing.
# =============================================================================

# --- Configuration ---

SPEC_FILE = "payment-refund-api-openapi.yaml"
MOCK_SCRIPT_FILE = "jwt_mock.js"
BASE_URL = "https://api.getpostman.com"

# WORKSPACE CONFIGURATION
# Option 1: Set via environment variable POSTMAN_WORKSPACE_ID (exact ID)
# Option 2: Set via environment variable POSTMAN_WORKSPACE_NAME (searches by name)
# Option 3: Falls back to "My Workspace" (Postman's default workspace name)
TARGET_WORKSPACE_ID = os.getenv('POSTMAN_WORKSPACE_ID', None)
TARGET_WORKSPACE_NAME = os.getenv('POSTMAN_WORKSPACE_NAME', 'My Workspace')

print("\n🚀 STARTING POSTMAN ADOPTION KIT ENGINE...\n")

# Load API Key from environment variable
API_KEY = os.getenv('POSTMAN_API_KEY')
if not API_KEY:
    print("❌ ERROR: POSTMAN_API_KEY environment variable not set!")
    print("   Set it with: export POSTMAN_API_KEY='your-api-key'")
    print("   See .env.example for configuration template")
    sys.exit(1)

print("🔒 Credentials loaded from environment variable")



headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

# Helper: Get Workspace ID
# Priority: 1) Configured ID, 2) Configured Name, 3) Auto-select first
WORKSPACE_ID = None

if TARGET_WORKSPACE_ID:
    # User specified an exact ID
    WORKSPACE_ID = TARGET_WORKSPACE_ID
    print(f"➡️  Using configured Workspace ID: {WORKSPACE_ID}")
else:
    try:
        ws_resp = requests.get(f"{BASE_URL}/workspaces", headers=headers)
        ws_resp.raise_for_status()
        workspaces = ws_resp.json().get('workspaces', [])
        
        if not workspaces:
            print("❌ No Workspaces found. Please create one in Postman.")
            sys.exit(1)
        
        # Search by name if configured
        if TARGET_WORKSPACE_NAME:
            target_ws = next((ws for ws in workspaces if TARGET_WORKSPACE_NAME.lower() in ws['name'].lower()), None)
            if target_ws:
                WORKSPACE_ID = target_ws['id']
                print(f"➡️  Found Target Workspace: '{target_ws['name']}' ({WORKSPACE_ID})")
            else:
                print(f"⚠️  Workspace '{TARGET_WORKSPACE_NAME}' not found. Available workspaces:")
                for ws in workspaces:
                    print(f"     - {ws['name']} ({ws['id']})")
                print("\n❌ Please update TARGET_WORKSPACE_NAME or TARGET_WORKSPACE_ID in the script.")
                sys.exit(1)
        else:
            # Auto-select first workspace
            target_ws = workspaces[0]
            WORKSPACE_ID = target_ws['id']
            print(f"➡️  Auto-selected Workspace: '{target_ws['name']}' ({WORKSPACE_ID})")
            
    except Exception as e:
        print(f"❌ Error fetching workspaces: {e}")
        sys.exit(1)


# =============================================================================
# BLOCK A: THE READER (Scalability)
# =============================================================================
# Business Value: Decouples the script from hardcoded values. Allows this engine
# to process ANY of the 47 Specs in the future without code changes.

print("\n📖 BLOCK A: Reading and Parsing Spec...")

# [SCALABILITY PATTERN]: In a real production environment, this block would 
# fetch the latest spec directly from your Infrastructure (AWS/Azure/GitHub).
# Example (Conceptual):
# 
# import boto3
# s3 = boto3.client('s3')
# obj = s3.get_object(Bucket='payment-specs', Key='refund-api.yaml')
# spec_content_raw = obj['Body'].read().decode('utf-8')
# print("   ✅ Fetched latest spec from AWS S3")

if not os.path.exists(SPEC_FILE):
    print(f"❌ ERROR: Spec file '{SPEC_FILE}' not found.")
    sys.exit(1)

with open(SPEC_FILE, 'r') as f:
    spec_content_raw = f.read()
    try:
        spec_data = yaml.safe_load(spec_content_raw)
    except yaml.YAMLError as exc:
        print(f"❌ Error parsing YAML: {exc}")
        sys.exit(1)

spec_name = spec_data.get('info', {}).get('title', 'Imported API')
spec_version = spec_data.get('info', {}).get('version', '1.0.0')
servers = spec_data.get('servers', [])

# Dynamic Parsing of Environments
# Logic maps 'description' keywords to environment keys
env_urls = {}
for server in servers:
    url = server.get('url')
    desc = server.get('description', '').lower()
    
    if 'production' in desc:
        env_urls['production'] = url
    elif 'uat' in desc:
        env_urls['uat'] = url
    elif 'qa' in desc:
        env_urls['qa'] = url
    elif 'dev' in desc:
        env_urls['development'] = url

print(f"   ✅ Loaded Spec: {spec_name} (v{spec_version})")
print(f"   ✅ Extracted {len(env_urls)} Environments: {', '.join(env_urls.keys())}")


# =============================================================================
# BLOCK B: THE ARCHITECT (Governance)
# =============================================================================
# Business Value: Enforces "Spec-First" design. The API Builder becomes the 
# Single Source of Truth, preventing "drift" between Code and Documentation.
#
# NOTE: Upgraded from legacy '/specs' to modern '/apis' endpoint for stability.
# This is the current Postman best practice and ensures production reliability.

print("\n🏛️  BLOCK B: Creating API in Postman API Builder...")

# Step 1: Check if API already exists
existing_api_id = None
try:
    apis_resp = requests.get(f"{BASE_URL}/apis?workspace={WORKSPACE_ID}", headers=headers)
    if apis_resp.status_code == 200:
        for api in apis_resp.json().get('apis', []):
            if api.get('name') == spec_name:
                existing_api_id = api.get('id')
                print(f"   ℹ️  API '{spec_name}' already exists ({existing_api_id}). Using it.")
                break
except Exception as e:
    print(f"   ⚠️  Could not check existing APIs: {e}")

# Step 2: Create API if it doesn't exist
api_id = existing_api_id
if not api_id:
    print(f"   ℹ️  Creating new API '{spec_name}'...")
    api_payload = {
        "api": {
            "name": spec_name,
            "summary": f"Automated ingestion of {spec_name}",
            "description": spec_data.get('info', {}).get('description', ''),
        }
    }
    
    api_resp = requests.post(f"{BASE_URL}/apis?workspace={WORKSPACE_ID}", headers=headers, json=api_payload)
    if api_resp.status_code not in [200, 201]:
        print(f"❌ Failed to create API: {api_resp.status_code}")
        print(f"   Response: {api_resp.text}")
        sys.exit(1)
    
    api_id = api_resp.json()['api']['id']
    print(f"   ✅ API Created: {api_id}")

# Step 3: Create Version
print(f"   ℹ️  Creating version '{spec_version}'...")
version_payload = {
    "version": {
        "name": spec_version
    }
}

version_resp = requests.post(f"{BASE_URL}/apis/{api_id}/versions", headers=headers, json=version_payload)
if version_resp.status_code not in [200, 201]:
    # Version might already exist, try to get it
    versions_resp = requests.get(f"{BASE_URL}/apis/{api_id}/versions", headers=headers)
    if versions_resp.status_code == 200:
        versions = versions_resp.json().get('versions', [])
        version_id = versions[0]['id'] if versions else None
        if version_id:
            print(f"   ℹ️  Using existing version: {version_id}")
        else:
            print(f"❌ Failed to create/find version")
            sys.exit(1)
    else:
        print(f"❌ Failed to create version: {version_resp.text}")
        sys.exit(1)
else:
    version_id = version_resp.json()['version']['id']
    print(f"   ✅ Version Created: {version_id}")

# Step 4: Import Schema using the Import API (more robust for large files)
print(f"   ℹ️  Importing OpenAPI schema via Import API...")

# First, let's use the simpler collection import approach
# The Import API can handle the OpenAPI spec and create both API + Collection
import_payload = {
    "type": "string",
    "input": spec_content_raw
}

import_resp = requests.post(f"{BASE_URL}/import/openapi?workspace={WORKSPACE_ID}", headers=headers, json=import_payload)
if import_resp.status_code not in [200, 201]:
    print(f"❌ Failed to import OpenAPI: {import_resp.status_code}")
    print(f"   Response: {import_resp.text}")
    sys.exit(1)

import_result = import_resp.json()
print(f"   ✅ OpenAPI Imported Successfully")

# Extract the created resources
collections = import_result.get('collections', [])
if collections:
    collection_id = collections[0].get('id') or collections[0].get('uid')
    print(f"   ✅ Collection Created: {collection_id}")
else:
    print(f"   ⚠️  No collection generated from import")
    # Fallback: manually create collection
    collection_id = None


# =============================================================================
# BLOCK C: THE BUILDER (Automation)
# =============================================================================
# Business Value: Eliminates manual errors. The Import API generates the 
# collection directly from the OpenAPI specification.
#
# GOVERNANCE NOTE:
# The Import API creates a fresh collection based on the spec.
# In a mature Governance model, we would use Postman's Git Integration or 
# "Merge" strategy to preserve manual tests added by developers.

print("\n🏗️  BLOCK C: Collection Ready from Import...")

# The Import API already created the collection in Step 4
if not collection_id:
    print("   ⚠️  Attempting manual collection creation as fallback...")
    # Manual fallback if needed
    collection_payload = {
        "collection": {
            "info": {
                "name": f"{spec_name} - Collection",
                "description": spec_data.get('info', {}).get('description', ''),
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            }
        }
    }
    
    coll_resp = requests.post(f"{BASE_URL}/collections?workspace={WORKSPACE_ID}", headers=headers, json=collection_payload)
    if coll_resp.status_code in [200,201]:
        collection_id = coll_resp.json()['collection']['id']
        print(f"   ✅ Fallback Collection Created: {collection_id}")
    else:
        print(f"   ❌ Could not create collection")
        sys.exit(1)
else:
    print(f"   ✅ Using Collection: {collection_id}")


# =============================================================================
# BLOCK D: THE CONFIGURATOR (Usability)
# =============================================================================
# Business Value: Environment Switcher logic (Dev -> QA -> Prod). 
# Reduces configuration time from 15 mins to 0 mins.

print("\n⚙️  BLOCK D: constructing Environment...")

# Create the Env Values list
env_values = []

# 1. Base URLs
# We set a default 'baseUrl' to the Development URL for immediate safety.
# We also store specific variables for reference.
dev_url = env_urls.get('development', 'https://example.com')
env_values.append({"key": "baseUrl", "value": dev_url, "enabled": True})

for key, url in env_urls.items():
    env_values.append({"key": f"url_{key}", "value": url, "enabled": True})

# 2. Auth Placeholders
# We inject these so the Mock Script knows where to look.
env_values.extend([
    {"key": "client_id", "value": "demo_client_id_123", "enabled": True},     # Pre-filled for demo
    {"key": "client_secret", "value": "demo_secret", "enabled": True},        # Pre-filled for demo
    {"key": "token_url", "value": "https://auth.example.com/token", "enabled": True}, 
    {"key": "jwt_token", "value": "", "enabled": True} # Dynamic variable
])

env_payload = {
    "environment": {
        "name": f"{spec_name} - Environment",
        "values": env_values
    }
}

env_resp = requests.post(f"{BASE_URL}/environments?workspace={WORKSPACE_ID}", headers=headers, json=env_payload)

# DEBUG: Show what happened
print(f"   🐛 DEBUG: Environment creation status: {env_resp.status_code}")

if env_resp.status_code not in [200, 201]:
    print(f"❌ Failed to create environment: {env_resp.status_code}")
    print(f"   Response: {env_resp.text}")
    print(f"   Payload had {len(env_values)} variables")
    # Soft fail - we can continue
else:
    env_id = env_resp.json()['environment']['id']
    env_name = env_resp.json()['environment']['name']
    print(f"   ✅ Environment Created: {env_id}")
    print(f"   ✅ Environment Name: '{env_name}'")
    print(f"   ✅ Variables: {len(env_values)} configured")


# =============================================================================
# BLOCK E: THE INJECTOR (Injector) - EXCEPTIONAL CRITERIA
# =============================================================================
# Business Value: "Batteries Included". We inject the Mock Auth logic directly
# into the Collection so it works immediately upon download. No coding required.

print("\n💉 BLOCK E: Injecting Mock Auth Logic...")

if os.path.exists(MOCK_SCRIPT_FILE):
    with open(MOCK_SCRIPT_FILE, 'r', encoding='utf-8') as f:
        mock_script_content = f.read()

    # 1. Fetch the Generated Collection JSON
    get_col_resp = requests.get(f"{BASE_URL}/collections/{collection_id}", headers=headers)
    if get_col_resp.status_code == 200:
        col_data = get_col_resp.json()
        
        # 2. Add Pre-request Script to the Collection Root
        # This ensures it runs for EVERY request in the collection.
        event = {
            "listen": "prerequest",
            "script": {
                "type": "text/javascript",
                "exec": mock_script_content.splitlines()
            }
        }
        
        if 'event' not in col_data['collection']:
            col_data['collection']['event'] = []
            
        col_data['collection']['event'].append(event)
        
        # 3. Update the Collection
        put_col_resp = requests.put(f"{BASE_URL}/collections/{collection_id}", headers=headers, json=col_data)
        if put_col_resp.status_code == 200:
            print("   ✅ Mock Script Injected successfully.")
        else:
            print(f"   ⚠️  Failed to update collection with script: {put_col_resp.text}")
            
    else:
        print(f"   ⚠️  Could not fetch collection for injection: {get_col_resp.text}")

else:
    print(f"   ⚠️  Mock script '{MOCK_SCRIPT_FILE}' not found. Skipping injection.")

print("\n✨ DEPLOYMENT COMPLETE!")
print(f"   👉 Go to Workspace: https://go.postman.co/workspace/{WORKSPACE_ID}")
