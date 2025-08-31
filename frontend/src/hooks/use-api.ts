"use client";

import { useAuth } from "@clerk/nextjs";
import { ApiClient } from "@/lib/api/client";
import { useMemo } from "react";

export function useApi() {
  const { getToken } = useAuth();

  const apiClient = useMemo(() => {
    return new ApiClient(getToken);
  }, [getToken]);

  return apiClient;
}
