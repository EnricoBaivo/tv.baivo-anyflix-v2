import { useState, useMemo, useEffect, useCallback } from "react";
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
  const [triedVideoIndices, setTriedVideoIndices] = useState<Set<number>>(new Set([0]));
  const [allQualitiesExhausted, setAllQualitiesExhausted] = useState(false);

  // Handle network failure by switching to next available quality
  const handleNetworkFailure = useCallback(() => {
    // If all qualities have been exhausted, don't try to auto-switch anymore
    if (allQualitiesExhausted) {
      console.log("All qualities already exhausted, not attempting auto-switch");
      return;
    }

    const currentIndex = videos.findIndex(v => v.url === selectedVideo.url);
    
    // Try to find the next video that hasn't been tried yet
    for (let i = currentIndex + 1; i < videos.length; i++) {
      if (!triedVideoIndices.has(i)) {
        console.log(`Switching from quality ${currentIndex} to ${i} due to network failure`);
        setTriedVideoIndices(prev => new Set(prev).add(i));
        setSelectedVideo(videos[i]);
        return;
      }
    }
    
    // If no untried videos found after current, try from the beginning
    for (let i = 0; i < currentIndex; i++) {
      if (!triedVideoIndices.has(i)) {
        console.log(`Switching from quality ${currentIndex} to ${i} due to network failure`);
        setTriedVideoIndices(prev => new Set(prev).add(i));
        setSelectedVideo(videos[i]);
        return;
      }
    }
    
    // All qualities have been tried and failed
    console.log("All video qualities have been tried and failed");
    setAllQualitiesExhausted(true);
  }, [videos, selectedVideo, triedVideoIndices, allQualitiesExhausted]);

  const {
    videoRef,
    isPlaying,
    isLoading,
    error,
    currentTime,
    duration,
    volume,
    isMuted,
  } = useVideoPlayer(selectedVideo, autoPlay, handleNetworkFailure);

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

  // Reset tried video indices when videos change (e.g., new episode)
  useEffect(() => {
    setSelectedVideo(videos[0]);
    setTriedVideoIndices(new Set([0]));
    setAllQualitiesExhausted(false);
  }, [videos]);

  // Handler for manual video quality selection
  const handleVideoSelect = (video: typeof selectedVideo) => {
    const videoIndex = videos.findIndex(v => v.url === video.url);
    setSelectedVideo(video);
    
    // If all qualities were exhausted, mark all as tried except the selected one
    // This prevents auto-fallback from cycling through again
    if (allQualitiesExhausted) {
      console.log("Manual quality selection after exhaustion - preventing auto-fallback loop");
      const allIndices = Array.from({ length: videos.length }, (_, i) => i);
      setTriedVideoIndices(new Set(allIndices));
    } else {
      // Normal behavior: reset tried indices for manual retry
      setTriedVideoIndices(new Set([videoIndex]));
    }
  };

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

      {error && <ErrorMessage error={error} provider_url={selectedVideo.original_url} />}

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

      {!isLoading && (
        <>
          <TopBar
            selectedVideo={selectedVideo}
            showControls={showControls || !!error}
            onBack={onBack}
          />

          <div
            className={cn(
              "absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/80 to-transparent transition-all duration-300 z-10",
              showControls || error
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
              showControls={showControls || !!error}
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
              onVideoSelect={handleVideoSelect}
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