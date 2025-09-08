import { useRef, useState, useEffect, useCallback } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Movie } from '@/types/movie';
import MovieCard from './MovieCard';

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

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = 300;
      const newScrollPosition = direction === 'left' 
        ? scrollRef.current.scrollLeft - scrollAmount
        : scrollRef.current.scrollLeft + scrollAmount;
      
      scrollRef.current.scrollTo({
        left: newScrollPosition,
        behavior: 'smooth'
      });
    }
  };

  const scrollToSelected = (index: number) => {
    if (scrollRef.current && containerRef.current) {
      const cardWidth = 224; // w-56 = 224px (14rem = 224px)
      const gap = 16; // space-x-4 = 16px (1rem = 16px)
      const padding = 16; // px-4 = 16px padding on container
      const totalCardWidth = cardWidth + gap;
      // Calculate scroll position to align selected card flush-left with container padding
      const scrollPosition = (index * totalCardWidth) - padding;
      
      scrollRef.current.scrollTo({
        left: Math.max(0, scrollPosition), // Ensure we don't scroll to negative position
        behavior: 'smooth'
      });
    }
  };

  const handleKeyNavigation = useCallback((direction: 'left' | 'right') => {
    if (movies.length === 0) return;
    
    let newIndex = selectedIndex;
    if (direction === 'right' && selectedIndex < movies.length - 1) {
      newIndex = selectedIndex + 1;
    } else if (direction === 'left' && selectedIndex > 0) {
      newIndex = selectedIndex - 1;
    }
    
    if (newIndex !== selectedIndex) {
      setSelectedIndex(newIndex);
      setSelectedMovie(movies[newIndex]);
      scrollToSelected(newIndex);
      onMovieClick?.(movies[newIndex]);
    }
  }, [selectedIndex, movies, onMovieClick]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'ArrowRight') {
        event.preventDefault();
        handleKeyNavigation('right');
      } else if (event.key === 'ArrowLeft') {
        event.preventDefault();
        handleKeyNavigation('left');
      }
    };

    // Add event listener to the container or document
    const container = containerRef.current;
    if (container) {
      container.addEventListener('keydown', handleKeyDown);
      return () => container.removeEventListener('keydown', handleKeyDown);
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
      <div className="relative">
        {/* Left scroll button */}
        <button
          onClick={() => scroll('left')}
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 text-white p-2 rounded-r-md opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-black/70"
          aria-label="Scroll left"
          title="Scroll left"
        >
          <ChevronLeft className="h-6 w-6" />
        </button>

        {/* Movies container */}
        <div
          ref={scrollRef}
          className="flex space-x-4 overflow-x-auto scrollbar-hide px-4 py-2"
        >
          {movies.map((movie, index) => (
            <div 
              key={movie.id} 
              className={`flex-none transition-all duration-300 ${
                selectedIndex === index
                  ? 'w-movie-xl h-movie-xl' 
                  : 'w-56 h-80'
              }`}
            >
              <MovieCard 
                movie={movie} 
                isSelected={selectedIndex === index}
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
          onClick={() => scroll('right')}
          className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 text-white p-2 rounded-l-md opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-black/70"
          aria-label="Scroll right"
          title="Scroll right"
        >
          <ChevronRight className="h-6 w-6" />
        </button>
      </div>
    </div>
  );
};

export default MovieRow;