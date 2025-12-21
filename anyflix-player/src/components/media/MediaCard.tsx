import React, { forwardRef, useImperativeHandle } from "react";
import {
  ThumbsUp,
  Star,
  Tv,
  Calendar,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useWebOSFocus } from "@/hooks/useWebOSFocus";
import { getFocusClasses, getWebOSProps } from "@/lib/webos-focus";
import { MediaTitle } from "../typography";
import { VideoTrailer } from "../VideoTrailer";
import { useNavigate } from "react-router-dom";
import type { MediaSpotlightCompat } from "@/lib/utils/mediaMapper";

interface MediaCardProps {
  media: MediaSpotlightCompat;
  index: number;
  isSelected?: boolean;
  isHovered?: boolean;
  isAnyHovered?: boolean;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  onFocus?: () => void;
  onClick?: () => void;
}

const MediaCard = React.memo(forwardRef<HTMLButtonElement, MediaCardProps>(({
  media,
  index,
  isSelected = false,
  isHovered = false,
  isAnyHovered = false,
  onMouseEnter,
  onMouseLeave,
  onFocus,
  onClick,
}, forwardedRef) => {
  const navigate = useNavigate();
  // WebOS focus handling - when focused, automatically becomes selected
  const { ref, focusableProps, isFocused, navigationMode } = useWebOSFocus({
    onFocus: onFocus, // Triggers selection when card receives focus
    onEnter: () => {
      onClick?.();
      // navigate to WatchMedia page
      console.log(media.provider_url, media.provider);
      navigate(
        `/media-detail?url=${
          media.provider_url
        }&src=${media.provider.toLowerCase()}`
      );
    }, // Triggers click action when Enter is pressed
  });

  // Combine refs: internal ref from useWebOSFocus and forwarded ref from parent
  useImperativeHandle(forwardedRef, () => ref.current as HTMLButtonElement);

  return (
    <button
      ref={ref}
      type="button"
      title={media.title}
      data-index={index}
      {...focusableProps}
      className={cn(
        focusableProps.className,
        "cursor-pointer transition-all duration-300 transform-gpu w-full h-full flex flex-col",
        "media-card group",
        !isSelected && isAnyHovered && !isHovered ? "scale-95" : "scale-100",
        isFocused && getFocusClasses("card", navigationMode)
      )}
      onFocus={(e) => {
        // Call focusableProps.onFocus first (for FocusContext)
        focusableProps.onFocus?.(e);
        // Then call parent's onFocus handler (for selection update)
        onFocus?.();
      }}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onClick={onClick}
    >
      <div
        className={cn(
          "relative overflow-hidden w-full h-full"
        )}
      >
        <img
          src={
            isSelected
              ? media.image_backdrop_url ?? media.image_cover_url
              : media.image_cover_url
          }
          alt={media.title}
          className="w-full h-full object-cover origin-center transform-gpu"
          loading="lazy"
        />
        {isFocused && media.trailers?.length > 0 && (
          <VideoTrailer
            trailers={media.trailers ?? []}
            clips={media.clips ?? []}
            teasers={media.teasers ?? []}
          />
        )}
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
            {/* Enhanced metadata display */}
            <div className="flex items-center gap-3 text-xs">
              {/* Year */}
              {media.release_year && (
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3 text-purple-500" />
                  <span>{media.release_year}</span>
                </div>
              )}

              {/* Rating - prefer AniList score, fallback to TMDB */}
              {(media.average_rating || media.votes > 0) && (
                <div className="flex items-center gap-1">
                  {media.average_rating ? (
                    <>
                      <Star className="h-3 w-3 text-yellow-500" />
                      <span className="font-medium">
                        {media.average_rating}%
                      </span>
                    </>
                  ) : (
                    <>
                      <ThumbsUp className="h-3 w-3 text-green-500" />
                      <span className="font-medium">
                        {media.votes.toFixed(1)}
                      </span>
                    </>
                  )}
                </div>
              )}

              {/* Episodes for anime */}
              {media.seasons_count && (
                <div className="flex items-center gap-1">
                  <Tv className="h-3 w-3 text-blue-500" />
                  <span>{media.seasons_count} eps</span>
                </div>
              )}
            </div>

            {/* Status for anime */}
            {media.media_status && (
              <div className="text-xs">
                <span className="px-2 py-1 bg-white/20 rounded text-white">
                  {media.media_status.toLowerCase()}
                </span>
              </div>
            )}

            {/* AniList Rankings */}
            {media.best_ranking && (
              <div className="flex flex-wrap gap-1 text-xs">
                {media.best_ranking.context === "highest Rated" && (
                  <span className="px-2 py-1 bg-yellow-600/80 rounded text-white font-medium">
                    #{media.best_ranking.rank} Rated
                  </span>
                )}
                {media.best_ranking.context === "most Popular" && (
                  <span className="px-2 py-1 bg-purple-600/80 rounded text-white font-medium">
                    #{media.best_ranking.rank} Popular
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
        {/* Title overlay - always visible for selected, hidden for others */}
        {isSelected && (
          <div className="absolute bottom-0 left-0 right-0 p-6 text-white bg-gradient-to-t from-black/80 via-black/40 to-transparent">
            {media.logo_urls?.length > 0 && media.logo_urls[0] ? (
              <img
                src={media.logo_urls[0]}
                alt={media.title}
                className="max-w-xs h-auto object-contain"
                style={{
                  filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.8))',
                }}
              />
            ) : (
              <h3 className="text-2xl md:text-3xl font-bold drop-shadow-lg">
                {media.title}
              </h3>
            )}
          </div>
        )}
      </div>
    </button>
  );
}), (prevProps, nextProps) => {
  // Custom comparison for better performance on TV hardware
  return (
    prevProps.media.id === nextProps.media.id &&
    prevProps.isSelected === nextProps.isSelected &&
    prevProps.isHovered === nextProps.isHovered &&
    prevProps.index === nextProps.index
  );
});

MediaCard.displayName = 'MediaCard';

export default MediaCard;
