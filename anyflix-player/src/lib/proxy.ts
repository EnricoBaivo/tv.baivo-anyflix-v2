import { components } from "@/lib/api/types";

type VideoSource = components["schemas"]["VideoSource"];

const PROXY_BASE_URL =
  import.meta.env.VITE_PROXY_URL || "http://localhost:8081";

interface ProxyResponse {
  proxy_url: string;
  message?: string;
}

/**
 * Get a proxied URL for a video source
 * @param videoSource - The video source to proxy
 * @returns The proxied URL that can be used in the video player
 */
export async function getProxiedVideoUrl(
  videoSource: VideoSource
): Promise<string> {
  // If proxy is not required, return the original URL
  if (!videoSource.requires_proxy) {
    return videoSource.url;
  }
  console.log("Getting proxied video url for:", videoSource);
  try {
    const response = await fetch(`${PROXY_BASE_URL}/api/v1/proxy/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(videoSource),
    });

    if (!response.ok) {
      throw new Error(`Proxy service returned ${response.status}`);
    }

    const data: ProxyResponse = await response.json();

    // Return the full proxy URL
    return `${PROXY_BASE_URL}${data.proxy_url}`;
  } catch (error) {
    console.error("Failed to get proxied URL:", error);
    // Fallback to direct URL if proxy fails
    console.warn("Falling back to direct URL");
    return videoSource.url;
  }
}

/**
 * Check if the proxy service is available
 * @returns True if the proxy service is healthy
 */
export async function isProxyAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${PROXY_BASE_URL}/api/v1/health`, {
      method: "GET",
    });
    return response.ok;
  } catch (error) {
    console.error("Proxy service is not available:", error);
    return false;
  }
}
