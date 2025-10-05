import { useState, useMemo } from "react";
import { cn } from "@/lib/utils";
import { SectionTitle } from "@/components/typography";
import { SeasonSelector, EpisodeGrid } from "./components";
import { SeasonEpisodeSelectorProps } from "./types";

export const SeasonEpisodeSelector = ({
  seasons,
  selectedSeason: controlledSeason,
  onSeasonChange,
  onEpisodeClick,
  className,
}: SeasonEpisodeSelectorProps) => {
  // Support both controlled and uncontrolled mode
  const [internalSeason, setInternalSeason] = useState(
    seasons[0]?.season || 1
  );

  const selectedSeason = controlledSeason ?? internalSeason;

  const handleSeasonChange = (season: number) => {
    if (onSeasonChange) {
      onSeasonChange(season);
    } else {
      setInternalSeason(season);
    }
  };

  const currentSeason = useMemo(
    () => seasons.find((s) => s.season === selectedSeason) || seasons[0],
    [seasons, selectedSeason]
  );

  if (seasons.length === 0) {
    return (
      <div className={cn("text-center py-12 text-gray-400", className)}>
        No seasons available
      </div>
    );
  }

  return (
    <div className={cn("space-y-8", className)}>
      {/* Season Selector Header */}
      <div className="flex items-center gap-4">
        <SectionTitle className="mb-0">Episodes</SectionTitle>
        <SeasonSelector
          seasons={seasons}
          selectedSeason={selectedSeason}
          onSeasonChange={handleSeasonChange}
        />
      </div>

      {/* Episodes Grid */}
      <EpisodeGrid
        episodes={currentSeason?.episodes || []}
        onEpisodeClick={onEpisodeClick}
      />
    </div>
  );
};
