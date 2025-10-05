import { cn } from "@/lib/utils";
import {
  Play,
  Pause,
  SkipForward,
  SkipBack,
  Maximize,
  Minimize,
  List,
} from "lucide-react";
import { VolumeControl } from "./VolumeControl";
import { QualitySelector } from "./QualitySelector";
import { NextEpisodeButton } from "./NextEpisodeButton";
import { VideoSource, GroupedVideos, Episode } from "../types";

interface ControlBarProps {
  isPlaying: boolean;
  showControls: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
  isFullscreen: boolean;
  groupedVideos: GroupedVideos;
  selectedVideo: VideoSource;
  onTogglePlay: () => void;
  onSkip: (seconds: number) => void;
  onToggleMute: () => void;
  onVolumeChange: (volume: number) => void;
  onVideoSelect: (video: VideoSource) => void;
  onToggleFullscreen: () => void;
  // Episode navigation
  nextEpisode?: Episode | null;
  onNextEpisode?: () => void;
  onShowEpisodeSelector?: () => void;
}

const formatTime = (seconds: number) => {
  if (isNaN(seconds)) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
};

export const ControlBar = ({
  isPlaying,
  showControls,
  currentTime,
  duration,
  volume,
  isMuted,
  isFullscreen,
  groupedVideos,
  selectedVideo,
  onTogglePlay,
  onSkip,
  onToggleMute,
  onVolumeChange,
  onVideoSelect,
  onToggleFullscreen,
  nextEpisode,
  onNextEpisode,
  onShowEpisodeSelector,
}: ControlBarProps) => {
  return (
    <div
      className={cn(
        "absolute bottom-0 left-0 right-0 transition-all duration-300",
        showControls
          ? "translate-y-0 opacity-100"
          : "translate-y-full opacity-0"
      )}
    >
      <div className="px-6 pb-6">
        <div className="flex items-center gap-4">
          {/* Left Controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={onTogglePlay}
              className="text-white hover:text-gray-300 transition-colors"
              aria-label={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? (
                <Pause className="w-8 h-8" />
              ) : (
                <Play className="w-8 h-8" />
              )}
            </button>

            <button
              onClick={() => onSkip(-10)}
              className="text-white hover:text-gray-300 transition-colors"
              aria-label="Skip backward 10 seconds"
            >
              <SkipBack className="w-6 h-6" />
            </button>

            <button
              onClick={() => onSkip(10)}
              className="text-white hover:text-gray-300 transition-colors"
              aria-label="Skip forward 10 seconds"
            >
              <SkipForward className="w-6 h-6" />
            </button>

            <VolumeControl
              volume={volume}
              isMuted={isMuted}
              onVolumeChange={onVolumeChange}
              onToggleMute={onToggleMute}
            />

            <div className="text-white text-sm font-medium">
              {formatTime(currentTime)} / {formatTime(duration)}
            </div>
          </div>

          {/* Right Controls */}
          <div className="flex-1" />
          <div className="flex items-center gap-3">
            {/* Episode Navigation */}
            {nextEpisode && onNextEpisode && (
              <NextEpisodeButton
                nextEpisode={nextEpisode}
                onNextEpisode={onNextEpisode}
              />
            )}

            {onShowEpisodeSelector && (
              <button
                onClick={onShowEpisodeSelector}
                className="flex items-center gap-2 text-white hover:text-gray-300 transition-colors px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg"
                aria-label="Show episodes"
              >
                <List className="w-5 h-5" />
                <span className="text-sm font-medium hidden md:inline">
                  Episodes
                </span>
              </button>
            )}

            <QualitySelector
              groupedVideos={groupedVideos}
              selectedVideo={selectedVideo}
              onVideoSelect={onVideoSelect}
            />

            <button
              onClick={onToggleFullscreen}
              className="text-white hover:text-gray-300 transition-colors"
              aria-label={
                isFullscreen ? "Exit fullscreen" : "Enter fullscreen"
              }
            >
              {isFullscreen ? (
                <Minimize className="w-6 h-6" />
              ) : (
                <Maximize className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
