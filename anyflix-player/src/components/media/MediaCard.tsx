import { Media } from "@/types/media";
import { getImageUrl } from "@/services/tmdb";
import { Play, Plus, ThumbsUp, ChevronDown, Star, Tv, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";
import { useWebOSFocus } from "@/hooks/useWebOSFocus";
import { getFocusClasses, getWebOSProps } from "@/lib/webos-focus";
import { MediaTitle } from "../typography";
import { components } from "@/lib/api/types";

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
              ? media.backdrop_path || media.bannerImage || media.poster_path || media.coverImage
              : media.poster_path || media.coverImage,
            isSelected ? 'w780' : 'w500' // Higher quality for selected cards
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
          <div className="space-y-2 w-full">
            <h2 className={"text-lg font-black truncate "}>{media.title}</h2>
            
            {/* Enhanced metadata display */}
            <div className="flex items-center gap-3 text-xs">
              {/* Year */}
              {media.release_date && (
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3 text-purple-500" />
                  <span>{new Date(media.release_date).getFullYear()}</span>
                </div>
              )}
              
              {/* Rating - prefer AniList score, fallback to TMDB */}
              {(media.averageScore || media.vote_average > 0) && (
                <div className="flex items-center gap-1">
                  {media.averageScore ? (
                    <>
                      <Star className="h-3 w-3 text-yellow-500" />
                      <span className="font-medium">{media.averageScore}%</span>
                    </>
                  ) : (
                    <>
                      <ThumbsUp className="h-3 w-3 text-green-500" />
                      <span className="font-medium">{media.vote_average.toFixed(1)}</span>
                    </>
                  )}
                </div>
              )}
              
              {/* Episodes for anime */}
              {media.episodes && (
                <div className="flex items-center gap-1">
                  <Tv className="h-3 w-3 text-blue-500" />
                  <span>{media.episodes} eps</span>
                </div>
              )}
            </div>
            
            {/* Status for anime */}
            {media.status && (
              <div className="text-xs">
                <span className="px-2 py-1 bg-white/20 rounded text-white">
                  {media.status.toLowerCase()}
                </span>
              </div>
            )}

            {/* AniList Rankings */}
            {media.rankings && (
              <div className="flex flex-wrap gap-1 text-xs">
                {media.rankings.highestRated && (
                  <span className="px-2 py-1 bg-yellow-600/80 rounded text-white font-medium">
                    #{media.rankings.highestRated} Rated
                  </span>
                )}
                {media.rankings.mostPopular && (
                  <span className="px-2 py-1 bg-purple-600/80 rounded text-white font-medium">
                    #{media.rankings.mostPopular} Popular
                  </span>
                )}
              </div>
            )}
          </div>
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
