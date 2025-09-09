import { useState, useEffect, useRef } from 'react';
import { Search, X } from 'lucide-react';
import { Media } from '@/types/media';
import { searchMovies } from '@/services/tmdb';
import MediaCard from './MediaCard';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SearchModal = ({ isOpen, onClose }: SearchModalProps) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Media[]>([]);
  const [selectedMovie, setSelectedMovie] = useState<Media | null>(null);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (query.trim()) {
        handleSearch();
      } else {
        setResults([]);
        setHasSearched(false);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setHasSearched(true);
    
    try {
      const response = await searchMovies(query);
      setResults(response.results);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setQuery('');
    setResults([]);
    setSelectedMovie(null);
    setHasSearched(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-background/95 backdrop-blur-sm">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Search Header */}
        <div className="flex items-center space-x-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Titles, people, genres"
              className="w-full bg-gray-800 text-white pl-12 pr-4 py-4 text-xl border border-gray-600 rounded focus:outline-none focus:border-white transition-colors"
            />
          </div>
          <button
            onClick={handleClose}
            className="text-white hover:text-gray-300 transition-colors"
            aria-label="Close search modal"
            title="Close search modal"
          >
            <X className="h-8 w-8" />
          </button>
        </div>

        {/* Search Results */}
        <div className="max-h-[calc(100vh-200px)] overflow-y-auto scrollbar-hide">
          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <p className="text-white">Searching...</p>
            </div>
          )}

          {!loading && hasSearched && results.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">
                Your search for "{query}" did not have any matches.
              </p>
              <p className="text-gray-500 mt-2">Suggestions:</p>
              <ul className="text-gray-500 mt-2 space-y-1">
                <li>• Try different keywords</li>
                <li>• Looking for a movie or TV show?</li>
                <li>• Try using a movie, TV show title, or person</li>
              </ul>
            </div>
          )}

          {!loading && results.length > 0 && (
            <div className="space-y-6">
              <div className="text-white text-lg">
                Showing results for "{query}"
              </div>
              
              {(() => {
                const itemsPerRow = 4;
                const rows = [];
                let currentRow = [];
                let selectedMovieIndex = -1;
                
                // Find selected movie index
                if (selectedMovie) {
                  selectedMovieIndex = results.findIndex(movie => movie.id === selectedMovie.id);
                }
                
                for (let i = 0; i < results.length; i++) {
                  const movie = results[i];
                  
                  // If this is the selected movie, insert it in a new row
                  if (selectedMovie?.id === movie.id) {
                    // Add current row if it has items
                    if (currentRow.length > 0) {
                      rows.push(
                        <div key={`row-${rows.length}`} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-6">
                          {currentRow}
                        </div>
                      );
                      currentRow = [];
                    }
                    
                    // Add selected movie in its own row
                    rows.push(
                      <div key={`selected-${movie.id}`} className="mb-6">
                        <MediaCard 
                          media={movie}
                          index={0}
                          isSelected={true}
                          onClick={() => setSelectedMovie(null)}
                        />
                      </div>
                    );
                  } else {
                    // Add to current row
                    currentRow.push(
                      <MediaCard 
                        key={movie.id}
                        media={movie}
                        index={i}
                        isSelected={false}
                        onClick={() => setSelectedMovie(movie)}
                      />
                    );
                    
                    // If row is full, add it to rows
                    if (currentRow.length === itemsPerRow) {
                      rows.push(
                        <div key={`row-${rows.length}`} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-6">
                          {currentRow}
                        </div>
                      );
                      currentRow = [];
                    }
                  }
                }
                
                // Add remaining items in current row
                if (currentRow.length > 0) {
                  rows.push(
                    <div key={`row-${rows.length}`} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-6">
                      {currentRow}
                    </div>
                  );
                }
                
                return rows;
              })()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchModal;