import useSWR from 'swr';
import { MediaResponse } from '@/types/media';
import {
  getTrendingMovies,
  getPopularMovies,
  getTopRatedMovies,
  getMoviesByGenre,
  searchMovies,
} from '@/services/tmdb';

// SWR fetcher functions
const fetchers = {
  trending: () => getTrendingMovies(),
  popular: () => getPopularMovies(),
  topRated: () => getTopRatedMovies(),
  genre: (genreId: number) => getMoviesByGenre(genreId),
  search: (query: string) => searchMovies(query),
};

// Custom hooks for each endpoint
export const useTrendingMovies = () => {
  return useSWR<MediaResponse>('movies/trending', fetchers.trending, {
    revalidateOnFocus: false,
    dedupingInterval: 5 * 60 * 1000, // 5 minutes
  });
};

export const usePopularMovies = () => {
  return useSWR<MediaResponse>('movies/popular', fetchers.popular, {
    revalidateOnFocus: false,
    dedupingInterval: 5 * 60 * 1000, // 5 minutes
  });
};

export const useTopRatedMovies = () => {
  return useSWR<MediaResponse>('movies/top-rated', fetchers.topRated, {
    revalidateOnFocus: false,
    dedupingInterval: 5 * 60 * 1000, // 5 minutes
  });
};

export const useMoviesByGenre = (genreId: number) => {
  return useSWR<MediaResponse>(
    genreId ? `movies/genre/${genreId}` : null,
    () => fetchers.genre(genreId),
    {
      revalidateOnFocus: false,
      dedupingInterval: 5 * 60 * 1000, // 5 minutes
    }
  );
};

export const useSearchMovies = (query: string) => {
  return useSWR<MediaResponse>(
    query && query.trim() ? `movies/search/${query}` : null,
    () => fetchers.search(query),
    {
      revalidateOnFocus: false,
      dedupingInterval: 30 * 1000, // 30 seconds for search results
      errorRetryCount: 3,
    }
  );
};

// Combined hook for home page data
export const useHomePageData = () => {
  const trending = useTrendingMovies();
  const popular = usePopularMovies();
  const topRated = useTopRatedMovies();
  const action = useMoviesByGenre(28); // Action genre ID

  return {
    trending,
    popular,
    topRated,
    action,
    isLoading: trending.isLoading || popular.isLoading || topRated.isLoading || action.isLoading,
    isError: trending.error || popular.error || topRated.error || action.error,
    mutate: () => {
      trending.mutate();
      popular.mutate();
      topRated.mutate();
      action.mutate();
    },
  };
};
