/**
 * Anime Backend Service
 * Connects to FastAPI backend for anime streaming sources using SWR
 */

import {
  SourcesResponse,
  PreferencesResponse,
  PopularResponse,
  LatestResponse,
  SearchResponse,
  DetailResponse,
  SeriesDetailResponse,
  SeasonsResponse,
  SeasonResponse,
  EpisodeResponse,
  MoviesResponse,
  MovieResponse,
  VideoListResponse,
  APIError,
  SearchParams,
  PaginationParams,
  AnimeServiceConfig,
} from '@/types/anime';

/**
 * Default configuration for the anime service
 */
const DEFAULT_CONFIG: AnimeServiceConfig = {
  baseURL: 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  retries: 3,
};

/**
 * Custom error class for anime service errors
 */
export class AnimeServiceError extends Error {
  public statusCode?: number;
  public originalError?: Error;

  constructor(message: string, statusCode?: number, originalError?: Error) {
    super(message);
    this.name = 'AnimeServiceError';
    this.statusCode = statusCode;
    this.originalError = originalError;
  }
}

/**
 * Global configuration for the anime service
 */
let config: AnimeServiceConfig = { ...DEFAULT_CONFIG };

/**
 * Update the global anime service configuration
 */
export const updateAnimeServiceConfig = (newConfig: Partial<AnimeServiceConfig>): void => {
  config = { ...config, ...newConfig };
};

/**
 * Get the current anime service configuration
 */
export const getAnimeServiceConfig = (): AnimeServiceConfig => config;

/**
 * SWR fetcher function for anime API endpoints
 */
export const animeFetcher = async (url: string): Promise<unknown> => {
  const fullUrl = url.startsWith('http') ? url : `${config.baseURL}${url}`;
  
  console.log(`[AnimeFetcher] GET ${fullUrl}`);
  
  try {
    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(config.timeout || 30000),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({})) as APIError;
      const message = errorData?.detail || `HTTP ${response.status}: ${response.statusText}`;
      throw new AnimeServiceError(message, response.status);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof AnimeServiceError) {
      throw error;
    }
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new AnimeServiceError('Request timeout', 408, error);
      }
      throw new AnimeServiceError(
        error.message || 'Network error: Unable to connect to anime backend',
        0,
        error
      );
    }
    
    throw new AnimeServiceError('Unknown error occurred', undefined, error as Error);
  }
};

/**
 * Build URL with query parameters
 */
const buildUrl = (path: string, params?: Record<string, unknown>): string => {
  const url = new URL(path, config.baseURL);
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  
  return url.toString();
};

// ========== SWR KEY GENERATORS ==========

/**
 * Generate SWR keys for consistent caching
 */
export const animeKeys = {
  // Source management
  sources: () => '/sources',
  sourcePreferences: (source: string) => `/sources/${source}/preferences`,
  
  // Content discovery
  popular: (source: string, page = 1) => `/sources/${source}/popular?page=${page}`,
  latest: (source: string, page = 1) => `/sources/${source}/latest?page=${page}`,
  search: (source: string, query: string, page = 1, lang?: string) => 
    `/sources/${source}/search?q=${encodeURIComponent(query)}&page=${page}${lang ? `&lang=${lang}` : ''}`,
  
  // Legacy endpoints (deprecated)
  animeDetail: (source: string, url: string, flat = false) => 
    `/sources/${source}/detail?url=${encodeURIComponent(url)}&flat=${flat}`,
  
  // Hierarchical API (modern)
  seriesDetail: (source: string, url: string) => 
    `/sources/${source}/series?url=${encodeURIComponent(url)}`,
  seriesSeasons: (source: string, url: string) => 
    `/sources/${source}/series/seasons?url=${encodeURIComponent(url)}`,
  seriesSeason: (source: string, seasonNum: number, url: string) => 
    `/sources/${source}/series/seasons/${seasonNum}?url=${encodeURIComponent(url)}`,
  seriesEpisode: (source: string, seasonNum: number, episodeNum: number, url: string) => 
    `/sources/${source}/series/seasons/${seasonNum}/episodes/${episodeNum}?url=${encodeURIComponent(url)}`,
  seriesMovies: (source: string, url: string) => 
    `/sources/${source}/series/movies?url=${encodeURIComponent(url)}`,
  seriesMovie: (source: string, movieNum: number, url: string) => 
    `/sources/${source}/series/movies/${movieNum}?url=${encodeURIComponent(url)}`,
  
  // Video sources
  videoSources: (source: string, url: string, lang?: string) => 
    `/sources/${source}/videos?url=${encodeURIComponent(url)}${lang ? `&lang=${lang}` : ''}`,
  
  // Health check
  health: () => '/health',
} as const;

// ========== DIRECT API FUNCTIONS ==========

/**
 * Direct API functions for use with SWR or manual calls
 * These functions return the full URL and can be used as SWR keys
 */

// Source management
export const getSourcesUrl = () => animeKeys.sources();
export const getSourcePreferencesUrl = (source: string) => animeKeys.sourcePreferences(source);

// Content discovery
export const getPopularUrl = (source: string, params: PaginationParams = {}) => 
  animeKeys.popular(source, params.page);

export const getLatestUrl = (source: string, params: PaginationParams = {}) => 
  animeKeys.latest(source, params.page);

export const getSearchUrl = (source: string, searchParams: SearchParams) => 
  animeKeys.search(source, searchParams.q, searchParams.page, searchParams.lang);

// Legacy endpoints (deprecated)
export const getAnimeDetailUrl = (source: string, url: string, flat = false) => {
  console.warn('[AnimeService] getAnimeDetailUrl() is deprecated. Use getSeriesDetailUrl() instead.');
  return animeKeys.animeDetail(source, url, flat);
};

// Hierarchical API (modern)
export const getSeriesDetailUrl = (source: string, url: string) => 
  animeKeys.seriesDetail(source, url);

export const getSeriesSeasonsUrl = (source: string, url: string) => 
  animeKeys.seriesSeasons(source, url);

export const getSeriesSeasonUrl = (source: string, seasonNum: number, url: string) => 
  animeKeys.seriesSeason(source, seasonNum, url);

export const getSeriesEpisodeUrl = (source: string, seasonNum: number, episodeNum: number, url: string) => 
  animeKeys.seriesEpisode(source, seasonNum, episodeNum, url);

export const getSeriesMoviesUrl = (source: string, url: string) => 
  animeKeys.seriesMovies(source, url);

export const getSeriesMovieUrl = (source: string, movieNum: number, url: string) => 
  animeKeys.seriesMovie(source, movieNum, url);

// Video sources
export const getVideoSourcesUrl = (source: string, url: string, lang?: string) => 
  animeKeys.videoSources(source, url, lang);

// Health check
export const getHealthCheckUrl = () => animeKeys.health();

// ========== UTILITY FUNCTIONS ==========

/**
 * Test connection to the backend
 */
export const healthCheck = async (): Promise<boolean> => {
  try {
    await animeFetcher(getHealthCheckUrl());
    return true;
  } catch (error) {
    console.error('[AnimeService] Health check failed:', error);
    return false;
  }
};

/**
 * Get the current backend base URL
 */
export const getBaseURL = (): string => config.baseURL;
