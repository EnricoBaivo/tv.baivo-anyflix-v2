/**
 * Utility functions to map API response types to component-compatible formats
 */

import type { components } from "@/lib/api/types";

type SearchResult = components["schemas"]["SearchResult"];

/**
 * MediaSpotlight-like interface for backward compatibility with MediaCard
 * This is a compatibility layer until MediaCard is fully migrated to SearchResult
 */
export interface MediaSpotlightCompat {
  id: string;
  title: string;
  name?: string;
  image_cover_url: string;
  image_backdrop_url?: string;
  provider_url: string;
  provider: string;
  release_year?: number | null;
  average_rating?: number | null;
  votes?: number;
  seasons_count?: number | null;
  media_status?: string | null;
  best_ranking?: {
    rank: number;
    context: string;
  } | null;
  logo_urls?: string[];
  trailers?: any[];
  clips?: any[];
  teasers?: any[];
}

/**
 * Maps SearchResult to MediaSpotlightCompat format for use with MediaCard
 */
export function mapSearchResultToMediaSpotlight(
  result: SearchResult,
  index: number = 0
): MediaSpotlightCompat {
  // Use link as unique identifier, fallback to index
  const id = result.link || `search-result-${index}`;
  
  // Extract year from media_info if available
  const releaseYear = result.media_info?.start_year || null;
  
  // Extract rating from media_info if available
  const rating = result.media_info?.rating_value || null;
  const ratingCount = result.media_info?.rating_count || 0;
  
  // Extract seasons/episodes count from media_info
  const seasonsCount = result.media_info?.seasons_length || null;
  
  return {
    id,
    title: result.name,
    name: result.name,
    image_cover_url: result.image_url,
    image_backdrop_url: result.media_info?.backdrop_url || result.image_url,
    provider_url: result.link,
    provider: result.provider,
    release_year: releaseYear,
    average_rating: rating ? Math.round(rating * 10) : null, // Convert to percentage if needed
    votes: ratingCount,
    seasons_count: seasonsCount,
    media_status: null, // Not available in SearchResult
    best_ranking: null, // Not available in SearchResult
    logo_urls: result.media_info?.cover_image_url ? [result.media_info.cover_image_url] : [],
    trailers: [],
    clips: [],
    teasers: [],
  };
}

/**
 * Maps an array of SearchResult to MediaSpotlightCompat array
 */
export function mapSearchResultsToMediaSpotlight(
  results: SearchResult[]
): MediaSpotlightCompat[] {
  return results.map((result, index) => mapSearchResultToMediaSpotlight(result, index));
}

