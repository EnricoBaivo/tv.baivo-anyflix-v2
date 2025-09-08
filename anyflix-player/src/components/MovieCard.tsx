import { Movie } from "@/types/movie";
import { getImageUrl } from "@/services/tmdb";
import { Play, Plus, ThumbsUp, ChevronDown } from "lucide-react";

interface MovieCardProps {
  movie: Movie;
  isSelected?: boolean;
  onClick?: () => void;
}

const MovieCard = ({ movie, isSelected = false, onClick }: MovieCardProps) => {
  if (isSelected) {
    return (
      <div
        className="movie-card-selected cursor-pointer"
        onClick={onClick}
      >
        <div className="relative rounded-lg overflow-hidden h-full">
          <img
            src={getImageUrl(movie.backdrop_path || movie.poster_path)}
            alt={movie.title}
            className="w-full h-full object-cover origin-center transform-gpu"
            loading="lazy"
          />

          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

          {/* Content overlay */}
          <div className="absolute bottom-0 left-0 right-0 p-4">
            <h3 className="text-white text-lg font-bold mb-2">{movie.title}</h3>
            <div className="flex items-center space-x-4 text-sm text-gray-300 mb-3">
              <span>{new Date(movie.release_date).getFullYear()}</span>
              <span className="flex items-center">
                ⭐ {movie.vote_average.toFixed(1)}
              </span>
            </div>
            <p className="text-white text-sm line-clamp-2 mb-4">
              {movie.overview}
            </p>

            {/* Action buttons */}
            <div
              className="flex space-x-2"
              role="group"
              aria-label="Movie actions"
            >
              <button
                className="bg-white text-black rounded px-4 py-1 text-sm font-semibold hover:bg-white/80 transition-colors duration-200 flex items-center space-x-1"
                aria-label={`Play ${movie.title}`}
                role="button"
                tabIndex={0}
                data-webos-focusable="true"
                data-webos-sound="true"
              >
                <Play className="h-4 w-4 fill-current" />
                <span>Play</span>
              </button>
              <button
                className="bg-gray-600/80 text-white rounded-full p-2 hover:bg-gray-500/80 transition-colors duration-200"
                aria-label={`Add ${movie.title} to watchlist`}
                role="button"
                tabIndex={0}
                data-webos-focusable="true"
                data-webos-sound="true"
              >
                <Plus className="h-4 w-4" />
              </button>
              <button
                className="bg-gray-600/80 text-white rounded-full p-2 hover:bg-gray-500/80 transition-colors duration-200"
                aria-label={`Like ${movie.title}`}
                role="button"
                tabIndex={0}
                data-webos-focusable="true"
                data-webos-sound="true"
              >
                <ThumbsUp className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="movie-card group cursor-pointer h-full flex flex-col" onClick={onClick}>
      <div className="relative rounded-md overflow-hidden flex-1">
        <img
          src={getImageUrl(movie.poster_path)}
          alt={movie.title}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          loading="lazy"
        />

        {/* Hover overlay */}
        {/*  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
          <div className="flex space-x-2" role="group" aria-label="Movie actions">
            <button 
              className="bg-white text-black rounded-full p-2 hover:bg-white/80 transition-colors duration-200"
              aria-label={`Play ${movie.title}`}
              role="button"
              tabIndex={0}
              data-webos-focusable="true"
              data-webos-sound="true"
            >
              <Play className="h-4 w-4 fill-current" />
            </button>
            <button 
              className="bg-gray-600 text-white rounded-full p-2 hover:bg-gray-500 transition-colors duration-200"
              aria-label={`Add ${movie.title} to watchlist`}
              role="button"
              tabIndex={0}
              data-webos-focusable="true"
              data-webos-sound="true"
            >
              <Plus className="h-4 w-4" />
            </button>
            <button 
              className="bg-gray-600 text-white rounded-full p-2 hover:bg-gray-500 transition-colors duration-200"
              aria-label={`Like ${movie.title}`}
              role="button"
              tabIndex={0}
              data-webos-focusable="true"
              data-webos-sound="true"
            >
              <ThumbsUp className="h-4 w-4" />
            </button>
          </div>
        </div> */}
      </div>

      {/* Movie info */}
      <div className="p-3">
        <h3 className="text-white text-sm font-semibold truncate mb-1">
          {movie.title}
        </h3>
        <div className="flex items-center justify-between text-xs text-gray-400">
          {new Date(movie.release_date).getFullYear()}
        </div>
      </div>
    </div>
  );
};

export default MovieCard;
