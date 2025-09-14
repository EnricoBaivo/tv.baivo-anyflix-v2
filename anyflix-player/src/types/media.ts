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
  // Metadata to track data source
  dataSource?: 'tmdb' | 'anilist' | 'hybrid';
  // Original data for debugging/advanced use
  originalData?: {
    tmdb?: Record<string, unknown>;
    anilist?: Record<string, unknown>;
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

// Anime-specific interfaces for API data
export interface AnimeItem {
  name: string;
  image_url: string;
  link: string;
  tmdb_data?: Record<string, unknown>;
  anilist_data?: Record<string, unknown>;
  match_confidence?: number;
}

// Utility functions to convert anime data to unified Media format
export function convertAnimeToMedia(anime: AnimeItem, index: number = 0): Media {
  const { tmdb_data, anilist_data } = anime;
  
  // Determine primary data source
  const hasAnilist = anilist_data && Object.keys(anilist_data).length > 0;
  const hasTmdb = tmdb_data && Object.keys(tmdb_data).length > 0;
  
  let dataSource: 'tmdb' | 'anilist' | 'hybrid' = 'anilist';
  if (hasTmdb && hasAnilist) dataSource = 'hybrid';
  else if (hasTmdb) dataSource = 'tmdb';

  // Extract title with fallbacks
  const getTitle = (): string => {
    const anilistTitle = anilist_data?.title as { userPreferred?: string; english?: string; romaji?: string } | undefined;
    if (anilistTitle?.userPreferred) return anilistTitle.userPreferred;
    if (anilistTitle?.english) return anilistTitle.english;
    if (anilistTitle?.romaji) return anilistTitle.romaji;
    if (tmdb_data?.title) return tmdb_data.title as string;
    if (tmdb_data?.name) return tmdb_data.name as string;
    return anime.name;
  };

  // Extract overview/description with fallbacks
  const getOverview = (): string => {
    if (anilist_data?.description) {
      return (anilist_data.description as string).replace(/<[^>]*>/g, ''); // Strip HTML tags
    }
    if (tmdb_data?.overview) return tmdb_data.overview as string;
    return '';
  };

  // Extract images with fallbacks - prioritize TMDB over AniList
  const getPosterPath = (): string => {
    // Prioritize TMDB poster first
    if (tmdb_data?.poster_path) return tmdb_data.poster_path as string;
    
    // Fallback to AniList images (highest quality first)
    const coverImage = anilist_data?.coverImage as { 
      extraLarge?: string; 
      large?: string; 
      medium?: string; 
      color?: string; 
    } | undefined;
    
    if (coverImage?.extraLarge) return coverImage.extraLarge;
    if (coverImage?.large) return coverImage.large;
    if (coverImage?.medium) return coverImage.medium;
    
    // Final fallback to original image
    return anime.image_url || '';
  };

  const getBackdropPath = (): string => {
    // Prioritize TMDB backdrop first (usually higher quality for movies/series)
    if (tmdb_data?.backdrop_path) return tmdb_data.backdrop_path as string;
    
    // Fallback to AniList banner (good for anime)
    if (anilist_data?.bannerImage) return anilist_data.bannerImage as string;
    
    // Last resort: use cover image (prefer highest quality)
    const coverImage = anilist_data?.coverImage as { 
      extraLarge?: string; 
      large?: string; 
      medium?: string; 
    } | undefined;
    if (coverImage?.extraLarge) return coverImage.extraLarge;
    if (coverImage?.large) return coverImage.large;
    if (coverImage?.medium) return coverImage.medium;
    
    return anime.image_url || '';
  };

  // Extract release date with fallbacks
  const getReleaseDate = (): string => {
    if (tmdb_data?.release_date) return tmdb_data.release_date as string;
    if (tmdb_data?.first_air_date) return tmdb_data.first_air_date as string;
    const startDate = anilist_data?.startDate as { year?: number; month?: number; day?: number } | undefined;
    if (startDate?.year) {
      const monthStr = startDate.month ? String(startDate.month).padStart(2, '0') : '01';
      const dayStr = startDate.day ? String(startDate.day).padStart(2, '0') : '01';
      return `${startDate.year}-${monthStr}-${dayStr}`;
    }
    return '';
  };

  // Extract rating with fallbacks
  const getVoteAverage = (): number => {
    if (tmdb_data?.vote_average) return tmdb_data.vote_average as number;
    if (anilist_data?.averageScore) return (anilist_data.averageScore as number) / 10; // Convert 0-100 to 0-10
    return 0;
  };

  // Extract genres with fallbacks
  const getGenres = (): string[] => {
    if (anilist_data?.genres) return anilist_data.genres as string[];
    if (tmdb_data?.genres) {
      return (tmdb_data.genres as unknown[]).map((g: unknown) => 
        typeof g === 'string' ? g : (g as { name: string }).name
      );
    }
    return [];
  };

  // Extract AniList rankings
  const getRankings = (): { highestRated?: number; mostPopular?: number } | undefined => {
    const rankings = anilist_data?.rankings as Array<{
      rank?: number;
      type?: string;
      allTime?: boolean;
      context?: string;
    }> | undefined;

    if (!rankings || !Array.isArray(rankings)) return undefined;

    const result: { highestRated?: number; mostPopular?: number } = {};

    rankings.forEach(ranking => {
      if (ranking.allTime && ranking.rank) {
        if (ranking.type === 'RATED') {
          result.highestRated = ranking.rank;
        } else if (ranking.type === 'POPULAR') {
          result.mostPopular = ranking.rank;
        }
      }
    });

    return Object.keys(result).length > 0 ? result : undefined;
  };

  // Create unified Media object
  const anilistTitle = anilist_data?.title as { native?: string } | undefined;
  const coverImage = anilist_data?.coverImage as { 
    extraLarge?: string; 
    large?: string; 
    medium?: string; 
  } | undefined;
  
  return {
    id: (anilist_data?.id as number) || (tmdb_data?.id as number) || index,
    title: getTitle(),
    overview: getOverview(),
    poster_path: getPosterPath(),
    backdrop_path: getBackdropPath(),
    release_date: getReleaseDate(),
    vote_average: getVoteAverage(),
    vote_count: (tmdb_data?.vote_count as number) || 0,
    genre_ids: (tmdb_data?.genre_ids as number[]) || [],
    adult: (tmdb_data?.adult as boolean) || false,
    original_language: (tmdb_data?.original_language as string) || (anilist_data?.countryOfOrigin as string) || 'ja',
    original_title: (tmdb_data?.original_title as string) || anilistTitle?.native || anime.name,
    popularity: (tmdb_data?.popularity as number) || (anilist_data?.popularity as number) || 0,
    video: (tmdb_data?.video as boolean) || false,
    // Extended anime fields
    genres: getGenres(),
    episodes: anilist_data?.episodes as number | undefined,
    status: anilist_data?.status as string | undefined,
    averageScore: anilist_data?.averageScore as number | undefined,
    bannerImage: anilist_data?.bannerImage as string | undefined,
    coverImage: coverImage?.extraLarge || coverImage?.large || coverImage?.medium,
    rankings: getRankings(),
    dataSource,
    originalData: {
      tmdb: tmdb_data,
      anilist: anilist_data,
    },
  };
}

// Convert array of anime items to Media array
export function convertAnimeListToMedia(animeList: AnimeItem[]): Media[] {
  return animeList.map((anime, index) => convertAnimeToMedia(anime, index));
}