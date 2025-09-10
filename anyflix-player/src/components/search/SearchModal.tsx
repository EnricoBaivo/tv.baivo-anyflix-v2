import { useState, useEffect, useRef, useCallback } from "react";
import { Media } from "@/types/media";
import { searchMovies } from "@/services/tmdb";
import MediaInfo from "../media/MediaInfo";
import SearchInput from "./SearchInput";
import MediaCard from "../media/MediaCard";
import { MediaTitle, MetadataText } from "../typography";

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SearchModal = ({ isOpen, onClose }: SearchModalProps) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Media[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [focusedCardIndex, setFocusedCardIndex] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      // Prevent body scroll when modal is open
      document.body.style.overflow = "hidden";
      if (inputRef.current) {
        inputRef.current.focus();
      }
    } else {
      // Restore body scroll when modal is closed
      document.body.style.overflow = "unset";
    }

    // Cleanup function to restore scroll on unmount
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;

    setLoading(true);
    setHasSearched(true);

    try {
      const response = await searchMovies(query);
      setResults(response.results);
    } catch (error) {
      console.error("Search error:", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [query]);

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
  }, [query, handleSearch]);

  const handleClose = () => {
    setQuery("");
    setResults([]);
    setHasSearched(false);
    setFocusedCardIndex(null);
    onClose();
  };

  const handleCardFocus = (index: number) => {
    setFocusedCardIndex(index);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed flex h-[calc(100vh)] w-full justify-center z-50 bg-background/95 backdrop-blur-sm">
      <div className="max-w-7xl mx-18 py-8">
        <SearchInput
          ref={inputRef}
          value={query}
          onChange={setQuery}
          onClose={handleClose}
        />

        {/*LoadingSearchResults */}
        <div className="max-h-[calc(100vh-200px)] overflow-y-auto scrollbar-hide">
          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <p className="text-white">Searching...</p>
            </div>
          )}

          {/* Search Query has no results */}
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

          {/* Search Query has results */}
          {!loading && results.length > 0 && (
            <div className="space-y-6">
              <div className="text-white text-lg">
                Showing results for "{query}"
              </div>

              <div className="grid px-2 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {results.map((media, index) => (
                  <div className="relative" key={media.id}>
                    <MediaCard 
                      media={media} 
                      index={index} 
                      onFocus={() => handleCardFocus(index)}
                    />
                    {focusedCardIndex === index && (
                      <div className="absolute bottom-0 left-0 right-0 p-6 text-white transition-opacity duration-300 opacity-1">
                        <MetadataText>{media.title}</MetadataText>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchModal;
