// Quick test to check API connection
const API_URL = "http://localhost:8000";

async function testApiConnection() {
    console.log("Testing API connection to", API_URL);
    
    try {
        // Test health endpoint first
        console.log("\n1. Testing health endpoint...");
        const healthResponse = await fetch(`${API_URL}/anonymous/health`);
        console.log("Health status:", healthResponse.status);
        
        if (healthResponse.ok) {
            const healthData = await healthResponse.json();
            console.log("Health data:", healthData);
        } else {
            const errorText = await healthResponse.text();
            console.log("Health error:", errorText);
        }
        
        // Test rate limit endpoint
        console.log("\n2. Testing rate limit endpoint...");
        const rateLimitResponse = await fetch(`${API_URL}/anonymous/rate-limit`);
        console.log("Rate limit status:", rateLimitResponse.status);
        
        if (rateLimitResponse.ok) {
            const rateLimitData = await rateLimitResponse.json();
            console.log("Rate limit data:", rateLimitData);
        } else {
            const errorText = await rateLimitResponse.text();
            console.log("Rate limit error:", errorText);
        }
        
        // Test upload with a small file
        console.log("\n3. Testing file upload...");
        const formData = new FormData();
        
        // Create a small test file
        const testFile = new Blob(["test audio content"], { type: "audio/mp3" });
        formData.append("file", testFile, "test.mp3");
        formData.append("name", "Test Upload");
        formData.append("language", "en");
        
        const uploadResponse = await fetch(`${API_URL}/anonymous/upload`, {
            method: "POST",
            body: formData
        });
        
        console.log("Upload status:", uploadResponse.status);
        
        if (uploadResponse.ok) {
            const uploadData = await uploadResponse.json();
            console.log("Upload successful:", uploadData);
        } else {
            const errorText = await uploadResponse.text();
            console.log("Upload error:", errorText);
            
            // Try to parse as JSON
            try {
                const errorJson = JSON.parse(errorText);
                console.log("Upload error JSON:", errorJson);
            } catch (e) {
                console.log("Error is not JSON");
            }
        }
        
    } catch (error) {
        console.error("Test failed with error:", error);
    }
}

testApiConnection();
