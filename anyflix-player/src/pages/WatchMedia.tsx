import VideoPlayer from "@/components/media-watch/VideoPlayer";
import { useVideoSources, useSeriesDetail } from "@/lib/api/hooks";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { useMemo } from "react";
import type { Episode } from "@/components/media-watch";

const WatchMedia = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const mediaUrl = searchParams.get("url");
  const source = searchParams.get("src");
  const lang = searchParams.get("lang");
  const seriesUrl = searchParams.get("seriesUrl");
  const episodeNum = searchParams.get("episode");
  const seasonNum = searchParams.get("season");
  
  // Fetch video sources
  const { data, isLoading, error } = useVideoSources(
    source || "",
    mediaUrl || "",
    lang || undefined
  );

  // Fetch series data if seriesUrl is provided
  const {
    data: seriesData,
    isLoading: isSeriesLoading,
    error: seriesError,
  } = useSeriesDetail(source || "", seriesUrl || "");

  // Find current episode and season if available (before any early returns)
  const currentEpisode = useMemo(() => {
    if (!seriesData || !episodeNum || !seasonNum) return undefined;
    
    const season = seriesData.series.seasons.find(
      (s) => s.season === Number(seasonNum)
    );
    
    if (!season) return undefined;
    
    return season.episodes.find((ep) => ep.episode === Number(episodeNum));
  }, [seriesData, episodeNum, seasonNum]);

  const currentSeason = useMemo(() => {
    if (!seriesData || !seasonNum) return undefined;
    
    return seriesData.series.seasons.find(
      (s) => s.season === Number(seasonNum)
    );
  }, [seriesData, seasonNum]);

  const handleEpisodeChange = (episodeUrl: string, episode: Episode) => {
    // Find which season this episode belongs to
    const season = seriesData?.series.seasons.find((s) =>
      s.episodes.some((ep) => ep.url === episodeUrl)
    );

    if (!season) {
      console.error("Could not find season for episode");
      return;
    }

    // Navigate to the new episode with all necessary parameters
    const params = new URLSearchParams({
      url: episodeUrl,
      src: source || "",
      ...(lang && { lang }),
      ...(seriesUrl && { seriesUrl }),
      episode: episode.episode.toString(),
      season: season.season.toString(),
    });

    navigate(`/watch?${params.toString()}`);
  };

  const handleBack = () => {
    // Navigate back to the media detail page
    console.log("handleBack", seriesUrl, source);
    if (seriesUrl && source) {
      navigate(`/media-detail?url=${encodeURIComponent(seriesUrl)}&src=${source}`);
    } else {
      window.history.back();
    }
  };

  // Check for missing parameters first
  if (!mediaUrl || !source) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center px-4">
          <h1 className="text-2xl font-bold text-white mb-4">
            Missing Parameters
          </h1>
          <p className="text-gray-400 mb-6">
            Both 'url' and 'src' search parameters are required to play video.
          </p>
          <button
            onClick={() => window.history.back()}
            className="px-6 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Show loading state
  if (isLoading || (seriesUrl && isSeriesLoading)) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-16 h-16 text-white animate-spin mx-auto mb-4" />
          <p className="text-white text-lg">Loading video sources...</p>
          <p className="text-gray-400 text-sm mt-2">Please wait</p>
        </div>
      </div>
    );
  }

  // Show error state (for video sources or series data)
  if (error || (seriesUrl && seriesError)) {
    const errorMessage = error
      ? error instanceof Error
        ? error.message
        : "Failed to load video sources"
      : seriesError instanceof Error
      ? seriesError.message
      : "Failed to load series data";

    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center px-4 max-w-md">
          <div className="bg-red-500/20 rounded-lg p-6 border border-red-500/50">
            <h1 className="text-2xl font-bold text-red-500 mb-4">
              Error Loading Video
            </h1>
            <p className="text-white mb-4">{errorMessage}</p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Retry
              </button>
              <button
                onClick={() => window.history.back()}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Check if data exists and has videos
  if (!data || !data.videos || data.videos.length === 0) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center px-4">
          <h1 className="text-2xl font-bold text-white mb-4">
            No Video Sources Found
          </h1>
          <p className="text-gray-400 mb-6">
            No playable video sources are available for this media.
          </p>
          <button
            onClick={() => window.history.back()}
            className="px-6 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Render the video player with all available video sources
  // Use mediaUrl as key to force remount when episode changes
  return (
    <VideoPlayer
      key={mediaUrl} // Force remount on episode change
      videos={data.videos}
      autoPlay={true}
      currentEpisode={currentEpisode}
      currentSeason={currentSeason}
      allSeasons={seriesData?.series.seasons}
      onEpisodeChange={handleEpisodeChange}
      onBack={handleBack}
    />
  );
};

export default WatchMedia;
