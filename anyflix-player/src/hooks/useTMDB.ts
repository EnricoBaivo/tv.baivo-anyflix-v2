/**
 * React hooks for TMDB integration using SWR
 */

import React from 'react';
import useSWR, { SWRConfiguration } from 'swr';
import { MediaResponse } from '@/types/media';
import {
  tmdbFetcher,
  getTrendingMoviesUrl,
  getPopularMoviesUrl,
  getTopRatedMoviesUrl,
  getMoviesByGenreUrl,
  getSearchMoviesUrl,
} from '@/services/tmdb';

// ========== TYPED FETCHER ==========

/**
 * Create a typed fetcher for TMDB responses
 */
const createTMDBFetcher = () => {
  return (url: string): Promise<MediaResponse> => tmdbFetcher(url);
};

// ========== DEFAULT SWR CONFIGURATION ==========

const defaultSWRConfig: SWRConfiguration = {
  revalidateOnFocus: false,
  revalidateOnReconnect: true,
  refreshInterval: 0, // Disable auto-refresh by default
  dedupingInterval: 5000, // 5 seconds deduping
  errorRetryCount: 3,
  errorRetryInterval: 1000,
  // Cache for 5 minutes since movie data doesn't change often
  refreshWhenHidden: false,
  refreshWhenOffline: false,
};

// ========== TMDB HOOKS ==========

/**
 * Hook to get trending movies
 */
export const useTrendingMovies = (config?: SWRConfiguration) => {
  return useSWR<MediaResponse>(
    getTrendingMoviesUrl(),
    createTMDBFetcher(),
    { 
      ...defaultSWRConfig,
      refreshInterval: 300000, // Refresh every 5 minutes for trending
      ...config 
    }
  );
};

/**
 * Hook to get popular movies
 */
export const usePopularMovies = (config?: SWRConfiguration) => {
  return useSWR<MediaResponse>(
    getPopularMoviesUrl(),
    createTMDBFetcher(),
    { 
      ...defaultSWRConfig,
      refreshInterval: 600000, // Refresh every 10 minutes for popular
      ...config 
    }
  );
};

/**
 * Hook to get top rated movies
 */
export const useTopRatedMovies = (config?: SWRConfiguration) => {
  return useSWR<MediaResponse>(
    getTopRatedMoviesUrl(),
    createTMDBFetcher(),
    { 
      ...defaultSWRConfig,
      refreshInterval: 3600000, // Refresh every hour for top rated
      ...config 
    }
  );
};

/**
 * Hook to get movies by genre
 */
export const useMoviesByGenre = (genreId: number, config?: SWRConfiguration) => {
  return useSWR<MediaResponse>(
    genreId ? getMoviesByGenreUrl(genreId) : null,
    createTMDBFetcher(),
    { 
      ...defaultSWRConfig,
      refreshInterval: 600000, // Refresh every 10 minutes
      ...config 
    }
  );
};

/**
 * Hook to search movies
 */
export const useSearchMovies = (query: string, config?: SWRConfiguration) => {
  const shouldFetch = query && query.trim().length > 0;
  
  return useSWR<MediaResponse>(
    shouldFetch ? getSearchMoviesUrl(query) : null,
    createTMDBFetcher(),
    { 
      ...defaultSWRConfig,
      dedupingInterval: 2000, // Shorter deduping for search
      refreshInterval: 0, // Never auto-refresh search results
      revalidateOnFocus: false,
      ...config 
    }
  );
};

// ========== COMPOSITE HOOKS ==========

/**
 * Hook that fetches multiple movie categories at once
 */
export const useMovieOverview = (config?: SWRConfiguration) => {
  const { data: trending, error: trendingError, isLoading: trendingLoading } = useTrendingMovies(config);
  const { data: popular, error: popularError, isLoading: popularLoading } = usePopularMovies(config);
  const { data: topRated, error: topRatedError, isLoading: topRatedLoading } = useTopRatedMovies(config);

  return {
    trending,
    popular,
    topRated,
    errors: {
      trending: trendingError,
      popular: popularError,
      topRated: topRatedError,
    },
    loading: {
      trending: trendingLoading,
      popular: popularLoading,
      topRated: topRatedLoading,
    },
    isLoading: trendingLoading || popularLoading || topRatedLoading,
    hasError: !!(trendingError || popularError || topRatedError),
  };
};

/**
 * Hook for getting movies by multiple genres
 */
export const useMoviesByGenres = (genreIds: number[], config?: SWRConfiguration) => {
  const requests = genreIds.map(genreId => ({
    genreId,
    // eslint-disable-next-line react-hooks/rules-of-hooks
    result: useSWR<MediaResponse>(
      getMoviesByGenreUrl(genreId),
      createTMDBFetcher(),
      { ...defaultSWRConfig, ...config }
    ),
  }));

  return {
    data: requests.reduce((acc, { genreId, result }) => {
      if (result.data) {
        acc[genreId] = result.data;
      }
      return acc;
    }, {} as Record<number, MediaResponse>),
    errors: requests.reduce((acc, { genreId, result }) => {
      if (result.error) {
        acc[genreId] = result.error;
      }
      return acc;
    }, {} as Record<number, Error>),
    loading: requests.some(({ result }) => result.isLoading),
    hasError: requests.some(({ result }) => result.error),
  };
};

// ========== UTILITY HOOKS ==========

/**
 * Hook for preloading movie data
 */
export const usePreloadMovies = () => {
  // Preload popular data that's likely to be needed
  useTrendingMovies({ revalidateOnMount: false });
  usePopularMovies({ revalidateOnMount: false });
  
  return {
    preloaded: true,
  };
};

/**
 * Hook for managing search state with debouncing
 */
export const useDebouncedMovieSearch = (query: string, delay = 500, config?: SWRConfiguration) => {
  const [debouncedQuery, setDebouncedQuery] = React.useState(query);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, delay);

    return () => clearTimeout(timer);
  }, [query, delay]);

  return useSearchMovies(debouncedQuery, config);
};

// ========== HOME PAGE SPECIFIC HOOK ==========

/**
 * Hook specifically for the Home page that fetches all needed data
 */
export const useHomePageData = (config?: SWRConfiguration) => {
  const trending = useTrendingMovies(config);
  const popular = usePopularMovies(config);
  const topRated = useTopRatedMovies(config);
  const action = useMoviesByGenre(28, config); // Action genre ID is 28

  return {
    trending,
    popular,
    topRated,
    action,
    isLoading: trending.isLoading || popular.isLoading || topRated.isLoading || action.isLoading,
    isError: trending.error || popular.error || topRated.error || action.error,
  };
};