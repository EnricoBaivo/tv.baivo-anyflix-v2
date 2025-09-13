/**
 * Base Zod schemas and enums for the Anyflix Backend API
 * Core data models and enums used throughout the application
 */

import { z } from 'zod';

// =============================================
// Base Enums
// =============================================

export const MovieKindSchema = z.enum(["movie", "ova", "special"]);
export type MovieKind = z.infer<typeof MovieKindSchema>;

export const MediaTypeSchema = z.enum(["ANIME", "MANGA"]);
export type MediaType = z.infer<typeof MediaTypeSchema>;

export const MediaFormatSchema = z.enum([
  "TV", "TV_SHORT", "MOVIE", "SPECIAL", "OVA", "ONA", 
  "MUSIC", "MANGA", "NOVEL", "ONE_SHOT"
]);
export type MediaFormat = z.infer<typeof MediaFormatSchema>;

export const MediaStatusSchema = z.enum([
  "FINISHED", "RELEASING", "NOT_YET_RELEASED", "CANCELLED", "HIATUS"
]);
export type MediaStatus = z.infer<typeof MediaStatusSchema>;

export const MediaSeasonSchema = z.enum(["WINTER", "SPRING", "SUMMER", "FALL"]);
export type MediaSeason = z.infer<typeof MediaSeasonSchema>;

export const RelationTypeSchema = z.enum([
  "ADAPTATION", "PREQUEL", "SEQUEL", "PARENT", "SIDE_STORY", 
  "CHARACTER", "SUMMARY", "ALTERNATIVE", "SPIN_OFF", "OTHER", 
  "SOURCE", "COMPILATION", "CONTAINS"
]);
export type RelationType = z.infer<typeof RelationTypeSchema>;

export const CharacterRoleSchema = z.enum(["MAIN", "SUPPORTING", "BACKGROUND"]);
export type CharacterRole = z.infer<typeof CharacterRoleSchema>;

// =============================================
// Core Data Models
// =============================================

export const EpisodeSchema = z.object({
  season: z.number(),
  episode: z.number(),
  title: z.string(),
  url: z.string(),
  date_upload: z.string().optional(),
  tags: z.array(z.string()).default([])
});
export type Episode = z.infer<typeof EpisodeSchema>;

export const SeasonSchema = z.object({
  season: z.number(),
  title: z.string().optional(),
  episodes: z.array(EpisodeSchema).default([])
});
export type Season = z.infer<typeof SeasonSchema>;

export const MovieSchema = z.object({
  number: z.number(),
  title: z.string(),
  kind: MovieKindSchema,
  url: z.string(),
  date_upload: z.string().optional(),
  tags: z.array(z.string()).default([])
});
export type Movie = z.infer<typeof MovieSchema>;

export const SeriesDetailSchema = z.object({
  slug: z.string(),
  seasons: z.array(SeasonSchema).default([]),
  movies: z.array(MovieSchema).default([])
});
export type SeriesDetail = z.infer<typeof SeriesDetailSchema>;

export const MediaInfoSchema = z.object({
  name: z.string(),
  image_url: z.string(),
  description: z.string(),
  author: z.string().default(""),
  status: z.number().default(5),
  genre: z.array(z.string()).default([]),
  episodes: z.array(z.record(z.any())).default([])
});
export type MediaInfo = z.infer<typeof MediaInfoSchema>;

export const SearchResultSchema = z.object({
  name: z.string(),
  image_url: z.string(),
  link: z.string(),
  tmdb_data: z.record(z.any()).optional(),
  anilist_data: z.record(z.any()).optional(),
  match_confidence: z.number().optional()
});
export type SearchResult = z.infer<typeof SearchResultSchema>;

export const VideoSourceSchema = z.object({
  url: z.string(),
  original_url: z.string(),
  quality: z.string(),
  language: z.string().optional(),
  type: z.string().optional(),
  host: z.string().optional(),
  requires_proxy: z.boolean().default(false),
  headers: z.record(z.string()).optional(),
  subtitles: z.array(z.record(z.string())).optional(),
  audios: z.array(z.record(z.string())).optional()
});
export type VideoSource = z.infer<typeof VideoSourceSchema>;

export const SourcePreferenceSchema = z.object({
  key: z.string(),
  list_preference: z.record(z.any()).optional(),
  multi_select_list_preference: z.record(z.any()).optional()
});
export type SourcePreference = z.infer<typeof SourcePreferenceSchema>;

// =============================================
// Common Date Schema
// =============================================

export const AniListDateSchema = z.object({
  year: z.number().optional(),
  month: z.number().optional(),
  day: z.number().optional()
});
export type AniListDate = z.infer<typeof AniListDateSchema>;
