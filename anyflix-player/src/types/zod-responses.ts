/**
 * Zod schemas for API Response models from the backend
 * Based on anyflix-backend/lib/models/responses.py
 * Provides runtime validation for API responses
 */

import { z } from 'zod';
import {
  SearchResultSchema,
  MediaInfoSchema,
  VideoSourceSchema,
  SeriesDetailSchema,
  SeasonSchema,
  EpisodeSchema,
  MovieSchema,
} from './schemas/base';

// =============================================
// Generic Response Schemas
// =============================================

/**
 * Generic paginated response schema
 */
export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    type: z.string(), // "anime" or "normal"
    list: z.array(itemSchema),
    has_next_page: z.boolean().default(false)
  });

// =============================================
// Specific Response Schemas
// =============================================

/**
 * Response for popular content endpoint
 */
export const PopularResponseSchema = PaginatedResponseSchema(SearchResultSchema);
export type PopularResponse = z.infer<typeof PopularResponseSchema>;

/**
 * Response for latest updates endpoint
 */
export const LatestResponseSchema = PaginatedResponseSchema(SearchResultSchema);
export type LatestResponse = z.infer<typeof LatestResponseSchema>;

/**
 * Response for search endpoint
 */
export const SearchResponseSchema = PaginatedResponseSchema(SearchResultSchema);
export type SearchResponse = z.infer<typeof SearchResponseSchema>;

/**
 * Response for media details endpoint
 */
export const DetailResponseSchema = z.object({
  media: MediaInfoSchema
});
export type DetailResponse = z.infer<typeof DetailResponseSchema>;

/**
 * Response for video sources endpoint
 */
export const VideoListResponseSchema = z.object({
  type: z.string(), // "anime" or "normal"
  videos: z.array(VideoSourceSchema)
});
export type VideoListResponse = z.infer<typeof VideoListResponseSchema>;

/**
 * Response for hierarchical series detail endpoint
 */
export const SeriesDetailResponseSchema = z.object({
  type: z.string(), // "anime" or "normal"
  tmdb_data: z.record(z.any()).optional(),
  anilist_data: z.record(z.any()).optional(),
  match_confidence: z.number().optional(),
  series: SeriesDetailSchema
});
export type SeriesDetailResponse = z.infer<typeof SeriesDetailResponseSchema>;

/**
 * Response for seasons list endpoint
 */
export const SeasonsResponseSchema = z.object({
  type: z.string(), // "anime" or "normal"
  seasons: z.array(SeasonSchema),
  tmdb_data: z.record(z.any()).optional(),
  anilist_data: z.record(z.any()).optional(),
  match_confidence: z.number().optional()
});
export type SeasonsResponse = z.infer<typeof SeasonsResponseSchema>;

/**
 * Response for single season endpoint
 */
export const SeasonResponseSchema = z.object({
  type: z.string(), // "anime" or "normal"
  tmdb_data: z.record(z.any()).optional(),
  anilist_data: z.record(z.any()).optional(),
  season: SeasonSchema
});
export type SeasonResponse = z.infer<typeof SeasonResponseSchema>;

/**
 * Response for single episode endpoint
 */
export const EpisodeResponseSchema = z.object({
  type: z.string(), // "anime" or "normal"
  tmdb_data: z.record(z.any()).optional(),
  anilist_data: z.record(z.any()).optional(),
  episode: EpisodeSchema
});
export type EpisodeResponse = z.infer<typeof EpisodeResponseSchema>;

/**
 * Response for movies list endpoint
 */
export const MoviesResponseSchema = z.object({
  type: z.string(), // "anime" or "normal"
  movies: z.array(MovieSchema),
  tmdb_data: z.record(z.any()).optional(),
  anilist_data: z.record(z.any()).optional(),
  match_confidence: z.number().optional()
});
export type MoviesResponse = z.infer<typeof MoviesResponseSchema>;

/**
 * Response for single movie endpoint
 */
export const MovieResponseSchema = z.object({
  type: z.string(), // "anime" or "normal"
  movie: MovieSchema,
  tmdb_data: z.record(z.any()).optional(),
  anilist_data: z.record(z.any()).optional(),
  match_confidence: z.number().optional()
});
export type MovieResponse = z.infer<typeof MovieResponseSchema>;

/**
 * Request schema for trailer extraction endpoint
 */
export const TrailerRequestSchema = z.object({
  // AniList trailer data
  anilist_trailer: z.record(z.any()).optional(),
  // TMDB trailer data
  tmdb_trailer: z.record(z.any()).optional()
});
export type TrailerRequest = z.infer<typeof TrailerRequestSchema>;

/**
 * Response for trailer extraction endpoint
 */
export const TrailerResponseSchema = z.object({
  success: z.boolean(),
  original_url: z.string(),
  streamable_url: z.string().optional(),
  quality: z.string().optional(),
  site: z.string().optional(),
  error: z.string().optional()
});
export type TrailerResponse = z.infer<typeof TrailerResponseSchema>;

/**
 * Response for sources list endpoint
 */
export const SourcesResponseSchema = z.object({
  sources: z.array(z.string())
});
export type SourcesResponse = z.infer<typeof SourcesResponseSchema>;

/**
 * Response for source preferences endpoint
 */
export const SourcePreferencesResponseSchema = z.object({
  preferences: z.record(z.any())
});
export type SourcePreferencesResponse = z.infer<typeof SourcePreferencesResponseSchema>;

// =============================================
// API Error and Success Schemas
// =============================================

/**
 * Generic API error response schema
 */
export const APIErrorSchema = z.object({
  detail: z.string(),
  status_code: z.number().optional()
});
export type APIError = z.infer<typeof APIErrorSchema>;

/**
 * Generic API success response wrapper schema
 */
export const APISuccessSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    success: z.literal(true),
    data: dataSchema
  });

/**
 * Generic API failure response wrapper schema
 */
export const APIFailureSchema = z.object({
  success: z.literal(false),
  error: z.string(),
  status_code: z.number().optional()
});
export type APIFailure = z.infer<typeof APIFailureSchema>;

/**
 * Union schema for all API responses
 */
export const APIResultSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.union([APISuccessSchema(dataSchema), APIFailureSchema]);

// =============================================
// Validation Helpers
// =============================================

/**
 * Validates and parses API response data
 * @param schema - Zod schema to validate against
 * @param data - Raw data to validate
 * @returns Parsed data or throws validation error
 */
export const validateAPIResponse = <T>(
  schema: z.ZodSchema<T>,
  data: unknown
): T => {
  const result = schema.safeParse(data);
  
  if (!result.success) {
    console.error('API Response validation failed:', result.error);
    throw new Error(`Invalid API response: ${result.error.message}`);
  }
  
  return result.data;
};

/**
 * Safely validates API response data
 * @param schema - Zod schema to validate against
 * @param data - Raw data to validate
 * @returns Success object with data or failure object with error
 */
export const safeValidateAPIResponse = <T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: T } | { success: false; error: string } => {
  const result = schema.safeParse(data);
  
  if (!result.success) {
    return {
      success: false,
      error: result.error.message
    };
  }
  
  return {
    success: true,
    data: result.data
  };
};

/**
 * Type guard to check if API result is successful
 */
export const isAPISuccess = <T>(
  result: z.infer<ReturnType<typeof APIResultSchema>>
): result is z.infer<ReturnType<typeof APISuccessSchema>> => {
  return result.success === true;
};

/**
 * Type guard to check if API result is a failure
 */
export const isAPIFailure = (
  result: z.infer<ReturnType<typeof APIResultSchema>>
): result is APIFailure => {
  return result.success === false;
};

// =============================================
// Specific Response Validators
// =============================================

/**
 * Validates popular content response
 */
export const validatePopularResponse = (data: unknown) =>
  validateAPIResponse(PopularResponseSchema, data);

/**
 * Validates search response
 */
export const validateSearchResponse = (data: unknown) =>
  validateAPIResponse(SearchResponseSchema, data);

/**
 * Validates video list response
 */
export const validateVideoListResponse = (data: unknown) =>
  validateAPIResponse(VideoListResponseSchema, data);

/**
 * Validates series detail response
 */
export const validateSeriesDetailResponse = (data: unknown) =>
  validateAPIResponse(SeriesDetailResponseSchema, data);

/**
 * Validates trailer response
 */
export const validateTrailerResponse = (data: unknown) =>
  validateAPIResponse(TrailerResponseSchema, data);

// =============================================
// Export all response schemas for convenience
// =============================================

export const ResponseSchemas = {
  Popular: PopularResponseSchema,
  Latest: LatestResponseSchema,
  Search: SearchResponseSchema,
  Detail: DetailResponseSchema,
  VideoList: VideoListResponseSchema,
  SeriesDetail: SeriesDetailResponseSchema,
  Seasons: SeasonsResponseSchema,
  Season: SeasonResponseSchema,
  Episode: EpisodeResponseSchema,
  Movies: MoviesResponseSchema,
  Movie: MovieResponseSchema,
  Trailer: TrailerResponseSchema,
  Sources: SourcesResponseSchema,
  SourcePreferences: SourcePreferencesResponseSchema,
  APIError: APIErrorSchema,
  APIFailure: APIFailureSchema
} as const;

/**
 * All possible API response types from the backend
 */
export type APIResponse = 
  | SourcesResponse
  | SourcePreferencesResponse
  | PopularResponse
  | LatestResponse
  | SearchResponse
  | VideoListResponse
  | SeriesDetailResponse
  | SeasonsResponse
  | SeasonResponse
  | EpisodeResponse
  | MoviesResponse
  | MovieResponse
  | TrailerResponse
  | DetailResponse;
