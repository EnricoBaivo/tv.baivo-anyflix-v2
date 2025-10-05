import { Play } from "lucide-react";
import { useWebOSFocus } from "@/hooks/useWebOSFocus";
import { EpisodeCardProps } from "../types";
import { cn } from "@/lib/utils";

export const EpisodeCard = ({ episode, onClick }: EpisodeCardProps) => {
  const isUpcoming = episode.title?.toLowerCase().includes("start:");
  const { ref, focusableProps, isFocused } = useWebOSFocus({
    onEnter: onClick,
    disabled: isUpcoming,
  });

  return (
    <button
      ref={ref as React.RefObject<HTMLButtonElement>}
      {...focusableProps}
      onClick={onClick}
      disabled={isUpcoming}
      className={cn(
        "group relative bg-gray-800 rounded-lg overflow-hidden transition-all duration-300",
        !isUpcoming && "hover:bg-gray-700 hover:scale-105",
        isFocused && !isUpcoming && "scale-105 bg-gray-700"
      )}
    >
      {/* Episode Number Badge */}
      <div className="aspect-video bg-gray-900 relative flex items-center justify-center">
        <span className="text-6xl font-bold text-gray-600 group-hover:text-gray-500 transition-colors">
          {episode.episode}
        </span>

        {/* Play overlay on hover */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <div className="w-16 h-16 rounded-full border-2 border-white flex items-center justify-center">
            <Play className="h-8 w-8 text-white fill-current ml-1" />
          </div>
        </div>
      </div>

      {/* Episode Info */}
      <div className="p-4 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-white text-left line-clamp-1">
            {episode.episode}. {episode.title}
          </h3>
        </div>

        {episode.tags && episode.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {episode.tags.map((tag, i) => (
              <span
                key={i}
                className="text-xs text-gray-400 bg-gray-900 px-2 py-1 rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </button>
  );
};
