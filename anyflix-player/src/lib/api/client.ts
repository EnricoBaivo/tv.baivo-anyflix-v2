/**
 * Type-safe API client using swr-openapi
 * Generated from FastAPI OpenAPI schema with runtime validation
 */

import createClient from "openapi-fetch";
import {
  createQueryHook,
  createImmutableHook,
  createInfiniteHook,
  createMutateHook,
} from "swr-openapi";
import isEqual from "fast-deep-equal";
import type { paths } from "./types";

// Create the base client with your FastAPI backend URL
// In development, use Vite proxy to avoid CORS issues
const client = createClient<paths>({
  baseUrl: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request/response interceptors for better debugging and error handling
client.use({
  onRequest({ request, options }) {
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`🚀 API Request: ${request.method} ${request.url}`);
    }
    return request;
  },
  onResponse({ response, options }) {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.status} ${response.url}`);
    }
    return response;
  },
});

const prefix = "anyflix-api";

// Export typed SWR hooks
export const useQuery = createQueryHook(client, prefix);
export const useImmutable = createImmutableHook(client, prefix);
export const useInfinite = createInfiniteHook(client, prefix);
export const useMutate = createMutateHook(client, prefix, isEqual);

// Export the client for direct usage if needed
export { client };

// Export types for convenience
export type { paths } from "./types";
