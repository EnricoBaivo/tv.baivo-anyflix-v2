import { useState, useMemo } from "react";
import { cn } from "@/lib/utils";
import { VideoPlayerProps } from "./types";
import {
  useVideoPlayer,
  useVideoControls,
  useControlsVisibility,
} from "./hooks";
import {
  LoadingSpinner,
  ErrorMessage,
  PlayOverlay,
  TopBar,
  ProgressBar,
  ControlBar,
  EpisodeSelectorOverlay,
} from "./components";
import { groupVideosByLanguage } from "./utils/videoUtils";

const VideoPlayer = ({
  videos,
  autoPlay = false,
  className,
  currentEpisode,
  currentSeason,
  allSeasons,
  onEpisodeChange,
  onBack,
}: VideoPlayerProps) => {
  const [selectedVideo, setSelectedVideo] = useState(videos[0]);
  const [showEpisodeSelector, setShowEpisodeSelector] = useState(false);

  const {
    videoRef,
    isPlaying,
    isLoading,
    error,
    currentTime,
    duration,
    volume,
    isMuted,
  } = useVideoPlayer(selectedVideo, autoPlay);

  const {
    isFullscreen,
    togglePlay,
    toggleMute,
    toggleFullscreen,
    handleVolumeChange,
    skip,
    seekTo,
  } = useVideoControls(videoRef);

  const { showControls, setShowControls, resetControlsTimeout } =
    useControlsVisibility(isPlaying);

  // Calculate next episode if episode data is available
  const nextEpisode = useMemo(() => {
    if (!currentEpisode || !currentSeason || !allSeasons) return null;

    const currentEpisodeIndex = currentSeason.episodes.findIndex(
      (ep) => ep.episode === currentEpisode.episode
    );

    // Check if there's a next episode in the current season
    if (currentEpisodeIndex < currentSeason.episodes.length - 1) {
      return currentSeason.episodes[currentEpisodeIndex + 1];
    }

    // Check if there's a next season
    const currentSeasonIndex = allSeasons.findIndex(
      (s) => s.season === currentSeason.season
    );
    if (currentSeasonIndex < allSeasons.length - 1) {
      const nextSeason = allSeasons[currentSeasonIndex + 1];
      return nextSeason.episodes[0] || null;
    }

    return null;
  }, [currentEpisode, currentSeason, allSeasons]);

  const handleNextEpisode = () => {
    if (nextEpisode && onEpisodeChange) {
      onEpisodeChange(nextEpisode.url, nextEpisode);
    }
  };

  const handleEpisodeSelect = (episodeUrl: string, episode: typeof currentEpisode) => {
    if (onEpisodeChange && episode) {
      onEpisodeChange(episodeUrl, episode);
    }
  };

  if (!selectedVideo?.url || videos.length === 0) {
    return (
      <div
        className={cn(
          "flex items-center justify-center bg-black rounded-lg min-h-screen",
          className
        )}
      >
        <p className="text-white text-center">No video source available</p>
      </div>
    );
  }

  const groupedVideos = groupVideosByLanguage(videos);

  return (
    <div
      className={cn(
        "relative bg-black w-full h-screen overflow-hidden",
        className
      )}
      onMouseMove={resetControlsTimeout}
      onMouseLeave={() => isPlaying && setShowControls(false)}
    >
      <video
        ref={videoRef}
        className="w-full h-full object-contain"
        playsInline
        onClick={togglePlay}
      />

      {isLoading && <LoadingSpinner />}

      {error && <ErrorMessage error={error} />}

      {!isPlaying && !isLoading && !error && (
        <PlayOverlay onPlay={togglePlay} />
      )}

      {/* Episode Selector Overlay */}
      {showEpisodeSelector && currentEpisode && currentSeason && allSeasons && (
        <EpisodeSelectorOverlay
          currentEpisode={currentEpisode}
          currentSeason={currentSeason}
          allSeasons={allSeasons}
          onEpisodeSelect={handleEpisodeSelect}
          onClose={() => setShowEpisodeSelector(false)}
        />
      )}

      {!isLoading && !error && (
        <>
          <TopBar
            selectedVideo={selectedVideo}
            showControls={showControls}
            onBack={onBack}
          />

          <div
            className={cn(
              "absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/80 to-transparent transition-all duration-300 z-10",
              showControls
                ? "translate-y-0 opacity-100"
                : "translate-y-full opacity-0"
            )}
          >
            <ProgressBar
              currentTime={currentTime}
              duration={duration}
              onSeek={seekTo}
            />

            <ControlBar
              isPlaying={isPlaying}
              showControls={showControls}
              currentTime={currentTime}
              duration={duration}
              volume={volume}
              isMuted={isMuted}
              isFullscreen={isFullscreen}
              groupedVideos={groupedVideos}
              selectedVideo={selectedVideo}
              onTogglePlay={togglePlay}
              onSkip={(seconds) => skip(seconds, duration)}
              onToggleMute={toggleMute}
              onVolumeChange={handleVolumeChange}
              onVideoSelect={setSelectedVideo}
              onToggleFullscreen={toggleFullscreen}
              nextEpisode={nextEpisode}
              onNextEpisode={nextEpisode ? handleNextEpisode : undefined}
              onShowEpisodeSelector={
                currentEpisode && currentSeason && allSeasons
                  ? () => setShowEpisodeSelector(true)
                  : undefined
              }
            />
          </div>
        </>
      )}
    </div>
  );
};

export default VideoPlayer;