import { SkipForward } from "lucide-react";
import { NextEpisodeButtonProps } from "../types";

export const NextEpisodeButton = ({
  nextEpisode,
  onNextEpisode,
}: NextEpisodeButtonProps) => {
  if (!nextEpisode) return null;

  return (
    <button
      onClick={onNextEpisode}
      className="flex items-center gap-2 text-white hover:text-gray-300 transition-colors px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg"
      aria-label={`Next episode: ${nextEpisode.title}`}
      title={`Next: Episode ${nextEpisode.episode}`}
    >
      <SkipForward className="w-5 h-5" />
      <span className="text-sm font-medium hidden md:inline">
        Next Episode
      </span>
    </button>
  );
};
