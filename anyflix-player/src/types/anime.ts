/**
 * TypeScript types for Anime Backend API
 * Matches the Pydantic models from the FastAPI backend
 */

// Base interfaces
export interface AnimeListItem {
  name: string;
  image_url: string;
  link: string;
}

export interface BaseResponse {
  has_next_page: boolean;
}

// Source management
export interface SourcesResponse {
  sources: string[];
}

export interface ListPreference {
  title: string;
  entries: string[];
  entryValues: string[];
}

export interface MultiSelectListPreference {
  title: string;
  entries: string[];
  entryValues: string[];
}

export interface Preference {
  key: string;
  list_preference?: ListPreference;
  multi_select_list_preference?: MultiSelectListPreference;
}

export interface PreferencesResponse {
  preferences: Preference[];
}

// Content discovery responses
export interface PopularResponse extends BaseResponse {
  list: AnimeListItem[];
}

export interface LatestResponse extends BaseResponse {
  list: AnimeListItem[];
}

export interface SearchResponse extends BaseResponse {
  list: AnimeListItem[];
}

// Legacy flat structure (deprecated)
export interface LegacyEpisode {
  name: string;
  url: string;
  date_upload: string | null;
}

export interface LegacyAnimeDetail {
  name: string;
  image_url: string;
  description: string;
  author: string;
  status: number;
  genre: string[];
  episodes: LegacyEpisode[];
}

export interface DetailResponse {
  anime: LegacyAnimeDetail;
}

// Modern hierarchical structure
export interface Episode {
  season: number;
  episode: number;
  title: string;
  url: string;
  date_upload: string | null;
  tags: string[];
}

export interface Season {
  season: number;
  title: string | null;
  episodes: Episode[];
}

export type MovieKind = 'movie' | 'ova' | 'special';

export interface Movie {
  number: number;
  title: string;
  kind: MovieKind;
  url: string;
  date_upload: string | null;
  tags: string[];
}

export interface SeriesDetail {
  slug: string;
  seasons: Season[];
  movies: Movie[];
}

export interface SeriesDetailResponse {
  series: SeriesDetail;
}

export interface SeasonsResponse {
  seasons: Season[];
}

export interface SeasonResponse {
  season: Season;
}

export interface EpisodeResponse {
  episode: Episode;
}

export interface MoviesResponse {
  movies: Movie[];
}

export interface MovieResponse {
  movie: Movie;
}

// Video sources
export interface VideoSource {
  host: string;
  url: string;
  quality?: string;
  language?: string;
  subtitles?: boolean;
}

export interface VideoListResponse {
  videos: VideoSource[];
  language?: string;
}

// API Error response
export interface APIError {
  detail: string;
  status_code?: number;
}

// Search parameters
export interface SearchParams {
  q: string;
  page?: number;
  lang?: string;
}

export interface PaginationParams {
  page?: number;
}

// Service configuration
export interface AnimeServiceConfig {
  baseURL: string;
  timeout?: number;
  retries?: number;
}

// Common anime metadata
export interface AnimeMetadata {
  name: string;
  image_url: string;
  description?: string;
  author?: string;
  status?: number;
  genre?: string[];
  link: string;
}

// Utility types for frontend state management
export interface AnimeState {
  sources: string[];
  selectedSource: string | null;
  preferences: Record<string, Preference[]>;
  loading: boolean;
  error: string | null;
}

export interface ContentState {
  popular: AnimeListItem[];
  latest: AnimeListItem[];
  searchResults: AnimeListItem[];
  currentSeries: SeriesDetail | null;
  currentVideos: VideoSource[];
  loading: boolean;
  error: string | null;
}
