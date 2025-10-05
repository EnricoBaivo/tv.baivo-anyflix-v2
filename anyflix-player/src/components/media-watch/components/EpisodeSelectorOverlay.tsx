import { useState } from "react";
import { X, ChevronDown, Play } from "lucide-react";
import { cn } from "@/lib/utils";
import { EpisodeSelectorProps } from "../types";

export const EpisodeSelectorOverlay = ({
  currentEpisode,
  currentSeason,
  allSeasons,
  onEpisodeSelect,
  onClose,
}: EpisodeSelectorProps) => {
  const [selectedSeasonNum, setSelectedSeasonNum] = useState(
    currentSeason.season
  );

  const selectedSeason =
    allSeasons.find((s) => s.season === selectedSeasonNum) || currentSeason;

  return (
    <div
      className="absolute inset-0 bg-black/95 z-30 overflow-y-auto"
      onClick={onClose}
    >
      <div
        className="min-h-screen p-6 md:p-12"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <h2 className="text-white text-2xl font-bold">Episodes</h2>
            
            {allSeasons.length > 1 && (
              <div className="relative">
                <select
                  value={selectedSeasonNum}
                  onChange={(e) => setSelectedSeasonNum(Number(e.target.value))}
                  aria-label="Select season"
                  className="appearance-none bg-gray-800 text-white border border-gray-600 rounded px-6 py-2 pr-10 cursor-pointer hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-white"
                >
                  {allSeasons.map((season) => (
                    <option key={season.season} value={season.season}>
                      {season.title}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
              </div>
            )}
          </div>

          <button
            onClick={onClose}
            className="text-white hover:text-gray-300 transition-colors p-2"
            aria-label="Close episode selector"
          >
            <X className="w-8 h-8" />
          </button>
        </div>

        {/* Episodes Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {selectedSeason.episodes.map((episode) => {
            const isCurrentEpisode =
              episode.episode === currentEpisode.episode &&
              selectedSeason.season === currentSeason.season;

            return (
              <button
                key={episode.url}
                onClick={() => {
                  onEpisodeSelect(episode.url, episode);
                  onClose();
                }}
                className={cn(
                  "group relative rounded-lg overflow-hidden transition-all duration-300 hover:scale-105",
                  isCurrentEpisode
                    ? "ring-2 ring-red-500"
                    : "hover:ring-2 hover:ring-white"
                )}
              >
                {/* Episode Number */}
                <div className="aspect-video bg-gray-800 relative flex items-center justify-center">
                  <span
                    className={cn(
                      "text-5xl font-bold transition-colors",
                      isCurrentEpisode
                        ? "text-red-500"
                        : "text-gray-600 group-hover:text-gray-500"
                    )}
                  >
                    {episode.episode}
                  </span>

                  {/* Play overlay on hover */}
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <div className="w-12 h-12 rounded-full border-2 border-white flex items-center justify-center">
                      <Play className="h-6 w-6 text-white fill-current ml-1" />
                    </div>
                  </div>

                  {isCurrentEpisode && (
                    <div className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded">
                      Playing
                    </div>
                  )}
                </div>

                {/* Episode Info */}
                <div className="bg-gray-900 p-3">
                  <h3 className="text-white text-sm font-medium line-clamp-2">
                    {episode.episode}. {episode.title}
                  </h3>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
