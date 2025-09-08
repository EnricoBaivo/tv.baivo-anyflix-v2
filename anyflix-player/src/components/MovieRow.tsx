import { useRef, useState } from 'react';
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
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);

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

  return (
    <div className="relative group mb-8">
      <h2 className="text-white text-xl font-bold mb-4 px-4">{title}</h2>
      <div className="relative">
        {/* Left scroll button */}
        <button
          onClick={() => scroll('left')}
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 text-white p-2 rounded-r-md opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-black/70"
        >
          <ChevronLeft className="h-6 w-6" />
        </button>

        {/* Movies container */}
        <div
          ref={scrollRef}
          className="flex space-x-4 overflow-x-auto scrollbar-hide px-4 py-2"
        >
          {movies.map((movie) => (
            <div 
              key={movie.id} 
              className={`flex-none transition-all duration-300 ${
                selectedMovie?.id === movie.id 
                  ? 'w-movie-xl h-movie-xl' 
                  : 'w-56 h-80'
              }`}
            >
              <MovieCard 
                movie={movie} 
                isSelected={selectedMovie?.id === movie.id}
                onClick={() => {
                  setSelectedMovie(selectedMovie?.id === movie.id ? null : movie);
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
        >
          <ChevronRight className="h-6 w-6" />
        </button>
      </div>
    </div>
  );
};

export default MovieRow;