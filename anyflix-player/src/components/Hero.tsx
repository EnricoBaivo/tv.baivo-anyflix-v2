import { Play, Info, Star } from "lucide-react";
import { BoldH1, MetadataText, SectionTitle } from "./typography";
import { components } from "@/lib/api/types";
import { useWebOSFocus } from "@/hooks/useWebOSFocus";
import { cn } from "@/lib/utils";
import { getFocusClasses } from "@/lib/webos-focus";
import { VideoTrailer } from "./VideoTrailer";

interface HeroProps {
  media: components["schemas"]["MediaSpotlight"];
}

const Hero = ({ media }: HeroProps) => {
  const { ref, focusableProps, isFocused, navigationMode } = useWebOSFocus({
    onFocus: () => {}, // Triggers selection when card receives focus
    onEnter: () => {}, // Triggers click action when Enter is pressed
  });
  return (
    <div
      ref={ref as React.RefObject<HTMLDivElement>}
      {...focusableProps}
      className={cn(
        focusableProps.className,
        "cursor-pointer transition-transform duration-300 transform-gpu origin-center h-full flex flex-col rounded-lg",
        isFocused && getFocusClasses("card", navigationMode),
        "relative flex flex-col justify-end mx-8 overflow-hidden rounded-3xl border border-white/10 mt-16 mb-8 min-h-[80vh] max-h-[85vh]"
      )}
    >
      {/* Background Image */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url(${media.image_backdrop_url}})`,
        }}
      />
      {isFocused && (
        <VideoTrailer
          trailers={media.trailers ?? []}
          clips={media.clips ?? []}
          teasers={media.teasers ?? []}
        />
      )}

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/50 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent" />

      {/* Content */}
      <div className="relative z-10  flex items-end">
        <div className="max-w-2xl px-4 sm:px-6 lg:px-12 pb-24">
          {/* Anyflix badge */}
          <div className="flex items-center space-x-2 mb-4">
            <span className="text-anyflix-red text-xl font-bold">A</span>
            <span className="text-white/80 text-sm uppercase tracking-wider">
              Series
            </span>
          </div>

          {/* Title */}
          {media.logo_urls && media.logo_urls.length > 0 ? (
            <>
              <img
                src={media.logo_urls.at(0)}
                alt={media.title}
                className="w-full max-w-96"
              />
              <MetadataText> {media.title}</MetadataText>
            </>
          ) : (
            <BoldH1> {media.title}</BoldH1>
          )}

          {/* Metadata */}
          <div className="flex items-center space-x-4 text-sm text-white mb-4">
            <span className="bg-red-600 text-white px-2 py-1 text-xs font-bold">
              `${media.average_rating || "N/A"}% Score`
            </span>
            <span className="flex items-center">
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400 mr-1" />
              {`Starring ${
                media.average_rating > 7 ? "Award Winners" : "Popular Actors  "
              }`}
            </span>
          </div>

          {/* AniList Rankings */}
          {media.best_ranking && (
            <div className="flex items-center space-x-4 text-sm text-white/90 mb-4">
              {media.best_ranking.context === "highest Rated" && (
                <span className="bg-yellow-600/80 text-white px-3 py-1 text-xs font-bold rounded">
                  #{media.best_ranking.rank} Highest Rated All Time
                </span>
              )}
              {media.best_ranking.context === "most Popular" && (
                <span className="bg-purple-600/80 text-white px-3 py-1 text-xs font-bold rounded">
                  #{media.best_ranking.rank} Most Popular All Time
                </span>
              )}
            </div>
          )}

          {/* Additional metadata */}
          <div className="flex items-center space-x-3 text-white/70 text-sm mb-6">
            {media.genres && (
              <span className="text-green-500 font-semibold">
                {media.genres.includes("Anime") ||
                media.genres.includes("animation")
                  ? "Anime"
                  : "Family Time TV"}
              </span>
            )}
            {media.release_year && (
              <>
                <span>•</span>
                <span>{media.release_year}</span>
              </>
            )}
            {media.media_status && (
              <>
                <span>•</span>
                <span className="capitalize">
                  {media.media_status.toLowerCase()}
                </span>
              </>
            )}
            {media.media_source_type && (
              <>
                <span>•</span>
                <span>{media.media_source_type}</span>
              </>
            )}
            <span>•</span>
            <span className="border border-white/50 px-2 py-0.5 text-xs">
              {media.media_format === "TV" ? "TV-MA" : "TV-PG"}
            </span>
          </div>

          {/* Description */}
          <p className="text-lg text-white/90 mb-8 leading-relaxed max-w-xl line-clamp-3">
            {media.description}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Hero;
