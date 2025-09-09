import { Media } from "@/types/media";
import { getImageUrl } from "@/services/tmdb";
import { Play, Plus, ThumbsUp, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { useWebOSFocus } from "@/hooks/useWebOSFocus";
import { getFocusClasses, getWebOSProps } from "@/lib/webos-focus";
import { MediaTitle } from "./typography";

interface MediaCardProps {
  media: Media;
  index: number;
  isSelected?: boolean;
  isHovered?: boolean;
  isAnyHovered?: boolean;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  onFocus?: () => void;
  onClick?: () => void;
}

const MediaCard = ({
  media,
  index,
  isSelected = false,
  isHovered = false,
  isAnyHovered = false,
  onMouseEnter,
  onMouseLeave,
  onFocus,
  onClick,
}: MediaCardProps) => {
  // WebOS focus handling - when focused, automatically becomes selected
  const { focusProps, navigationMode } = useWebOSFocus({
    onFocus: onFocus, // Triggers selection when card receives focus
    onEnter: onClick, // Triggers click action when Enter is pressed
  });

  return (
    <div
      {...focusProps}
      {...getWebOSProps()}
      className={cn(
        "cursor-pointer transition-transform duration-300 transform-gpu origin-center h-full flex flex-col rounded-lg",
        isSelected ? "media-card-selected" : "media-card group",
        !isSelected && isAnyHovered && !isHovered ? "scale-95" : "scale-100",
        getFocusClasses("card", navigationMode)
      )}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onClick={onClick}
    >
      <div
        className={cn(
          "relative overflow-hidden flex-1",
          isSelected ? "rounded-lg" : "rounded-md"
        )}
      >
        <img
          src={getImageUrl(
            isSelected
              ? media.backdrop_path || media.poster_path
              : media.poster_path
          )}
          alt={media.title}
          className="w-full h-full object-cover origin-center transform-gpu"
          loading="lazy"
        />
        {/* Gradient overlay - only for selected */}
        {!isSelected && (
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
        )}
        <div
          className={cn(
            "flex flex-col items-start justify-between opacity-0 transition-opacity duration-300 absolute bottom-0 left-0 right-0 p-6 text-white",
            isHovered && !isSelected && "opacity-100"
          )}
        >
          <h2 className={"text-lg font-black truncate "}>{media.title}</h2>
          <span>{new Date(media.release_date).getFullYear()}</span>
        </div>
        <div
          className={cn(
            "absolute bottom-0 left-0 right-0 p-6 text-white transition-opacity duration-300 opacity-0",
            isSelected && "opacity-100"
          )}
        >
          <MediaTitle>{media.title}</MediaTitle>
        </div>
      </div>
    </div>
  );
};

export default MediaCard;
