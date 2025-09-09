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
        isSelected ? "movie-card-selected" : "movie-card group",
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
