import type { components } from "@/lib/api/types";
import { z } from "zod";
// If codegen exists:
// import { schemas as S } from "./openapi.zod.gen"; // e.g., S.TMDBSearchResult, S.Media, S.MediaInfo
type MediaInfo = components["schemas"]["MediaInfo"];
const MediaInfoSchema = z.custom<MediaInfo>();
// Minimal base (swap in your generated schemas if you have them)
const Base = z.object({
  name: z.string(),
  image_url: z.string().nullable().optional(),
  link: z.string(),
  media_info: MediaInfoSchema, // or your S.MediaInfo.nullish()
  confidence: z.number().nullable().optional(),
});

// If you have generated schemas:
// const Tmdb = S.TMDBSearchResult;
// const Ani  = S.Media;

// If you only have TS types, but still want inference (no structural checks):
type TmdbMatch = components["schemas"]["TMDBSearchResult"];
type AniListMatch = components["schemas"]["Media"];
const Tmdb = z.custom<TmdbMatch>();
const Ani = z.custom<AniListMatch>();

export const SearchResultSchema = z.union([
  Base.extend({ best_match_source: z.literal("tmdb"), best_match: Tmdb }),
  Base.extend({ best_match_source: z.literal("anilist"), best_match: Ani }),
  Base.extend({
    best_match_source: z.union([z.null(), z.undefined()]),
    best_match: z.union([z.null(), z.undefined()]),
  }),
]);

export type SearchResult = z.infer<typeof SearchResultSchema>;

export interface Media {
  id: number;
  title: string;
  overview: string;
  poster_path: string;
  backdrop_path: string;
  release_date: string;
  vote_average: number;
  vote_count: number;
  genre_ids: number[];
  adult: boolean;
  original_language: string;
  original_title: string;
  popularity: number;
  video: boolean;
  // Extended fields for anime/unified content
  genres?: string[]; // For AniList genre names
  episodes?: number; // For anime episode count
  status?: string; // For anime status (FINISHED, RELEASING, etc.)
  averageScore?: number; // AniList score (0-100)
  bannerImage?: string; // AniList banner image
  coverImage?: string; // AniList cover image
  // AniList rankings
  rankings?: {
    highestRated?: number; // Rank in highest rated all time
    mostPopular?: number; // Rank in most popular all time
  };
}

export interface MediaResponse {
  page: number;
  results: Media[];
  total_pages: number;
  total_results: number;
}

export interface Genre {
  id: number;
  name: string;
}

// Helper functions for extracting rankings from AniList data
const extractRankingByType = (
  rankings: unknown[] | undefined,
  type: string
): number | undefined => {
  if (!Array.isArray(rankings)) return undefined;
  return (rankings as { type: string; rank: number }[])?.find(
    (ranking) => ranking.type === type
  )?.rank;
};

const getAniListRankings = (rankings: unknown[] | undefined) => ({
  highestRated: extractRankingByType(rankings, "RATED"),
  mostPopular: extractRankingByType(rankings, "POPULAR"),
});

// Helper function to convert AniList date format to string
const formatAniListDate = (date: unknown): string => {
  if (!date || typeof date !== "object") return "";
  const dateObj = date as { year?: number; month?: number; day?: number };
  if (!dateObj.year) return "";

  const year = dateObj.year;
  const month = dateObj.month ? String(dateObj.month).padStart(2, "0") : "01";
  const day = dateObj.day ? String(dateObj.day).padStart(2, "0") : "01";

  return `${year}-${month}-${day}`;
};

// Convert AniList data to unified Media format
const convertAniListToMedia = (
  aniListData: AniListMatch,
  mediaInfo: MediaInfo
): Media => ({
  // Core media fields
  id: aniListData.id,
  title: aniListData.title?.userPreferred || mediaInfo.name || "",
  overview: aniListData.description || "",
  poster_path: aniListData.coverImage?.large || mediaInfo.cover_image_url || "",
  backdrop_path: aniListData.bannerImage || "",
  release_date: formatAniListDate(aniListData.startDate),

  // Rating and popularity
  vote_average: aniListData.averageScore || 0,
  vote_count: aniListData.meanScore || 0,
  popularity: aniListData.popularity || 0,

  // Basic metadata
  genre_ids: [0], // AniList uses string genres, not IDs
  adult: aniListData.isAdult || false,
  original_language: aniListData.countryOfOrigin || "",
  original_title: aniListData.title?.native || "",
  video: Boolean(aniListData.trailer?.site),

  // AniList-specific fields
  genres: aniListData.genres || [],
  episodes: aniListData.episodes,
  status: aniListData.status,
  averageScore: aniListData.averageScore,
  bannerImage: aniListData.bannerImage,
  coverImage: aniListData.coverImage?.large,
  rankings: getAniListRankings(aniListData.rankings),
});

// Convert TMDB data to unified Media format
const convertTMDBToMedia = (
  tmdbData: TmdbMatch,
  mediaInfo: MediaInfo
): Media => ({
  // Core media fields
  id: tmdbData.id,
  title: tmdbData.title || mediaInfo.name || "",
  overview: tmdbData.overview || "",
  poster_path: tmdbData.poster_path || mediaInfo.cover_image_url || "",
  backdrop_path: tmdbData.backdrop_path || "",
  release_date: tmdbData.release_date || "",

  // Rating and popularity
  vote_average: tmdbData.vote_average || 0,
  vote_count: tmdbData.vote_count || 0,
  popularity: tmdbData.popularity || 0,

  // Basic metadata
  genre_ids: tmdbData.genre_ids || [],
  adult: tmdbData.adult || false,
  original_language: tmdbData.original_language || "",
  original_title: tmdbData.original_title || "",
  video: tmdbData.video || false,

  // Map TMDB fields to anime-like structure for consistency
  averageScore: tmdbData.vote_average,
  bannerImage: tmdbData.backdrop_path,
  coverImage: tmdbData.poster_path,
  rankings: {
    highestRated: tmdbData.vote_average,
    mostPopular: tmdbData.popularity,
  },
});

// Convert array of anime items to Media array
export function unifyMediaList(
  mediaList: {
    name: string;
    image_url: string;
    link: string;
    media_info?: components["schemas"]["MediaInfo"] | null;
    best_match?:
      | components["schemas"]["TMDBSearchResult"]
      | components["schemas"]["Media"]
      | null;
    best_match_source?: components["schemas"]["MatchSource"] | null;
    confidence?: number | null;
  }[]
): Media[] {
  return mediaList
    .map((media, index) => {
      const { best_match, best_match_source, media_info } =
        media as SearchResult;

      // Handle null/undefined cases for best_match data (media_info is always present)
      if (!best_match || !best_match_source) {
        return null;
      }

      // Route to appropriate converter based on source
      switch (best_match_source) {
        case "anilist":
          return convertAniListToMedia(best_match, media_info);

        case "tmdb":
          return convertTMDBToMedia(best_match, media_info);

        default:
          return null;
      }
    })
    .filter((media): media is Media => media !== null);
}
