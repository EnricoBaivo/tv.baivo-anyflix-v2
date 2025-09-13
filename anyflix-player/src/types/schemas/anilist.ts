/**
 * AniList Zod schemas for GraphQL API responses
 * Complete AniList data models with runtime validation
 */

import { z } from 'zod';
import { 
  MediaFormatSchema, 
  MediaTypeSchema, 
  MediaStatusSchema, 
  MediaSeasonSchema,
  RelationTypeSchema,
  CharacterRoleSchema,
  AniListDateSchema,
  type MediaFormat,
  type MediaType,
  type MediaStatus,
  type MediaSeason,
  type AniListDate
} from './base';

// =============================================
// AniList Core Models
// =============================================

export const MediaTitleSchema = z.object({
  romaji: z.string().optional(),
  english: z.string().optional(),
  native: z.string().optional(),
  userPreferred: z.string().optional()
});
export type MediaTitle = z.infer<typeof MediaTitleSchema>;

export const CoverImageSchema = z.object({
  extraLarge: z.string().optional(),
  large: z.string().optional(),
  medium: z.string().optional(),
  color: z.string().optional()
});
export type CoverImage = z.infer<typeof CoverImageSchema>;

export const TrailerSchema = z.object({
  id: z.string().optional(),
  site: z.string().optional(),
  thumbnail: z.string().optional()
});
export type Trailer = z.infer<typeof TrailerSchema>;

export const NextAiringEpisodeSchema = z.object({
  airingAt: z.number().optional(),
  timeUntilAiring: z.number().optional(),
  episode: z.number().optional()
});
export type NextAiringEpisode = z.infer<typeof NextAiringEpisodeSchema>;

export const MediaTagSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().optional(),
  category: z.string().optional(),
  rank: z.number().optional(),
  isGeneralSpoiler: z.boolean().optional(),
  isMediaSpoiler: z.boolean().optional(),
  isAdult: z.boolean().optional(),
  userId: z.number().optional()
});
export type MediaTag = z.infer<typeof MediaTagSchema>;

export const MediaRankingSchema = z.object({
  id: z.number(),
  rank: z.number(),
  type: z.string(),
  format: MediaFormatSchema,
  year: z.number().optional(),
  season: MediaSeasonSchema.optional(),
  allTime: z.boolean().optional(),
  context: z.string()
});
export type MediaRanking = z.infer<typeof MediaRankingSchema>;

export const StatusDistributionSchema = z.object({
  status: z.string().optional(),
  amount: z.number().optional()
});
export type StatusDistribution = z.infer<typeof StatusDistributionSchema>;

export const ScoreDistributionSchema = z.object({
  score: z.number().optional(),
  amount: z.number().optional()
});
export type ScoreDistribution = z.infer<typeof ScoreDistributionSchema>;

export const MediaStatsSchema = z.object({
  statusDistribution: z.array(StatusDistributionSchema).optional(),
  scoreDistribution: z.array(ScoreDistributionSchema).optional()
});
export type MediaStats = z.infer<typeof MediaStatsSchema>;

export const StreamingEpisodeSchema = z.object({
  title: z.string().optional(),
  thumbnail: z.string().optional(),
  url: z.string().optional(),
  site: z.string().optional()
});
export type StreamingEpisode = z.infer<typeof StreamingEpisodeSchema>;

export const ExternalLinkSchema = z.object({
  id: z.number(),
  url: z.string().optional(),
  site: z.string(),
  siteId: z.number().optional(),
  type: z.string().optional(),
  language: z.string().optional(),
  color: z.string().optional(),
  icon: z.string().optional(),
  notes: z.string().optional(),
  isDisabled: z.boolean().optional()
});
export type ExternalLink = z.infer<typeof ExternalLinkSchema>;

// =============================================
// Character and Staff Models
// =============================================

export const CharacterNameSchema = z.object({
  first: z.string().optional(),
  middle: z.string().optional(),
  last: z.string().optional(),
  full: z.string().optional(),
  native: z.string().optional(),
  alternative: z.array(z.string()).optional(),
  alternativeSpoiler: z.array(z.string()).optional(),
  userPreferred: z.string().optional()
});
export type CharacterName = z.infer<typeof CharacterNameSchema>;

export const CharacterImageSchema = z.object({
  large: z.string().optional(),
  medium: z.string().optional()
});
export type CharacterImage = z.infer<typeof CharacterImageSchema>;

export const CharacterSchema = z.object({
  id: z.number(),
  name: CharacterNameSchema.optional(),
  image: CharacterImageSchema.optional(),
  description: z.string().optional(),
  gender: z.string().optional(),
  dateOfBirth: AniListDateSchema.optional(),
  age: z.string().optional(),
  bloodType: z.string().optional(),
  isFavourite: z.boolean().optional(),
  isFavouriteBlocked: z.boolean().optional(),
  siteUrl: z.string().optional()
});
export type Character = z.infer<typeof CharacterSchema>;

export const StaffNameSchema = z.object({
  first: z.string().optional(),
  middle: z.string().optional(),
  last: z.string().optional(),
  full: z.string().optional(),
  native: z.string().optional(),
  alternative: z.array(z.string()).optional(),
  userPreferred: z.string().optional()
});
export type StaffName = z.infer<typeof StaffNameSchema>;

export const StaffImageSchema = z.object({
  large: z.string().optional(),
  medium: z.string().optional()
});
export type StaffImage = z.infer<typeof StaffImageSchema>;

export const StaffSchema = z.object({
  id: z.number(),
  name: StaffNameSchema.optional(),
  languageV2: z.string().optional(),
  image: StaffImageSchema.optional(),
  description: z.string().optional(),
  primaryOccupations: z.array(z.string()).optional(),
  gender: z.string().optional(),
  dateOfBirth: AniListDateSchema.optional(),
  dateOfDeath: AniListDateSchema.optional(),
  age: z.number().optional(),
  yearsActive: z.array(z.number()).optional(),
  homeTown: z.string().optional(),
  bloodType: z.string().optional(),
  isFavourite: z.boolean().optional(),
  isFavouriteBlocked: z.boolean().optional(),
  siteUrl: z.string().optional()
});
export type Staff = z.infer<typeof StaffSchema>;

export const VoiceActorSchema = StaffSchema.extend({
  language: z.string().optional()
});
export type VoiceActor = z.infer<typeof VoiceActorSchema>;

// =============================================
// Studio Models
// =============================================

export const StudioSchema = z.object({
  id: z.number(),
  name: z.string(),
  isAnimationStudio: z.boolean().optional(),
  siteUrl: z.string().optional(),
  isFavourite: z.boolean().optional()
});
export type Studio = z.infer<typeof StudioSchema>;

// =============================================
// User Models
// =============================================

export const UserAvatarSchema = z.object({
  large: z.string().optional(),
  medium: z.string().optional()
});
export type UserAvatar = z.infer<typeof UserAvatarSchema>;

export const UserSchema = z.object({
  id: z.number(),
  name: z.string(),
  avatar: UserAvatarSchema.optional(),
  bannerImage: z.string().optional(),
  about: z.string().optional(),
  isFollowing: z.boolean().optional(),
  isFollower: z.boolean().optional(),
  isBlocked: z.boolean().optional(),
  bans: z.array(z.any()).optional(),
  options: z.record(z.any()).optional(),
  mediaListOptions: z.record(z.any()).optional(),
  favourites: z.record(z.any()).optional(),
  statistics: z.record(z.any()).optional(),
  unreadNotificationCount: z.number().optional(),
  siteUrl: z.string().optional(),
  donatorTier: z.number().optional(),
  donatorBadge: z.string().optional(),
  moderatorRoles: z.array(z.string()).optional(),
  createdAt: z.number().optional(),
  updatedAt: z.number().optional()
});
export type User = z.infer<typeof UserSchema>;

// =============================================
// Pagination Models
// =============================================

export const PageInfoSchema = z.object({
  total: z.number().optional(),
  perPage: z.number().optional(),
  currentPage: z.number().optional(),
  lastPage: z.number().optional(),
  hasNextPage: z.boolean().optional()
});
export type PageInfo = z.infer<typeof PageInfoSchema>;

// =============================================
// Connection Types (GraphQL structure)
// =============================================

export const CharacterEdgeSchema = z.object({
  id: z.number().optional(),
  role: CharacterRoleSchema.optional(),
  name: z.string().optional(),
  voiceActors: z.array(VoiceActorSchema).optional(),
  node: CharacterSchema.optional()
});
export type CharacterEdge = z.infer<typeof CharacterEdgeSchema>;

export const StaffEdgeSchema = z.object({
  id: z.number().optional(),
  role: z.string().optional(),
  node: StaffSchema.optional()
});
export type StaffEdge = z.infer<typeof StaffEdgeSchema>;

export const StudioEdgeSchema = z.object({
  id: z.number().optional(),
  isMain: z.boolean(),
  node: StudioSchema.optional()
});
export type StudioEdge = z.infer<typeof StudioEdgeSchema>;

export const CharacterConnectionSchema = z.object({
  edges: z.array(CharacterEdgeSchema).optional(),
  nodes: z.array(CharacterSchema).optional()
});
export type CharacterConnection = z.infer<typeof CharacterConnectionSchema>;

export const StaffConnectionSchema = z.object({
  edges: z.array(StaffEdgeSchema).optional(),
  nodes: z.array(StaffSchema).optional()
});
export type StaffConnection = z.infer<typeof StaffConnectionSchema>;

export const StudioConnectionSchema = z.object({
  edges: z.array(StudioEdgeSchema).optional(),
  nodes: z.array(StudioSchema).optional()
});
export type StudioConnection = z.infer<typeof StudioConnectionSchema>;

// =============================================
// Main Media Model (with lazy evaluation for circular references)
// =============================================

export const AniListMediaSchema = z.lazy(() => z.object({
  id: z.number(),
  idMal: z.number().optional(),
  title: MediaTitleSchema.optional(),
  type: MediaTypeSchema.optional(),
  format: MediaFormatSchema.optional(),
  status: MediaStatusSchema.optional(),
  description: z.string().optional(),
  startDate: AniListDateSchema.optional(),
  endDate: AniListDateSchema.optional(),
  season: MediaSeasonSchema.optional(),
  seasonYear: z.number().optional(),
  seasonInt: z.number().optional(),
  episodes: z.number().optional(),
  duration: z.number().optional(),
  chapters: z.number().optional(),
  volumes: z.number().optional(),
  countryOfOrigin: z.string().optional(),
  isLicensed: z.boolean().optional(),
  source: z.string().optional(),
  hashtag: z.string().optional(),
  trailer: TrailerSchema.optional(),
  updatedAt: z.number().optional(),
  coverImage: CoverImageSchema.optional(),
  bannerImage: z.string().optional(),
  genres: z.array(z.string()).optional(),
  synonyms: z.array(z.string()).optional(),
  averageScore: z.number().optional(),
  meanScore: z.number().optional(),
  popularity: z.number().optional(),
  isLocked: z.boolean().optional(),
  trending: z.number().optional(),
  favourites: z.number().optional(),
  tags: z.array(MediaTagSchema).optional(),
  relations: z.lazy(() => MediaConnectionSchema).optional(),
  characters: CharacterConnectionSchema.optional(),
  characterPreview: CharacterConnectionSchema.optional(),
  staff: StaffConnectionSchema.optional(),
  staffPreview: StaffConnectionSchema.optional(),
  studios: StudioConnectionSchema.optional(),
  isFavourite: z.boolean().optional(),
  isFavouriteBlocked: z.boolean().optional(),
  isAdult: z.boolean().optional(),
  nextAiringEpisode: NextAiringEpisodeSchema.optional(),
  airingSchedule: z.any().optional(),
  trends: z.any().optional(),
  externalLinks: z.array(ExternalLinkSchema).optional(),
  streamingEpisodes: z.array(StreamingEpisodeSchema).optional(),
  rankings: z.array(MediaRankingSchema).optional(),
  mediaListEntry: z.any().optional(),
  reviews: z.any().optional(),
  reviewPreview: z.any().optional(),
  recommendations: z.any().optional(),
  stats: MediaStatsSchema.optional(),
  siteUrl: z.string().optional(),
  autoCreateForumThread: z.boolean().optional(),
  isRecommendationBlocked: z.boolean().optional(),
  isReviewBlocked: z.boolean().optional(),
  modNotes: z.string().optional()
}));

export type AniListMedia = z.infer<typeof AniListMediaSchema>;

export const MediaEdgeSchema = z.object({
  id: z.number().optional(),
  relationType: RelationTypeSchema.optional(),
  isMainStudio: z.boolean().optional(),
  characters: z.array(CharacterSchema).optional(),
  characterRole: CharacterRoleSchema.optional(),
  characterName: z.string().optional(),
  roleNotes: z.string().optional(),
  dubGroup: z.string().optional(),
  staffRole: z.string().optional(),
  voiceActors: z.array(VoiceActorSchema).optional(),
  voiceActorRoles: z.array(z.any()).optional(),
  node: AniListMediaSchema.optional()
});
export type MediaEdge = z.infer<typeof MediaEdgeSchema>;

export const MediaConnectionSchema = z.object({
  edges: z.array(MediaEdgeSchema).optional(),
  nodes: z.array(AniListMediaSchema).optional(),
  pageInfo: PageInfoSchema.optional()
});
export type MediaConnection = z.infer<typeof MediaConnectionSchema>;
