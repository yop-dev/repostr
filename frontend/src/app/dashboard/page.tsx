"use client";

import { useAuth, useUser, UserButton } from "@clerk/nextjs";
import { useState, useEffect } from "react";

export default function DashboardPage() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();
  const [token, setToken] = useState<string | null>(null);
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Get and display the JWT
  useEffect(() => {
    async function fetchToken() {
      if (isSignedIn) {
        const jwt = await getToken();
        setToken(jwt);
      }
    }
    fetchToken();
  }, [isSignedIn, getToken]);

  // Test API call
  const testAPI = async () => {
    setLoading(true);
    try {
      const jwt = await getToken();
      const response = await fetch("http://localhost:8000/auth/me", {
        headers: {
          Authorization: `Bearer ${jwt}`,
        },
      });
      const data = await response.json();
      setApiResponse(data);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      setApiResponse({ error: errorMessage });
    }
    setLoading(false);
  };

  if (!isLoaded) return <div>Loading...</div>;
  if (!isSignedIn) return <div>Not signed in</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Repostr Dashboard</h1>
          <UserButton afterSignOutUrl="/" />
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">User Info</h2>
          <p className="text-gray-600">Email: {user?.primaryEmailAddress?.emailAddress}</p>
          <p className="text-gray-600">User ID: {user?.id}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Your JWT Token</h2>
          <p className="text-xs text-gray-500 mb-2">Use this in the backend API:</p>
          <div className="bg-gray-100 p-3 rounded overflow-x-auto">
            <code className="text-xs break-all">{token || "Loading..."}</code>
          </div>
          <button
            onClick={() => navigator.clipboard.writeText(token || "")}
            className="mt-3 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Copy Token
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Test API Connection</h2>
          <button
            onClick={testAPI}
            disabled={loading}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
          >
            {loading ? "Loading..." : "Test /auth/me Endpoint"}
          </button>
          {apiResponse && (
            <div className="mt-4 bg-gray-100 p-3 rounded">
              <pre className="text-xs overflow-x-auto">
                {JSON.stringify(apiResponse, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
