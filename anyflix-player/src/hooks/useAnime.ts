/**
 * React hooks for anime backend integration using SWR
 */

import useSWR, { SWRConfiguration } from 'swr';
import useSWRMutation from 'swr/mutation';
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
  SearchParams,
  PaginationParams,
} from '@/types/anime';
import {
  animeFetcher,
  animeKeys,
  getSourcesUrl,
  getSourcePreferencesUrl,
  getPopularUrl,
  getLatestUrl,
  getSearchUrl,
  getAnimeDetailUrl,
  getSeriesDetailUrl,
  getSeriesSeasonsUrl,
  getSeriesSeasonUrl,
  getSeriesEpisodeUrl,
  getSeriesMoviesUrl,
  getSeriesMovieUrl,
  getVideoSourcesUrl,
  getHealthCheckUrl,
} from '@/services/anime';

// ========== TYPED FETCHERS ==========

/**
 * Create a typed fetcher for specific response types
 */
const createTypedFetcher = <T>() => {
  return (url: string): Promise<T> => animeFetcher(url) as Promise<T>;
};

// ========== DEFAULT SWR CONFIGURATION ==========

const defaultSWRConfig: SWRConfiguration = {
  revalidateOnFocus: false,
  revalidateOnReconnect: true,
  refreshInterval: 0, // Disable auto-refresh by default
  dedupingInterval: 5000, // 5 seconds deduping
  errorRetryCount: 3,
  errorRetryInterval: 1000,
};

// ========== SOURCE MANAGEMENT HOOKS ==========

/**
 * Hook to get all available anime sources
 */
export const useSources = (config?: SWRConfiguration) => {
  return useSWR<SourcesResponse>(
    getSourcesUrl(),
    createTypedFetcher<SourcesResponse>(),
    { ...defaultSWRConfig, ...config }
  );
};

/**
 * Hook to get preferences for a specific source
 */
export const useSourcePreferences = (source: string, config?: SWRConfiguration) => {
  return useSWR<PreferencesResponse>(
    source ? getSourcePreferencesUrl(source) : null,
    createTypedFetcher<PreferencesResponse>(),
    { ...defaultSWRConfig, ...config }
  );
};

// ========== CONTENT DISCOVERY HOOKS ==========

/**
 * Hook to get popular anime from a source
 */
export const usePopular = (
  source: string,
  params: PaginationParams = {},
  config?: SWRConfiguration
) => {
  return useSWR<PopularResponse>(
    source ? getPopularUrl(source, params) : null,
    createTypedFetcher<PopularResponse>(),
    { ...defaultSWRConfig, ...config }
  );
};

/**
 * Hook to get latest anime updates from a source
 */
export const useLatest = (
  source: string,
  params: PaginationParams = {},
  config?: SWRConfiguration
) => {
  return useSWR<LatestResponse>(
    source ? getLatestUrl(source, params) : null,
    createTypedFetcher<LatestResponse>(),
    { ...defaultSWRConfig, ...config }
  );
};

/**
 * Hook to search for anime in a source
 */
export const useSearch = (
  source: string,
  searchParams: SearchParams,
  config?: SWRConfiguration
) => {
  const shouldFetch = source && searchParams.q && searchParams.q.trim().length > 0;
  
  return useSWR<SearchResponse>(
    shouldFetch ? getSearchUrl(source, searchParams) : null,
    createTypedFetcher<SearchResponse>(),
    { 
      ...defaultSWRConfig, 
      dedupingInterval: 2000, // Shorter deduping for search
      ...config 
    }
  );
};

// ========== LEGACY HOOKS (DEPRECATED) ==========

/**
 * Hook to get anime detail with flat episode structure (DEPRECATED)
 * @deprecated Use useSeriesDetail() for hierarchical structure
 */
export const useAnimeDetail = (
  source: string,
  url: string,
  flat = false,
  config?: SWRConfiguration
) => {
  console.warn('[useAnimeDetail] This hook is deprecated. Use useSeriesDetail() instead.');
  
  return useSWR<DetailResponse>(
    source && url ? getAnimeDetailUrl(source, url, flat) : null,
    createTypedFetcher<DetailResponse>(),
    { ...defaultSWRConfig, ...config }
  );
};

// ========== HIERARCHICAL API HOOKS (MODERN) ==========

/**
 * Hook to get series detail with hierarchical structure (seasons + movies)
 */
export const useSeriesDetail = (
  source: string,
  url: string,
  config?: SWRConfiguration
) => {
  return useSWR<SeriesDetailResponse>(
    source && url ? getSeriesDetailUrl(source, url) : null,
    createTypedFetcher<SeriesDetailResponse>(),
    { ...defaultSWRConfig, ...config }
  );
};

/**
 * Hook to get all seasons for a series
 */
export const useSeriesSeasons = (
  source: string,
  url: string,
  config?: SWRConfiguration
) => {
  return useSWR<SeasonsResponse>(
    source && url ? getSeriesSeasonsUrl(source, url) : null,
    createTypedFetcher<SeasonsResponse>(),
    { ...defaultSWRConfig, ...config }
  );
};

/**
 * Hook to get specific season details
 */
export const useSeriesSeason = (
  source: string,
  seasonNum: number,
  url: string,
  config?: SWRConfiguration
) => {
  return useSWR<SeasonResponse>(
    source && seasonNum && url ? getSeriesSeasonUrl(source, seasonNum, url) : null,
    createTypedFetcher<SeasonResponse>(),
    { ...defaultSWRConfig, ...config }
  );
};

/**
 * Hook to get specific episode details
 */
export const useSeriesEpisode = (
  source: string,
  seasonNum: number,
  episodeNum: number,
  url: string,
  config?: SWRConfiguration
) => {
  return useSWR<EpisodeResponse>(
    source && seasonNum && episodeNum && url 
      ? getSeriesEpisodeUrl(source, seasonNum, episodeNum, url) 
      : null,
    createTypedFetcher<EpisodeResponse>(),
    { ...defaultSWRConfig, ...config }
  );
};

/**
 * Hook to get all movies/OVAs for a series
 */
export const useSeriesMovies = (
  source: string,
  url: string,
  config?: SWRConfiguration
) => {
  return useSWR<MoviesResponse>(
    source && url ? getSeriesMoviesUrl(source, url) : null,
    createTypedFetcher<MoviesResponse>(),
    { ...defaultSWRConfig, ...config }
  );
};

/**
 * Hook to get specific movie/OVA details
 */
export const useSeriesMovie = (
  source: string,
  movieNum: number,
  url: string,
  config?: SWRConfiguration
) => {
  return useSWR<MovieResponse>(
    source && movieNum && url ? getSeriesMovieUrl(source, movieNum, url) : null,
    createTypedFetcher<MovieResponse>(),
    { ...defaultSWRConfig, ...config }
  );
};

// ========== VIDEO SOURCES HOOKS ==========

/**
 * Hook to get video sources for an episode
 */
export const useVideoSources = (
  source: string,
  url: string,
  lang?: string,
  config?: SWRConfiguration
) => {
  return useSWR<VideoListResponse>(
    source && url ? getVideoSourcesUrl(source, url, lang) : null,
    createTypedFetcher<VideoListResponse>(),
    { 
      ...defaultSWRConfig,
      refreshInterval: 0, // Never auto-refresh video sources
      revalidateOnFocus: false,
      ...config 
    }
  );
};

// ========== UTILITY HOOKS ==========

/**
 * Hook for health check
 */
export const useHealthCheck = (config?: SWRConfiguration) => {
  return useSWR<boolean>(
    getHealthCheckUrl(),
    async () => {
      try {
        await animeFetcher(getHealthCheckUrl());
        return true;
      } catch {
        return false;
      }
    },
    { 
      ...defaultSWRConfig,
      refreshInterval: 30000, // Check every 30 seconds
      ...config 
    }
  );
};

// ========== MUTATION HOOKS ==========

/**
 * Hook for triggering manual search with mutation
 */
export const useSearchMutation = () => {
  return useSWRMutation(
    'search-mutation',
    async (key: string, { arg }: { arg: { source: string; searchParams: SearchParams } }) => {
      const { source, searchParams } = arg;
      return await animeFetcher(getSearchUrl(source, searchParams));
    }
  );
};

/**
 * Hook for manual data refresh
 */
export const useRefreshData = () => {
  return useSWRMutation(
    'refresh-data',
    async (key: string, { arg }: { arg: { url: string } }) => {
      return await animeFetcher(arg.url);
    }
  );
};

// ========== COMPOSITE HOOKS ==========

/**
 * Composite hook that combines multiple anime data sources
 */
export const useAnimeOverview = (source: string, config?: SWRConfiguration) => {
  const { data: sources, error: sourcesError, isLoading: sourcesLoading } = useSources(config);
  const { data: popular, error: popularError, isLoading: popularLoading } = usePopular(source, {}, config);
  const { data: latest, error: latestError, isLoading: latestLoading } = useLatest(source, {}, config);
  const { data: preferences, error: preferencesError, isLoading: preferencesLoading } = useSourcePreferences(source, config);

  return {
    sources,
    popular,
    latest,
    preferences,
    errors: {
      sources: sourcesError,
      popular: popularError,
      latest: latestError,
      preferences: preferencesError,
    },
    loading: {
      sources: sourcesLoading,
      popular: popularLoading,
      latest: latestLoading,
      preferences: preferencesLoading,
    },
    isLoading: sourcesLoading || popularLoading || latestLoading || preferencesLoading,
    hasError: !!(sourcesError || popularError || latestError || preferencesError),
  };
};

/**
 * Hook for managing anime series with all related data
 */
export const useAnimeSeries = (source: string, url: string, config?: SWRConfiguration) => {
  const { data: series, error: seriesError, isLoading: seriesLoading } = useSeriesDetail(source, url, config);
  const { data: seasons, error: seasonsError, isLoading: seasonsLoading } = useSeriesSeasons(source, url, config);
  const { data: movies, error: moviesError, isLoading: moviesLoading } = useSeriesMovies(source, url, config);

  return {
    series,
    seasons,
    movies,
    errors: {
      series: seriesError,
      seasons: seasonsError,
      movies: moviesError,
    },
    loading: {
      series: seriesLoading,
      seasons: seasonsLoading,
      movies: moviesLoading,
    },
    isLoading: seriesLoading || seasonsLoading || moviesLoading,
    hasError: !!(seriesError || seasonsError || moviesError),
  };
};
