import { useWebOSFocus } from "@/hooks/useWebOSFocus";
import { SeasonSelectorProps } from "../types";
import { cn } from "@/lib/utils";

export const SeasonSelector = ({
  seasons,
  selectedSeason,
  onSeasonChange,
}: SeasonSelectorProps) => {
  if (seasons.length <= 1) {
    return null;
  }

  return (
    <div className="flex gap-2 flex-wrap">
      {seasons.map((season) => {
        const isSelected = season.season === selectedSeason;
        return (
          <SeasonButton
            key={season.season}
            season={season}
            isSelected={isSelected}
            onClick={() => onSeasonChange(season.season)}
          />
        );
      })}
    </div>
  );
};

interface SeasonButtonProps {
  season: { season: number; title?: string };
  isSelected: boolean;
  onClick: () => void;
}

const SeasonButton = ({ season, isSelected, onClick }: SeasonButtonProps) => {
  const { ref, focusableProps, isFocused } = useWebOSFocus({
    onEnter: onClick,
  });

  return (
    <button
      ref={ref as React.RefObject<HTMLButtonElement>}
      {...focusableProps}
      onClick={onClick}
      className={cn(
        "px-4 py-2 rounded-lg font-medium transition-all duration-200",
        "min-w-[100px] text-center",
        isSelected
          ? "bg-white text-black"
          : "bg-gray-800 text-white hover:bg-gray-700",
        isFocused && !isSelected && "ring-2 ring-white ring-offset-2 ring-offset-background"
      )}
    >
      {season.title || `Season ${season.season}`}
    </button>
  );
};
