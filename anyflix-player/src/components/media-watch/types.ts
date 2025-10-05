import { components } from "@/lib/api/types";

export type VideoSource = components["schemas"]["VideoSource"];
export type Episode = components["schemas"]["Episode"];
export type Season = components["schemas"]["Season"];

export interface VideoPlayerProps {
  videos: VideoSource[];
  autoPlay?: boolean;
  className?: string;
  // Optional episode navigation
  currentEpisode?: Episode;
  currentSeason?: Season;
  allSeasons?: Season[];
  onEpisodeChange?: (episodeUrl: string, episode: Episode) => void;
  onBack?: () => void;
}

export interface GroupedVideos {
  [language: string]: VideoSource[];
}

export interface EpisodeSelectorProps {
  currentEpisode: Episode;
  currentSeason: Season;
  allSeasons: Season[];
  onEpisodeSelect: (episodeUrl: string, episode: Episode) => void;
  onClose: () => void;
}

export interface NextEpisodeButtonProps {
  nextEpisode: Episode | null;
  onNextEpisode: () => void;
}
