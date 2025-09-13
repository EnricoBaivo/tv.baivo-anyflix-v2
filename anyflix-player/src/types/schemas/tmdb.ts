/**
 * TMDB (The Movie Database) Zod schemas
 * Complete TMDB API data models with runtime validation
 */

import { z } from 'zod';

// =============================================
// TMDB Core Models
// =============================================

export const TMDBGenreSchema = z.object({
  id: z.number(),
  name: z.string()
});
export type TMDBGenre = z.infer<typeof TMDBGenreSchema>;

export const TMDBProductionCompanySchema = z.object({
  id: z.number(),
  logo_path: z.string().optional(),
  name: z.string(),
  origin_country: z.string()
});
export type TMDBProductionCompany = z.infer<typeof TMDBProductionCompanySchema>;

export const TMDBProductionCountrySchema = z.object({
  iso_3166_1: z.string(),
  name: z.string()
});
export type TMDBProductionCountry = z.infer<typeof TMDBProductionCountrySchema>;

export const TMDBSpokenLanguageSchema = z.object({
  english_name: z.string(),
  iso_639_1: z.string(),
  name: z.string()
});
export type TMDBSpokenLanguage = z.infer<typeof TMDBSpokenLanguageSchema>;

export const TMDBVideoSchema = z.object({
  iso_639_1: z.string(),
  iso_3166_1: z.string(),
  name: z.string(),
  key: z.string(),
  site: z.string(),
  size: z.number(),
  type: z.string(),
  official: z.boolean(),
  published_at: z.string(),
  id: z.string()
});
export type TMDBVideo = z.infer<typeof TMDBVideoSchema>;

export const TMDBImageSchema = z.object({
  aspect_ratio: z.number(),
  height: z.number(),
  iso_639_1: z.string().optional(),
  file_path: z.string(),
  vote_average: z.number(),
  vote_count: z.number(),
  width: z.number()
});
export type TMDBImage = z.infer<typeof TMDBImageSchema>;

export const TMDBImagesSchema = z.object({
  backdrops: z.array(TMDBImageSchema).default([]),
  logos: z.array(TMDBImageSchema).default([]),
  posters: z.array(TMDBImageSchema).default([])
});
export type TMDBImages = z.infer<typeof TMDBImagesSchema>;

export const TMDBExternalIdsSchema = z.object({
  imdb_id: z.string().optional(),
  freebase_mid: z.string().optional(),
  freebase_id: z.string().optional(),
  tvdb_id: z.number().optional(),
  tvrage_id: z.number().optional(),
  wikidata_id: z.string().optional(),
  facebook_id: z.string().optional(),
  instagram_id: z.string().optional(),
  twitter_id: z.string().optional()
});
export type TMDBExternalIds = z.infer<typeof TMDBExternalIdsSchema>;

// =============================================
// TMDB TV-specific Models
// =============================================

export const TMDBCreatedBySchema = z.object({
  id: z.number(),
  credit_id: z.string(),
  name: z.string(),
  gender: z.number(),
  profile_path: z.string().optional()
});
export type TMDBCreatedBy = z.infer<typeof TMDBCreatedBySchema>;

export const TMDBNetworkSchema = z.object({
  id: z.number(),
  logo_path: z.string().optional(),
  name: z.string(),
  origin_country: z.string()
});
export type TMDBNetwork = z.infer<typeof TMDBNetworkSchema>;

export const TMDBSeasonSchema = z.object({
  air_date: z.string().optional(),
  episode_count: z.number(),
  id: z.number(),
  name: z.string(),
  overview: z.string(),
  poster_path: z.string().optional(),
  season_number: z.number(),
  vote_average: z.number()
});
export type TMDBSeason = z.infer<typeof TMDBSeasonSchema>;

export const TMDBEpisodeSchema = z.object({
  id: z.number(),
  name: z.string(),
  overview: z.string(),
  vote_average: z.number(),
  vote_count: z.number(),
  air_date: z.string().optional(),
  episode_number: z.number(),
  episode_type: z.string(),
  production_code: z.string(),
  runtime: z.number().optional(),
  season_number: z.number(),
  show_id: z.number(),
  still_path: z.string().optional()
});
export type TMDBEpisode = z.infer<typeof TMDBEpisodeSchema>;

// =============================================
// TMDB Detail Models
// =============================================

export const TMDBMovieDetailSchema = z.object({
  adult: z.boolean(),
  backdrop_path: z.string().optional(),
  belongs_to_collection: z.record(z.any()).optional(),
  budget: z.number(),
  genres: z.array(TMDBGenreSchema).default([]),
  homepage: z.string().optional(),
  id: z.number(),
  imdb_id: z.string().optional(),
  original_language: z.string(),
  original_title: z.string(),
  overview: z.string().optional(),
  popularity: z.number(),
  poster_path: z.string().optional(),
  production_companies: z.array(TMDBProductionCompanySchema).default([]),
  production_countries: z.array(TMDBProductionCountrySchema).default([]),
  release_date: z.string().optional(),
  revenue: z.number(),
  runtime: z.number().optional(),
  spoken_languages: z.array(TMDBSpokenLanguageSchema).default([]),
  status: z.string(),
  tagline: z.string().optional(),
  title: z.string(),
  video: z.boolean(),
  vote_average: z.number(),
  vote_count: z.number(),
  // Additional fields when requested
  videos: z.record(z.array(TMDBVideoSchema)).optional(),
  images: TMDBImagesSchema.optional(),
  external_ids: TMDBExternalIdsSchema.optional()
});
export type TMDBMovieDetail = z.infer<typeof TMDBMovieDetailSchema>;

export const TMDBTVDetailSchema = z.object({
  adult: z.boolean(),
  backdrop_path: z.string().optional(),
  created_by: z.array(TMDBCreatedBySchema).default([]),
  episode_run_time: z.array(z.number()).default([]),
  first_air_date: z.string().optional(),
  genres: z.array(TMDBGenreSchema).default([]),
  homepage: z.string(),
  id: z.number(),
  in_production: z.boolean(),
  languages: z.array(z.string()).default([]),
  last_air_date: z.string().optional(),
  last_episode_to_air: TMDBEpisodeSchema.optional(),
  name: z.string(),
  networks: z.array(TMDBNetworkSchema).default([]),
  next_episode_to_air: TMDBEpisodeSchema.optional(),
  number_of_episodes: z.number(),
  number_of_seasons: z.number(),
  origin_country: z.array(z.string()).default([]),
  original_language: z.string(),
  original_name: z.string(),
  overview: z.string(),
  popularity: z.number(),
  poster_path: z.string().optional(),
  production_companies: z.array(TMDBProductionCompanySchema).default([]),
  production_countries: z.array(TMDBProductionCountrySchema).default([]),
  seasons: z.array(TMDBSeasonSchema).default([]),
  spoken_languages: z.array(TMDBSpokenLanguageSchema).default([]),
  status: z.string(),
  tagline: z.string(),
  type: z.string(),
  vote_average: z.number(),
  vote_count: z.number(),
  // Additional fields when requested
  videos: z.record(z.array(TMDBVideoSchema)).optional(),
  images: TMDBImagesSchema.optional(),
  external_ids: TMDBExternalIdsSchema.optional()
});
export type TMDBTVDetail = z.infer<typeof TMDBTVDetailSchema>;

// =============================================
// TMDB Search Models
// =============================================

export const TMDBSearchResultSchema = z.object({
  id: z.number(),
  media_type: z.string(),
  adult: z.boolean().optional(),
  backdrop_path: z.string().optional(),
  poster_path: z.string().optional(),
  popularity: z.number().default(0),
  vote_average: z.number().optional(),
  vote_count: z.number().optional(),
  overview: z.string().optional(),
  genre_ids: z.array(z.number()).default([]),
  original_language: z.string().optional(),
  // Movie specific fields
  title: z.string().optional(),
  original_title: z.string().optional(),
  release_date: z.string().optional(),
  video: z.boolean().optional(),
  // TV specific fields
  name: z.string().optional(),
  original_name: z.string().optional(),
  first_air_date: z.string().optional(),
  origin_country: z.array(z.string()).default([]),
  // Person specific fields
  profile_path: z.string().optional(),
  known_for: z.array(z.record(z.any())).default([]),
  known_for_department: z.string().optional(),
  gender: z.number().optional()
});
export type TMDBSearchResult = z.infer<typeof TMDBSearchResultSchema>;

export const TMDBSearchResponseSchema = z.object({
  page: z.number(),
  results: z.array(TMDBSearchResultSchema).default([]),
  total_pages: z.number(),
  total_results: z.number()
});
export type TMDBSearchResponse = z.infer<typeof TMDBSearchResponseSchema>;

// =============================================
// TMDB Configuration
// =============================================

export const TMDBConfigurationSchema = z.object({
  images: z.record(z.any()),
  change_keys: z.array(z.string()).default([])
});
export type TMDBConfiguration = z.infer<typeof TMDBConfigurationSchema>;
