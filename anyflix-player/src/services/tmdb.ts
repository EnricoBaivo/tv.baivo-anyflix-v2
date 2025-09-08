import axios from 'axios';
import { MovieResponse } from '@/types/movie';

// TMDB API configuration
const BASE_URL = 'https://api.themoviedb.org/3';
const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p';

// For demo purposes, using a public API key. In production, this should be in environment variables
const API_KEY = '8265bd1679663a7ea12ac168da84d2e8'; // Public demo key

const tmdbApi = axios.create({
  baseURL: BASE_URL,
  params: {
    api_key: API_KEY,
  },
});

export const getImageUrl = (path: string, size: string = 'w500') => {
  if (!path) return '/placeholder.svg';
  return `${IMAGE_BASE_URL}/${size}${path}`;
};

export const getTrendingMovies = async (): Promise<MovieResponse> => {
  const response = await tmdbApi.get('/trending/movie/week');
  return response.data;
};

export const getPopularMovies = async (): Promise<MovieResponse> => {
  const response = await tmdbApi.get('/movie/popular');
  return response.data;
};

export const getTopRatedMovies = async (): Promise<MovieResponse> => {
  const response = await tmdbApi.get('/movie/top_rated');
  return response.data;
};

export const getMoviesByGenre = async (genreId: number): Promise<MovieResponse> => {
  const response = await tmdbApi.get('/discover/movie', {
    params: {
      with_genres: genreId,
    },
  });
  return response.data;
};

export const searchMovies = async (query: string): Promise<MovieResponse> => {
  const response = await tmdbApi.get('/search/movie', {
    params: {
      query,
    },
  });
  return response.data;
};