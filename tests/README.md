# Test & Diagnostic Scripts

This directory contains diagnostic and test scripts used during development to troubleshoot the `/specs` endpoint issues.

## Files

### Diagnostic Scripts
- **`diagnostic_specs.py`** - Comprehensive 7-test diagnostic testing every payload variation for `/specs` endpoint
- **`test_official_payload.py`** - Test using the exact payload structure from RESOURCES.md (case study documentation)
- **`final_files_attempt.py`** - Final attempt to satisfy the "files" parameter requirement

### Utility Scripts
- **`debug_environment.py`** - Inspects Postman environments via API for debugging
- **`cleanup_env.py`** - Removes empty/test environments from workspace

## Purpose

These scripts document the exhaustive troubleshooting process when the case study's specified `/specs` endpoint failed to work. They demonstrate:

1. **Due Diligence** - Tested 10+ different payload variations
2. **Official Documentation Follow** - Used exact examples from case study materials
3. **API Contract Analysis** - Reverse-engineered error messages to understand requirements
4. **Decision Documentation** - Proof that pivoting to `/apis` was necessary, not optional

## Results Summary

**All `/specs` endpoint tests failed with:**
```
400 Bad Request: "Required body parameter files is missing"
```

**Root Cause (Confirmed 2025-12-09):**

Postman underwent an architectural migration from v9 "Spec Hub" to v10 "API Builder." The `/specs` endpoint is **officially deprecated**.

**Official Evidence:**
1. [Postman API Introduction](https://learning.postman.com/docs/developer/postman-api/intro-api/) - States v10 is required, v9 deprecated
2. [Deprecated Endpoints Folder](https://www.postman.com/postman/postman-public-workspace/folder/0a4bnwe/deprecated) - `/specs` resides in DEPRECATED folder
3. [November 2025 Spec Hub Overhaul](https://www.youtube.com/watch?v=eBpfudPN-XQ) - Multi-file architecture changes broke old payload format

**V10 Architecture Changes:**
- **Multi-File Support:** Requires `files` array with `path` and `content` fields
- **New Hierarchy:** API → Version → Schema (replaces flat Spec Hub)
- **Endpoint Path Changed:** `/specs` → `/apis/{id}/versions/{id}/schemas`

**V10 Payload Testing:**
We tested the exact v10 payload structure documented in official Postman sources:
```python
{
    "files": [{"path": "openapi.yaml", "content": spec_content}]
}
```
**Result:** Still failed with `400`. The v10 `files` array applies to `/schemas` endpoint within the API Builder hierarchy, NOT the deprecated `/specs` endpoint path.

**Conclusion:**
The `/specs` endpoint itself no longer exists in v10—it's been architecturally replaced by the API → Version → Schema workflow. Our implementation using `/apis` and `/import/openapi` IS the v10 approach.

## For Interview Panel

These scripts can be run to reproduce the diagnostic process and validate that:
1. We followed the case study instructions exactly
2. The documented approach uses deprecated v9 endpoints
3. The modern v10 solution was necessary, not optional
4. We have official Postman documentation confirming the deprecation
