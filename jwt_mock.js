// jwt_mock.js - OAuth 2.0 Simulation Logic
// Purpose: Simulates a Token Exchange for the "Payment Refund API"
// Context: The provided spec URLs are example.com (non-functional).
//          This script enables immediate "Green Checkmark" testing without a live Auth Provider.

console.log("-----------------------------------------");
console.log("   POSTMAN ADOPTION STARTER KIT - MOCK AUTH   ");
console.log("-----------------------------------------");

// 1. Read Configuration from the Environment
const clientId = pm.environment.get("client_id");
const clientSecret = pm.environment.get("client_secret");
const tokenUrl = pm.environment.get("token_url"); // Placeholder for the real IdP

// 2. Validate Prerequisites
if (!clientId) {
    console.warn("⚠️ No 'client_id' found. Skipping Mock Auth generation.");
    // In a real scenario, we might fail the test, but for discovery, we let it pass or fail naturally.
    return;
}

// 3. Simulate the Token Exchange Logic
// In a real production script, this would be a pm.sendRequest() to the 'token_url'.
// Here, we simulate the network latency and immediate success to unblock the Developer.

const simulateAuth = () => {
    console.log(`🔄 Simulating OAuth 2.0 Exchange for Client ID: ${clientId}...`);
    
    // Simulate a JWT (Header.Payload.Signature)
    const mockToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." + 
                      btoa(JSON.stringify({
                          sub: clientId,
                          name: "Postman Case Study User",
                          iat: Math.floor(Date.now() / 1000),
                          exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour expiry
                          scope: "refunds:write refunds:read"
                      })).replace(/=/g, "") + 
                      ".simulated_signature_hash";

    // 4. Inject the Token into the Environment
    // The Collection Auth is set to "Bearer Token" using {{jwt_token}}
    pm.environment.set("jwt_token", mockToken);
    
    console.log("✅ SUCCESS: Mock JWT Token generated and injected.");
    console.log("🔑 Token preview: " + mockToken.substring(0, 20) + "...");
    console.log("💡 The request will now proceed using this token.");
};

// Check if we already have a valid token (Optimization)
const currentToken = pm.environment.get("jwt_token");
if (currentToken && !currentToken.includes("simulated")) {
    // If there's a real token manually put there, respect it.
    console.log("ℹ️ Existing token found. Using it.");
} else {
    simulateAuth();
}
