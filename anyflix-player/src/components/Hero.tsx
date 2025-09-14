import { Media } from "@/types/media";
import { getImageUrl } from "@/services/tmdb";
import { Play, Info, Star } from "lucide-react";
import { BoldH1 } from "./typography";

interface HeroProps {
  media: Media;
}

const Hero = ({ media }: HeroProps) => {
  return (
    <div className="relative flex flex-col justify-end mx-8 overflow-hidden rounded-3xl border border-white/10 mt-16 mb-8 min-h-[85vh]">
      {/* Background Image */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url(${getImageUrl(
            media.backdrop_path ||
              media.bannerImage ||
              media.poster_path ||
              media.coverImage,
            "original"
          )})`,
        }}
      />

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
          <BoldH1> {media.title}</BoldH1>

          {/* Metadata */}
          <div className="flex items-center space-x-4 text-sm text-white mb-4">
            <span className="bg-red-600 text-white px-2 py-1 text-xs font-bold">
              {media.dataSource === "anilist" || media.dataSource === "hybrid"
                ? `${media.averageScore || "N/A"}% Score`
                : `#${Math.floor(Math.random() * 10) + 1} in TV Shows`}
            </span>
            <span className="flex items-center">
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400 mr-1" />
              {media.dataSource === "anilist" || media.dataSource === "hybrid"
                ? `${media.episodes || "Unknown"} Episodes`
                : `Starring ${
                    media.vote_average > 7 ? "Award Winners" : "Popular Actors"
                  }`}
            </span>
          </div>

          {/* AniList Rankings */}
          {(media.dataSource === "anilist" || media.dataSource === "hybrid") &&
            media.rankings && (
              <div className="flex items-center space-x-4 text-sm text-white/90 mb-4">
                {media.rankings.highestRated && (
                  <span className="bg-yellow-600/80 text-white px-3 py-1 text-xs font-bold rounded">
                    #{media.rankings.highestRated} Highest Rated All Time
                  </span>
                )}
                {media.rankings.mostPopular && (
                  <span className="bg-purple-600/80 text-white px-3 py-1 text-xs font-bold rounded">
                    #{media.rankings.mostPopular} Most Popular All Time
                  </span>
                )}
              </div>
            )}

          {/* Additional metadata */}
          <div className="flex items-center space-x-3 text-white/70 text-sm mb-6">
            <span className="text-green-500 font-semibold">
              {media.dataSource === "anilist" || media.dataSource === "hybrid"
                ? "Anime"
                : "Family Time TV"}
            </span>
            {media.release_date && (
              <>
                <span>•</span>
                <span>{new Date(media.release_date).getFullYear()}</span>
              </>
            )}
            {media.status &&
              (media.dataSource === "anilist" ||
                media.dataSource === "hybrid") && (
                <>
                  <span>•</span>
                  <span className="capitalize">
                    {media.status.toLowerCase()}
                  </span>
                </>
              )}
            {!media.status && (
              <>
                <span>•</span>
                <span>Episodes</span>
              </>
            )}
            <span>•</span>
            <span className="border border-white/50 px-2 py-0.5 text-xs">
              {media.adult ? "TV-MA" : "TV-PG"}
            </span>
          </div>

          {/* Description */}
          <p className="text-lg text-white/90 mb-8 leading-relaxed max-w-xl line-clamp-3">
            {media.overview}
          </p>

          {/* Action Buttons */}
          <div className="flex items-center space-x-4">
            <button className="bg-white text-black px-8 py-3 rounded font-bold text-lg hover:bg-white/80 transition-colors duration-200 flex items-center space-x-2">
              <Play className="h-6 w-6 fill-current" />
              <span>Play</span>
            </button>

            <button className="bg-gray-600/70 text-white px-8 py-3 rounded font-bold text-lg hover:bg-gray-600/90 transition-colors duration-200 flex items-center space-x-2">
              <Info className="h-6 w-6" />
              <span>More Info</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
