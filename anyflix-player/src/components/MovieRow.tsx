import { useRef, useState, useEffect, useCallback } from "react";
import { ChevronLeft, ChevronRight, Play, Plus, ThumbsUp } from "lucide-react";
import { Movie } from "@/types/movie";
import MovieCard from "./MovieCard";

interface MovieRowProps {
  title: string;
  movies: Movie[];
  onMovieClick?: (movie: Movie) => void;
}

const MovieRow = ({ title, movies, onMovieClick }: MovieRowProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const scrollToSelected = (index: number) => {
    if (scrollRef.current && containerRef.current) {
      const unselectedWidth = 300; // w-movie-md = 300px
      const gap = 16; // space-x-4 = 16px (1rem = 16px)
      const padding = 16; // px-4 = 16px padding on container

      // Calculate cumulative width up to the target card
      // All cards before the target will be unselected (use unselectedWidth)
      let scrollPosition = 0;
      for (let i = 0; i < index; i++) {
        scrollPosition += unselectedWidth + gap;
      }

      // Subtract padding to align flush-left
      scrollPosition -= padding;

      scrollRef.current.scrollTo({
        left: Math.max(0, scrollPosition), // Ensure we don't scroll to negative position
        behavior: "smooth",
      });
    }
  };

  const handleKeyNavigation = useCallback(
    (direction: "left" | "right") => {
      if (movies.length === 0) return;

      let newIndex = selectedIndex;
      if (direction === "right" && selectedIndex < movies.length - 1) {
        newIndex = selectedIndex + 1;
      } else if (direction === "left" && selectedIndex > 0) {
        newIndex = selectedIndex - 1;
      }

      if (newIndex !== selectedIndex) {
        setSelectedIndex(newIndex);
        setSelectedMovie(movies[newIndex]);
        scrollToSelected(newIndex);
        onMovieClick?.(movies[newIndex]);
      }
    },
    [selectedIndex, movies, onMovieClick]
  );

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "ArrowRight") {
        event.preventDefault();
        handleKeyNavigation("right");
      } else if (event.key === "ArrowLeft") {
        event.preventDefault();
        handleKeyNavigation("left");
      }
    };

    // Add event listener to the container or document
    const container = containerRef.current;
    if (container) {
      container.addEventListener("keydown", handleKeyDown);
      return () => container.removeEventListener("keydown", handleKeyDown);
    }
  }, [handleKeyNavigation]);

  // Initialize first movie as selected
  useEffect(() => {
    if (movies.length > 0 && !selectedMovie) {
      setSelectedMovie(movies[0]);
      setSelectedIndex(0);
    }
  }, [movies, selectedMovie]);

  return (
    <div
      ref={containerRef}
      className="relative group mb-8 focus:outline-none"
      tabIndex={0}
    >
      <h2 className="text-white text-xl font-bold mb-4 px-4">{title}</h2>
      <div className="relative overflow-visible">
        {/* Left scroll button */}
        <button
          onClick={() => handleKeyNavigation("left")}
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 text-white p-2 rounded-r-md opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-black/70"
          aria-label="Navigate to previous movie"
          title="Navigate to previous movie"
        >
          <ChevronLeft className="h-6 w-6" />
        </button>

        {/* Movies container */}
        <div
          ref={scrollRef}
          className="flex space-x-4 overflow-x-auto overflow-y-visible scrollbar-hide px-4 py-8 group-hover:opacity-100 opacity-90 transition-all duration-300"
        >
          {movies.map((movie, index) => (
            <div
              key={movie.id}
              className={`flex-none transition-all duration-300 h-movie-2xl overflow-visible ${
                selectedIndex === index ? "w-movie-2xl" : "w-movie-md"
              }`}
            >
              <MovieCard
                movie={movie}
                isSelected={selectedIndex === index}
                isHovered={hoveredIndex === index}
                isAnyHovered={hoveredIndex !== null}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                onClick={() => {
                  setSelectedIndex(index);
                  setSelectedMovie(movie);
                  scrollToSelected(index);
                  onMovieClick?.(movie);
                }}
              />
            </div>
          ))}
        </div>

        {/* Right scroll button */}
        <button
          onClick={() => handleKeyNavigation("right")}
          className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 text-white p-2 rounded-l-md opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-black/70"
          aria-label="Navigate to next movie"
          title="Navigate to next movie"
        >
          <ChevronRight className="h-6 w-6" />
        </button>
      </div>

      {/* Movie Info Section - positioned below selected card */}

      {selectedMovie && (
        <div
          key={selectedMovie.id}
          className="px-4 transition-all duration-700 ease-in-out animate-in fade-in slide-in-from-right-4"
        >
          {/* // TODO: add correct movie info section */}
          <div className=" pl-8">
            <h3 className="text-white text-3xl font-bold mb-4 transition-all duration-300">
              {selectedMovie.title}
            </h3>
            <div className="flex items-center space-x-6 text-lg text-gray-300  transition-all duration-300">
              <span>{new Date(selectedMovie.release_date).getFullYear()}</span>
              <span>•</span>
              <span> staffeln oder film länge</span>
              <span>•</span>
              <span className="flex items-center">fsk 18</span>
            </div>
            <ol className="flex items-center space-x-2 text-lg text-gray-300 mb-6 transition-all duration-300">
              <li>fantasy</li>
              <li>action</li>
              <li>adventure</li>
            </ol>
            <p className="text-white text-lg line-clamp-3 mb-8 transition-all duration-300 text-wrap w-movie-2xl ">
              {selectedMovie.overview}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MovieRow;
