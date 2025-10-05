import { components } from "@/lib/api/types";

export type Season = components["schemas"]["Season"];
export type Episode = components["schemas"]["Episode"];

export interface SeasonEpisodeSelectorProps {
  seasons: Season[];
  selectedSeason?: number;
  onSeasonChange?: (season: number) => void;
  onEpisodeClick: (episodeUrl: string, episode: Episode) => void;
  className?: string;
}

export interface SeasonSelectorProps {
  seasons: Season[];
  selectedSeason: number;
  onSeasonChange: (season: number) => void;
}

export interface EpisodeCardProps {
  episode: Episode;
  onClick: () => void;
}

export interface EpisodeGridProps {
  episodes: Episode[];
  onEpisodeClick: (episodeUrl: string, episode: Episode) => void;
}
