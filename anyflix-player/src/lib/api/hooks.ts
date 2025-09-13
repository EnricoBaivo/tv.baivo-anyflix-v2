/**
 * Specialized API hooks for Anyflix media endpoints
 * Type-safe wrappers around the base swr-openapi hooks
 */

import { useQuery, useMutate } from "./client";
import type { paths } from "./types";

// Type helpers for better IntelliSense
type ApiPaths = paths;
type GetEndpoint<T extends keyof ApiPaths> = ApiPaths[T] extends { get: unknown } ? T : never;
type PostEndpoint<T extends keyof ApiPaths> = ApiPaths[T] extends { post: unknown } ? T : never;

// =============================================
// Source Management Hooks
// =============================================

/**
 * Get all available media sources
 */
export const useSources = () => {
  return useQuery("/sources/", {});
};

/**
 * Get source-specific preferences/configuration
 */
export const useSourcePreferences = (source: string) => {
  return useQuery("/sources/{source}/preferences", {
    params: {
      path: { source },
    },
  });
};

// =============================================
// Content Discovery Hooks
// =============================================

/**
 * Get popular content from a source with pagination
 */
export const usePopular = (source: string, page: number = 1) => {
  return useQuery("/sources/{source}/popular", {
    params: {
      path: { source },
      query: { page },
    },
  });
};

/**
 * Get latest updates from a source with pagination
 */
export const useLatest = (source: string, page: number = 1) => {
  return useQuery("/sources/{source}/latest", {
    params: {
      path: { source },
      query: { page },
    },
  });
};

/**
 * Search content with query string (only searches when query is valid)
 */
export const useSearch = (source: string, query: string, page: number = 1, lang?: string) => {
  const result = useQuery("/sources/{source}/search", {
    params: {
      path: { source },
      query: { q: query, page, ...(lang && { lang }) },
    },
  });

  // Return disabled state if query is too short
  if (!query || query.length < 1) {
    return {
      ...result,
      data: undefined,
      error: undefined,
      isLoading: false,
      isValidating: false,
    };
  }

  return result;
};

// =============================================
// Series Structure Hooks
// =============================================

/**
 * Get complete series data with hierarchical structure
 */
export const useSeriesDetail = (source: string, url: string) => {
  return useQuery("/sources/{source}/series", {
    params: {
      path: { source },
      query: { url },
    },
  });
};

/**
 * Get all seasons for a series
 */
export const useSeriesSeasons = (source: string, url: string) => {
  return useQuery("/sources/{source}/series/seasons", {
    params: {
      path: { source },
      query: { url },
    },
  });
};

/**
 * Get specific season details
 */
export const useSeason = (source: string, seasonNum: number, url: string) => {
  return useQuery("/sources/{source}/series/seasons/{season_num}", {
    params: {
      path: { source, season_num: seasonNum },
      query: { url },
    },
  });
};

/**
 * Get specific episode details
 */
export const useEpisode = (
  source: string, 
  seasonNum: number, 
  episodeNum: number, 
  url: string
) => {
  return useQuery("/sources/{source}/series/seasons/{season_num}/episodes/{episode_num}", {
    params: {
      path: { source, season_num: seasonNum, episode_num: episodeNum },
      query: { url },
    },
  });
};

/**
 * Get all movies/OVAs/specials for a series
 */
export const useSeriesMovies = (source: string, url: string) => {
  return useQuery("/sources/{source}/series/movies", {
    params: {
      path: { source },
      query: { url },
    },
  });
};

/**
 * Get specific movie/OVA details
 */
export const useMovie = (source: string, movieNum: number, url: string) => {
  return useQuery("/sources/{source}/series/movies/{movie_num}", {
    params: {
      path: { source, movie_num: movieNum },
      query: { url },
    },
  });
};

// =============================================
// Video & Media Hooks
// =============================================

/**
 * Get video streaming links for an episode/movie
 */
export const useVideoSources = (source: string, url: string, lang?: string) => {
  return useQuery("/sources/{source}/videos", {
    params: {
      path: { source },
      query: { url, ...(lang && { lang }) },
    },
  });
};

/**
 * Extract streamable trailer URL (mutation)
 * TODO: Fix useMutate parameters
 */
// export const useTrailerExtraction = () => {
//   return useMutate("/sources/trailer");
// };

// =============================================
// Admin Hooks (for development/debugging)
// =============================================

/**
 * Get cache statistics
 */
export const useCacheStats = () => {
  return useQuery("/admin/cache/stats", {});
};

/**
 * Get sources status
 */
export const useSourcesStatus = () => {
  return useQuery("/admin/sources/status", {});
};

// =============================================
// Conditional Hooks (with enable/disable logic)
// =============================================

/**
 * Conditionally fetch popular content (useful for tabs/lazy loading)
 */
export const usePopularConditional = (
  source: string, 
  page: number = 1, 
  enabled: boolean = true
) => {
  const result = useQuery("/sources/{source}/popular", {
    params: {
      path: { source },
      query: { page },
    },
  });

  // Return disabled state if not enabled
  if (!enabled) {
    return {
      ...result,
      data: undefined,
      error: undefined,
      isLoading: false,
      isValidating: false,
    };
  }

  return result;
};

/**
 * Conditionally search (useful for debounced search)
 */
export const useSearchConditional = (
  source: string, 
  query: string, 
  page: number = 1, 
  enabled: boolean = true,
  lang?: string
) => {
  const result = useQuery("/sources/{source}/search", {
    params: {
      path: { source },
      query: { q: query, page, ...(lang && { lang }) },
    },
  });

  // Return disabled state if not enabled or query is too short
  if (!enabled || query.length < 2) {
    return {
      ...result,
      data: undefined,
      error: undefined,
      isLoading: false,
      isValidating: false,
    };
  }

  return result;
};

// =============================================
// Health Check Hook
// =============================================

/**
 * Health check endpoint
 */
export const useHealthCheck = () => {
  return useQuery("/health", {});
};

// =============================================
// Type Exports for Components
// =============================================

// Export response types for component usage
export type SourcesResponse = NonNullable<ReturnType<typeof useSources>['data']>;
export type PopularResponse = NonNullable<ReturnType<typeof usePopular>['data']>;
export type SearchResponse = NonNullable<ReturnType<typeof useSearch>['data']>;
export type SeriesDetailResponse = NonNullable<ReturnType<typeof useSeriesDetail>['data']>;
export type VideoSourcesResponse = NonNullable<ReturnType<typeof useVideoSources>['data']>;

// Export individual item types
export type SearchResult = PopularResponse extends { list: (infer T)[] } ? T : never;
export type VideoSource = VideoSourcesResponse extends { videos: (infer T)[] } ? T : never;
export type SeriesDetail = SeriesDetailResponse extends { series: infer T } ? T : never;
