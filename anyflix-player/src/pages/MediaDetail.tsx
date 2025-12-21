import { useState, useMemo, useCallback, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { FocusZone } from "../components/navigation/FocusZone";
import { FocusableItem } from "../components/navigation/FocusableItem";
import { MediaTitle, SectionTitle, MetadataText, DescriptionText } from "../components/typography";
import { useSeriesDetail } from "../lib/api/hooks";
import type { SeriesDetailResponse } from "../lib/api/hooks";
import type { components } from "../lib/api/types";
import { cn } from "../lib/utils";

// TMDB image base URL
const TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p";

// Build TMDB image URL
const buildTmdbImageUrl = (path: string | null | undefined, size: string = "original"): string | null => {
  if (!path) return null;
  return `${TMDB_IMAGE_BASE}/${size}${path}`;
};

// Format title from slug
const formatTitle = (slug: string): string => {
  return slug
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

interface EpisodeCardProps {
  episode: components["schemas"]["Episode"];
  seasonNum: number;
  episodeNum: number;
  tmdbEpisodeData?: components["schemas"]["TMDBEpisodeDetail"] | null;
  onSelect: () => void;
}

const EpisodeCard = ({ episode, seasonNum, episodeNum, tmdbEpisodeData, onSelect }: EpisodeCardProps) => {
  const stillUrl = buildTmdbImageUrl(tmdbEpisodeData?.still_path, "w300");

  return (
    <FocusableItem
      id={`episode-${seasonNum}-${episodeNum}`}
      onSelect={onSelect}
      className="relative bg-gray-800 rounded-lg overflow-hidden cursor-pointer transition-all duration-300"
      style={{
        // Force hardware acceleration for smooth focus transitions
        transform: 'translateZ(0)',
        WebkitTransform: 'translateZ(0)',
      }}
    >
      {/* Episode thumbnail */}
      <div className="relative w-full aspect-video bg-gray-900">
        {stillUrl ? (
          <img
            src={stillUrl}
            alt={`Episode ${episodeNum}`}
            className="w-full h-full object-cover"
            loading="lazy"
            style={{
              // Hardware acceleration on image
              transform: 'translateZ(0)',
              WebkitTransform: 'translateZ(0)',
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-gray-500 text-4xl font-bold">E{episodeNum}</span>
          </div>
        )}
      </div>

      {/* Episode info */}
      <div className="p-4">
        <div className="flex items-center mb-2" style={{ gap: '0.5rem' }}>
          <span className="text-primary font-bold">Episode {episodeNum}</span>
          {tmdbEpisodeData?.runtime && (
            <span className="text-gray-400 text-sm">{tmdbEpisodeData.runtime}min</span>
          )}
        </div>

        <h3 className="text-white font-semibold mb-2 line-clamp-2">
          {tmdbEpisodeData?.name || episode.title}
        </h3>

        {tmdbEpisodeData?.overview && (
          <p className="text-gray-400 text-sm line-clamp-3">
            {tmdbEpisodeData.overview}
          </p>
        )}
      </div>
    </FocusableItem>
  );
};

interface SeasonButtonProps {
  seasonNum: number;
  isSelected: boolean;
  onSelect: () => void;
}

const SeasonButton = ({ seasonNum, isSelected, onSelect }: SeasonButtonProps) => {
  return (
    <FocusableItem
      id={`season-${seasonNum}`}
      onSelect={onSelect}
      className={cn(
        "px-6 py-3 rounded-lg font-semibold cursor-pointer text-center min-w-[120px] transition-all duration-300",
        // Use mr-4 instead of gap for Chromium 79 compatibility
        "mr-4",
        isSelected
          ? "bg-primary text-white"
          : "bg-gray-800 text-gray-300 hover:bg-gray-700"
      )}
      style={{
        // Force hardware acceleration
        transform: 'translateZ(0)',
        WebkitTransform: 'translateZ(0)',
      }}
    >
      Season {seasonNum}
    </FocusableItem>
  );
};

const MediaDetailContent = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const url = searchParams.get("url");
  const source = searchParams.get("source");

  const [selectedSeasonNum, setSelectedSeasonNum] = useState<number>(1);

  // Fetch series detail
  const { data, error, isLoading } = useSeriesDetail(
    source || "aniworld",
    url || ""
  );

  // Memoized backdrop URL
  const backdropUrl = useMemo(() => {
    if (!data?.tmdb_series_data?.backdrop_path) return null;
    return buildTmdbImageUrl(data.tmdb_series_data.backdrop_path, "original");
  }, [data?.tmdb_series_data?.backdrop_path]);

  // Memoized formatted title
  const title = useMemo(() => {
    if (!data?.series?.slug) return "";
    return formatTitle(data.series.slug);
  }, [data?.series?.slug]);

  // Memoized seasons
  const seasons = useMemo(() => {
    return data?.series?.seasons || [];
  }, [data?.series?.seasons]);

  // Selected season data
  const selectedSeason = useMemo(() => {
    return seasons.find(s => s.season === selectedSeasonNum);
  }, [seasons, selectedSeasonNum]);

  // Handle episode selection
  const handleEpisodeSelect = useCallback((episodeUrl: string, seasonNum: number, episodeNum: number) => {
    const params = new URLSearchParams();
    params.set("url", episodeUrl);
    params.set("source", source || "aniworld");
    params.set("seriesUrl", url || "");
    params.set("season", seasonNum.toString());
    params.set("episode", episodeNum.toString());

    navigate(`/watch?${params.toString()}`);
  }, [navigate, source, url]);

  // Handle Play button (plays first episode of selected season)
  const handlePlay = useCallback(() => {
    if (!selectedSeason?.episodes || selectedSeason.episodes.length === 0) return;

    const firstEpisode = selectedSeason.episodes[0];
    handleEpisodeSelect(firstEpisode.url, selectedSeasonNum, firstEpisode.episode || 1);
  }, [selectedSeason, selectedSeasonNum, handleEpisodeSelect]);

  // Handle More Info (scroll to episodes section)
  const handleMoreInfo = useCallback(() => {
    const episodesSection = document.getElementById("episodes-section");
    episodesSection?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Handle back button - listen for Escape/Back key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Back button (webOS) or Escape (browser)
      if (e.keyCode === 461 || e.keyCode === 27) {
        e.preventDefault();
        e.stopPropagation();
        navigate(-1);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [navigate]);

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-white text-xl">Loading series details...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !data) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Error loading series</h2>
          <p className="text-gray-400 mb-6">
            {error?.message || "Failed to load series details"}
          </p>
          <button
            onClick={() => navigate(-1)}
            className="px-6 py-3 bg-primary text-white rounded-lg font-semibold"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background overflow-y-auto">
        {/* Hero Section - 70vh height */}
        <div className="relative h-[70vh] w-full overflow-hidden">
          {/* Backdrop Image */}
          {backdropUrl && (
            <div
              className="absolute inset-0 w-full h-full"
              style={{
                // Force hardware acceleration
                transform: 'translateZ(0)',
                WebkitTransform: 'translateZ(0)',
              }}
            >
              <img
                src={backdropUrl}
                alt={title}
                className="w-full h-full object-cover"
                style={{
                  // Hardware acceleration on image
                  transform: 'translateZ(0)',
                  WebkitTransform: 'translateZ(0)',
                }}
              />
            </div>
          )}

          {/* Bottom Gradient Overlay - NO backdrop-blur for Chromium 79 */}
          <div
            className="absolute inset-x-0 bottom-0 h-3/4 pointer-events-none"
            style={{
              background: 'linear-gradient(to top, hsl(0 0% 8%) 0%, hsl(0 0% 8% / 0.6) 50%, transparent 100%)',
              // Force hardware acceleration
              transform: 'translateZ(0)',
              WebkitTransform: 'translateZ(0)',
            }}
          />

          {/* Side Gradient Overlay - NO backdrop-blur for Chromium 79 */}
          <div
            className="absolute inset-y-0 left-0 w-1/3 pointer-events-none"
            style={{
              background: 'linear-gradient(to right, hsl(0 0% 8%) 0%, transparent 100%)',
              // Force hardware acceleration
              transform: 'translateZ(0)',
              WebkitTransform: 'translateZ(0)',
            }}
          />

          {/* Hero Content - positioned at bottom with justify-end */}
          <div className="relative h-full flex flex-col justify-end px-8 md:px-16 lg:px-20 pb-12 z-10">
            {/* Title */}
            <MediaTitle>{title}</MediaTitle>

            {/* Metadata */}
            <div className="flex items-center mb-6" style={{ gap: '1rem' }}>
              {data.tmdb_series_data?.first_air_date && (
                <MetadataText>
                  {new Date(data.tmdb_series_data.first_air_date).getFullYear()}
                </MetadataText>
              )}
              {data.season_count !== null && data.season_count !== undefined && (
                <MetadataText>
                  {data.season_count} {data.season_count === 1 ? 'Season' : 'Seasons'}
                </MetadataText>
              )}
              {data.tmdb_series_data?.vote_average && (
                <MetadataText>
                  ⭐ {data.tmdb_series_data.vote_average.toFixed(1)}
                </MetadataText>
              )}
            </div>

            {/* Description */}
            {data.tmdb_series_data?.overview && (
              <div className="max-w-2xl mb-8">
                <DescriptionText>
                  {data.tmdb_series_data.overview}
                </DescriptionText>
              </div>
            )}

            {/* Action Buttons */}
            <FocusZone
              id="hero-actions"
              type="row"
              priority={0}
              navigationAxis="horizontal"
              className="flex"
            >
              <FocusableItem
                id="btn-play"
                onSelect={handlePlay}
                className={cn(
                  "px-8 py-4 rounded-lg font-bold text-lg cursor-pointer transition-all duration-300",
                  "bg-primary text-white hover:bg-primary/90",
                  // Use mr-4 instead of gap for Chromium 79 compatibility
                  "mr-4"
                )}
                style={{
                  // Force hardware acceleration
                  transform: 'translateZ(0)',
                  WebkitTransform: 'translateZ(0)',
                }}
              >
                ▶ Play
              </FocusableItem>

              <FocusableItem
                id="btn-more-info"
                onSelect={handleMoreInfo}
                className={cn(
                  "px-8 py-4 rounded-lg font-bold text-lg cursor-pointer transition-all duration-300",
                  "bg-gray-700/80 text-white hover:bg-gray-600/80"
                )}
                style={{
                  // Force hardware acceleration
                  transform: 'translateZ(0)',
                  WebkitTransform: 'translateZ(0)',
                }}
              >
                ℹ More Info
              </FocusableItem>
            </FocusZone>
          </div>
        </div>

        {/* Episodes Section */}
        <div id="episodes-section" className="px-8 md:px-16 lg:px-20 py-12">
          {/* Season Selector */}
          {seasons.length > 0 && (
            <div className="mb-8">
              <SectionTitle className="mb-4">Seasons</SectionTitle>
              <FocusZone
                id="season-selector"
                type="row"
                priority={1}
                rememberFocus
                navigationAxis="horizontal"
                className="flex overflow-x-auto pb-4 scrollbar-hide"
              >
                {seasons.map(season => (
                  <SeasonButton
                    key={season.season}
                    seasonNum={season.season}
                    isSelected={season.season === selectedSeasonNum}
                    onSelect={() => setSelectedSeasonNum(season.season)}
                  />
                ))}
              </FocusZone>
            </div>
          )}

          {/* Episode Grid */}
          {selectedSeason?.episodes && selectedSeason.episodes.length > 0 && (
            <div>
              <SectionTitle className="mb-6">
                Season {selectedSeasonNum} Episodes
              </SectionTitle>

              <FocusZone
                id="episode-grid"
                type="grid"
                priority={2}
                rememberFocus
                navigationAxis="both"
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
                style={{
                  // Use manual gap with margin for Chromium 79 compatibility
                  gap: '1.5rem'
                }}
              >
                {selectedSeason.episodes.map((episode) => {
                  const episodeNum = episode.episode || 0;

                  return (
                    <EpisodeCard
                      key={episode.url}
                      episode={episode}
                      seasonNum={selectedSeasonNum}
                      episodeNum={episodeNum}
                      tmdbEpisodeData={
                        (episode as components["schemas"]["EnrichedEpisode"]).tmdb_episode_data
                      }
                      onSelect={() => handleEpisodeSelect(episode.url, selectedSeasonNum, episodeNum)}
                    />
                  );
                })}
              </FocusZone>
            </div>
          )}

          {/* Empty state */}
          {(!selectedSeason?.episodes || selectedSeason.episodes.length === 0) && (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">
                No episodes found for this season
              </p>
            </div>
          )}
        </div>
    </div>
  );
};

// Main component - uses FocusProvider from App.tsx
const MediaDetail = () => {
  return <MediaDetailContent />;
};

export default MediaDetail;
