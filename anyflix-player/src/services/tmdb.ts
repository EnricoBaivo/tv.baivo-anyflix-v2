import { MediaResponse } from '@/types/media';

// TMDB API configuration
const BASE_URL = 'https://api.themoviedb.org/3';
const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p';

// For demo purposes, using a public API key. In production, this should be in environment variables
const API_KEY = '8265bd1679663a7ea12ac168da84d2e8'; // Public demo key

/**
 * SWR fetcher function for TMDB API endpoints
 */
export const tmdbFetcher = async (url: string): Promise<MediaResponse> => {
  const fullUrl = url.startsWith('http') ? url : `${BASE_URL}${url}`;
  const urlWithKey = new URL(fullUrl);
  urlWithKey.searchParams.set('api_key', API_KEY);
  
  console.log(`[TMDBFetcher] GET ${urlWithKey.toString()}`);
  
  try {
    const response = await fetch(urlWithKey.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(30000), // 30 seconds timeout
    });

    if (!response.ok) {
      throw new Error(`TMDB API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('TMDB API request timeout');
      }
      throw new Error(`TMDB API error: ${error.message}`);
    }
    throw new Error('Unknown TMDB API error');
  }
};

/**
 * Get image URL for TMDB images
 */
export const getImageUrl = (path: string, size: string = 'w500') => {
  if (!path) return '/placeholder.svg';
  return `${IMAGE_BASE_URL}/${size}${path}`;
};

// ========== SWR KEY GENERATORS ==========

/**
 * Generate SWR keys for TMDB endpoints
 */
export const tmdbKeys = {
  trending: () => '/trending/movie/week',
  popular: () => '/movie/popular',
  topRated: () => '/movie/top_rated',
  moviesByGenre: (genreId: number) => `/discover/movie?with_genres=${genreId}`,
  search: (query: string) => `/search/movie?query=${encodeURIComponent(query)}`,
} as const;

// ========== URL GENERATORS ==========

/**
 * URL generator functions for use with SWR
 */
export const getTrendingMoviesUrl = () => tmdbKeys.trending();
export const getPopularMoviesUrl = () => tmdbKeys.popular();
export const getTopRatedMoviesUrl = () => tmdbKeys.topRated();
export const getMoviesByGenreUrl = (genreId: number) => tmdbKeys.moviesByGenre(genreId);
export const getSearchMoviesUrl = (query: string) => tmdbKeys.search(query);

// ========== LEGACY FUNCTIONS (DEPRECATED) ==========

/**
 * @deprecated Use useTrendingMovies hook instead
 */
export const getTrendingMovies = async (): Promise<MediaResponse> => {
  console.warn('[TMDB] getTrendingMovies() is deprecated. Use useTrendingMovies() hook instead.');
  return tmdbFetcher(getTrendingMoviesUrl());
};

/**
 * @deprecated Use usePopularMovies hook instead
 */
export const getPopularMovies = async (): Promise<MediaResponse> => {
  console.warn('[TMDB] getPopularMovies() is deprecated. Use usePopularMovies() hook instead.');
  return tmdbFetcher(getPopularMoviesUrl());
};

/**
 * @deprecated Use useTopRatedMovies hook instead
 */
export const getTopRatedMovies = async (): Promise<MediaResponse> => {
  console.warn('[TMDB] getTopRatedMovies() is deprecated. Use useTopRatedMovies() hook instead.');
  return tmdbFetcher(getTopRatedMoviesUrl());
};

/**
 * @deprecated Use useMoviesByGenre hook instead
 */
export const getMoviesByGenre = async (genreId: number): Promise<MediaResponse> => {
  console.warn('[TMDB] getMoviesByGenre() is deprecated. Use useMoviesByGenre() hook instead.');
  return tmdbFetcher(getMoviesByGenreUrl(genreId));
};

/**
 * @deprecated Use useSearchMovies hook instead
 */
export const searchMovies = async (query: string): Promise<MediaResponse> => {
  console.warn('[TMDB] searchMovies() is deprecated. Use useSearchMovies() hook instead.');
  return tmdbFetcher(getSearchMoviesUrl(query));
};