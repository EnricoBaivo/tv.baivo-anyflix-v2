import type { SearchResult } from "@/lib/api/hooks";
import type { components } from "@/lib/api/types";

/**
 * MediaSpotlightCompat - Compatible type for MediaCard and MediaRow components
 * Maps SearchResult and MediaInfo to a unified format
 */
export interface MediaSpotlightCompat {
  id: string;
  title: string;
  image_cover_url: string;
  image_backdrop_url: string | null;
  provider_url: string;
  provider: string;
  release_year: number | null;
  average_rating: number | null;
  votes: number;
  seasons_count: number | null;
  media_status: string | null;
  best_ranking: { rank: number; context: string } | null;
  logo_urls: string[] | null;
  trailers: unknown[] | null;
  clips: unknown[] | null;
  teasers: unknown[] | null;
}

type MediaInfo = components["schemas"]["MediaInfo"];

/**
 * Maps a single SearchResult to MediaSpotlightCompat format
 * @param result - SearchResult from API
 * @param index - Optional index for generating unique ID
 * @returns MediaSpotlightCompat object
 */
export function mapSearchResultToMediaSpotlight(
  result: SearchResult,
  index?: number
): MediaSpotlightCompat {
  const mediaInfo = result.media_info;
  const id = `${result.provider}-${result.link}-${index ?? Date.now()}`;

  return {
    id,
    title: result.name,
    image_cover_url: result.image_url,
    image_backdrop_url: mediaInfo?.backdrop_url ?? null,
    provider_url: result.link,
    provider: result.provider,
    release_year: mediaInfo?.start_year ?? null,
    average_rating: mediaInfo?.rating_value
      ? Math.round(mediaInfo.rating_value * 10)
      : null,
    votes: mediaInfo?.rating_count ?? 0,
    seasons_count: mediaInfo?.seasons_length ?? null,
    media_status: null, // Not available in SearchResult/MediaInfo
    best_ranking: null, // Not available in SearchResult/MediaInfo
    logo_urls: null, // Not available in SearchResult/MediaInfo
    trailers: mediaInfo?.trailer_url ? [mediaInfo.trailer_url] : null,
    clips: null,
    teasers: null,
  };
}

/**
 * Maps an array of SearchResult to MediaSpotlightCompat format
 * @param results - Array of SearchResult from API
 * @returns Array of MediaSpotlightCompat objects
 */
export function mapSearchResultsToMediaSpotlight(
  results: SearchResult[]
): MediaSpotlightCompat[] {
  return results.map((result, index) =>
    mapSearchResultToMediaSpotlight(result, index)
  );
}




