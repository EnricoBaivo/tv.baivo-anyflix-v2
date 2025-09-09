import { Movie } from "@/types/movie";
import { getImageUrl } from "@/services/tmdb";
import { Play, Plus, ThumbsUp, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface MovieCardProps {
  movie: Movie;
  isSelected?: boolean;
  isHovered?: boolean;
  isAnyHovered?: boolean;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  onClick?: () => void;
}

const MovieCard = ({
  movie,
  isSelected = false,
  isHovered = false,
  isAnyHovered = false,
  onMouseEnter,
  onMouseLeave,
  onClick,
}: MovieCardProps) => {
  return (
    <div
      className={cn(
        "cursor-pointer transition-transform duration-300 transform-gpu origin-center h-full flex flex-col",
        isSelected
          ? "movie-card-selected"
          : "movie-card group",
        isAnyHovered && !isHovered ? "scale-95" : "scale-100"
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
              ? movie.backdrop_path || movie.poster_path
              : movie.poster_path
          )}
          alt={movie.title}
          className="w-full h-full object-cover origin-center transform-gpu"
          loading="lazy"
        />
        {/* Gradient overlay - only for selected */}
        {!isSelected && (
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
        )}
        {/* Content overlay - only for selected */}
        {isSelected && (
          <div className="absolute bottom-0 left-0 right-0 p-8">
            <h3 className="text-white text-3xl font-bold mb-4">
              {movie.title}
            </h3>
            <div className="flex items-center space-x-6 text-lg text-gray-300 mb-6">
              <span>{new Date(movie.release_date).getFullYear()}</span>
              <span className="flex items-center">
                ⭐ {movie.vote_average.toFixed(1)}
              </span>
            </div>
            <p className="text-white text-lg line-clamp-3 mb-8">
              {movie.overview}
            </p>

            {/* Action buttons */}
            <div
              className="flex space-x-4"
              role="group"
              aria-label="Movie actions"
            >
              <button
                className="bg-white text-black rounded-lg px-8 py-3 text-lg font-semibold hover:bg-white/80 transition-colors duration-200 flex items-center space-x-2"
                aria-label={`Play ${movie.title}`}
                role="button"
                tabIndex={0}
                data-webos-focusable="true"
                data-webos-sound="true"
              >
                <Play className="h-6 w-6 fill-current" />
                <span>Play</span>
              </button>
              <button
                className="bg-gray-600/80 text-white rounded-full p-4 hover:bg-gray-500/80 transition-colors duration-200"
                aria-label={`Add ${movie.title} to watchlist`}
                role="button"
                tabIndex={0}
                data-webos-focusable="true"
                data-webos-sound="true"
              >
                <Plus className="h-6 w-6" />
              </button>
              <button
                className="bg-gray-600/80 text-white rounded-full p-4 hover:bg-gray-500/80 transition-colors duration-200"
                aria-label={`Like ${movie.title}`}
                role="button"
                tabIndex={0}
                data-webos-focusable="true"
                data-webos-sound="true"
              >
                <ThumbsUp className="h-6 w-6" />
              </button>
            </div>
          </div>
        )}
        <div
          className={cn(
            "flex flex-col items-start justify-between opacity-0 transition-opacity duration-300 absolute bottom-0 left-0 right-0 p-6 text-white",
            isHovered && !isSelected && "opacity-100"
          )}
        >
          <h2 className={"text-lg font-black truncate "}>{movie.title}</h2>
          <span>{new Date(movie.release_date).getFullYear()}</span>
        </div>
      </div>
    </div>
  );
};

export default MovieCard;
