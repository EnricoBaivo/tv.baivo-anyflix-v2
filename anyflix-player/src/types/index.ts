/**
 * Main types export file for Anyflix Frontend
 * Exports all types from backend API models and responses
 * Now with Zod schemas for runtime validation!
 */

// Export all Zod schemas and inferred types from split files
export * from './schemas/base';
export * from './schemas/anilist';
export * from './schemas/tmdb';
export * from './zod-responses';

// Legacy backend API types have been removed - use Zod schemas instead

// Export existing media types (keeping for backward compatibility)
// Note: Some types may conflict with backend-api types, use explicit imports when needed
export type {
  Media as TMDBMedia,
  MediaResponse as TMDBMediaResponse,
  Genre as TMDBGenreOld
} from './media';

export type {
  Media as MovieMedia
} from './movie';

// =============================================
// Re-export commonly used Zod schemas and types
// =============================================

// Core data schemas and types
export {
  SearchResultSchema,
  VideoSourceSchema,
  EpisodeSchema,
  SeasonSchema,
  MovieSchema,
  SeriesDetailSchema,
  MediaInfoSchema,
} from './schemas/base';

export type {
  SearchResult,
  VideoSource,
  Episode,
  Season,
  Movie,
  SeriesDetail,
  MediaInfo,
} from './schemas/base';

// Response schemas and types
export {
  PopularResponseSchema,
  LatestResponseSchema,
  SearchResponseSchema,
  VideoListResponseSchema,
  SeriesDetailResponseSchema,
  SeasonsResponseSchema,
  SeasonResponseSchema,
  EpisodeResponseSchema,
  MoviesResponseSchema,
  MovieResponseSchema,
  TrailerResponseSchema,
  TrailerRequestSchema,
  APIErrorSchema,
  APIFailureSchema,
  ResponseSchemas,
} from './zod-responses';

export type {
  PopularResponse,
  LatestResponse,
  SearchResponse,
  VideoListResponse,
  SeriesDetailResponse,
  SeasonsResponse,
  SeasonResponse,
  EpisodeResponse,
  MoviesResponse,
  MovieResponse,
  TrailerResponse,
  TrailerRequest,
  APIResponse,
  APIError,
  APIFailure,
} from './zod-responses';

// Validation helpers
export {
  validateAPIResponse,
  safeValidateAPIResponse,
  isAPISuccess,
  isAPIFailure,
  validatePopularResponse,
  validateSearchResponse,
  validateVideoListResponse,
  validateSeriesDetailResponse,
  validateTrailerResponse,
} from './zod-responses';

// AniList schemas and types
export {
  AniListMediaSchema,
  MediaTitleSchema,
  CoverImageSchema,
  TrailerSchema,
  MediaTagSchema,
  CharacterSchema,
  StaffSchema,
  StudioSchema,
  MediaConnectionSchema,
  CharacterConnectionSchema,
  StaffConnectionSchema,
  StudioConnectionSchema,
} from './schemas/anilist';

export type {
  AniListMedia,
  MediaTitle,
  CoverImage,
  Trailer,
  MediaTag,
  Character,
  Staff,
  Studio,
  MediaConnection,
  CharacterConnection,
  StaffConnection,
  StudioConnection,
} from './schemas/anilist';

// TMDB schemas and types
export {
  TMDBMovieDetailSchema,
  TMDBTVDetailSchema,
  TMDBGenreSchema,
  TMDBVideoSchema,
  TMDBImageSchema,
  TMDBImagesSchema,
  TMDBSearchResultSchema,
  TMDBSearchResponseSchema,
} from './schemas/tmdb';

export type {
  TMDBMovieDetail,
  TMDBTVDetail,
  TMDBGenre,
  TMDBVideo,
  TMDBImage,
  TMDBImages,
  TMDBSearchResult,
  TMDBSearchResponse,
} from './schemas/tmdb';

// Enum schemas and types
export {
  MovieKindSchema,
  MediaTypeSchema,
  MediaFormatSchema,
  MediaStatusSchema,
  MediaSeasonSchema,
  RelationTypeSchema,
  CharacterRoleSchema,
} from './schemas/base';

export type {
  MovieKind,
  MediaType,
  MediaFormat,
  MediaStatus,
  MediaSeason,
  RelationType,
  CharacterRole,
} from './schemas/base';
