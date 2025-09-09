import { useRef, useState, useEffect, useCallback } from "react";
import { ChevronLeft, ChevronRight, Play, Plus, ThumbsUp } from "lucide-react";
import { Media } from "@/types/media";
import MediaCard from "./MediaCard";
import { getFocusClasses, getWebOSProps } from "@/lib/webos-focus";
import { useWebOSFocus } from "@/hooks/useWebOSFocus";
import { cn } from "@/lib/utils";
import {
  SectionTitle,
  MediaTitle,
  MetadataText,
  DescriptionText,
} from "./typography";

interface MediaRowProps {
  title: string;
  media: Media[];
  onMediaClick?: (media: Media) => void;
}

const MediaRow = ({ title, media, onMediaClick }: MediaRowProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedMedia, setSelectedMedia] = useState<Media | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [isRowHovered, setIsRowHovered] = useState<boolean>(false);

  // WebOS focus for navigation buttons
  const leftButtonFocus = useWebOSFocus({
    onEnter: () => handleKeyNavigation("left"),
  });

  const rightButtonFocus = useWebOSFocus({
    onEnter: () => handleKeyNavigation("right"),
  });

  const scrollToSelected = (index: number) => {
    if (scrollRef.current && containerRef.current) {
      const unselectedWidth = 300; // w-movie-md = 300px
      const gap = 32; // space-x-8 = 32px (2rem = 32px)
      const padding = 32; // px-8 = 32px padding on container

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
      if (media.length === 0) return;

      let newIndex = selectedIndex;
      if (direction === "right" && selectedIndex < media.length - 1) {
        newIndex = selectedIndex + 1;
      } else if (direction === "left" && selectedIndex > 0) {
        newIndex = selectedIndex - 1;
      }

      if (newIndex !== selectedIndex) {
        setSelectedIndex(newIndex);
        setSelectedMedia(media[newIndex]);
        scrollToSelected(newIndex);
        onMediaClick?.(media[newIndex]);
      }
    },
    [selectedIndex, media, onMediaClick]
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

  // Initialize first media as selected
  useEffect(() => {
    if (media.length > 0 && !selectedMedia) {
      setSelectedMedia(media[0]);
      setSelectedIndex(0);
    }
  }, [media, selectedMedia]);

  return (
    <div
      ref={containerRef}
      className="relative group mb-16 focus:outline-none overflow-visible"
      tabIndex={0}
      onMouseEnter={() => setIsRowHovered(true)}
      onMouseLeave={() => setIsRowHovered(false)}
    >
      <SectionTitle className="ml-8 mb-0">{title}</SectionTitle>
      <div className="relative overflow-visible">
        {/* Left scroll button */}
        <button
          {...leftButtonFocus.focusProps}
          {...getWebOSProps()}
          onClick={() => handleKeyNavigation("left")}
          className={cn(
            "absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 text-white p-2 rounded-r-md opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-black/70 focus:opacity-100",
            getFocusClasses("button", leftButtonFocus.navigationMode)
          )}
          aria-label="Navigate to previous movie"
          title="Navigate to previous movie"
        >
          <ChevronLeft className="h-6 w-6" />
        </button>

        {/* Movies container - overflow-y must be visible for focus rings and hover effects */}
        <div
          ref={scrollRef}
          className="flex space-x-8 overflow-x-auto overflow-y-visible scrollbar-hide px-8 py-12 group-hover:opacity-100 opacity-90 transition-all duration-300"
        >
          {media.map((item, index) => (
            <div
              key={item.id}
              className={`flex-none transition-all duration-300 overflow-visible relative ${
                selectedIndex === index
                  ? "w-movie-2xl h-movie-2xl"
                  : "w-movie-md h-movie-2xl"
              } ${
                hoveredIndex === index || selectedIndex === index
                  ? "z-50"
                  : "z-10"
              }`}
            >
              <MediaCard
                media={item}
                index={index}
                isSelected={selectedIndex === index}
                isHovered={hoveredIndex === index}
                isAnyHovered={isRowHovered}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                onFocus={() => {
                  setSelectedIndex(index);
                  setSelectedMedia(item);
                  scrollToSelected(index);
                  onMediaClick?.(item);
                }}
                onClick={() => {
                  setSelectedIndex(index);
                  setSelectedMedia(item);
                  scrollToSelected(index);
                  onMediaClick?.(item);
                }}
              />
            </div>
          ))}
        </div>

        {/* Right scroll button */}
        <button
          {...rightButtonFocus.focusProps}
          {...getWebOSProps()}
          onClick={() => handleKeyNavigation("right")}
          className={cn(
            "absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 text-white p-2 rounded-l-md opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-black/70 focus:opacity-100",
            getFocusClasses("button", rightButtonFocus.navigationMode)
          )}
          aria-label="Navigate to next media"
          title="Navigate to next media"
        >
          <ChevronRight className="h-6 w-6" />
        </button>
      </div>

      {/* Media Info Section - positioned below selected card */}

      {selectedMedia && (
        <div
          key={selectedMedia.id}
          className="relative max-w-5xl h-48 ml-16 transition-all duration-700 ease-in-out animate-in fade-in slide-in-from-right-4 "
        >
          {/* Movie Info Section with Netflix-style typography */}
          <div className="absolute -top-4 left-0  ">
            <MetadataText>
              <div className="flex items-center space-x-4 mb-2">
                <span>
                  {new Date(selectedMedia.release_date).getFullYear()}
                </span>
                <span>•</span>
                <span>Staffeln oder Film Länge</span>
                <span>•</span>
                <span className="flex items-center">FSK 18</span>
              </div>
            </MetadataText>
            <MetadataText>
              <div className="flex items-center space-x-4 mb-6  ">
                <span className="px-3 py-2 bg-gray-600 rounded-md text-sm font-medium">
                  Fantasy
                </span>
                <span className="px-3 py-2 bg-gray-600 rounded-md text-sm font-medium">
                  Action
                </span>
                <span className="px-3 py-2 bg-gray-600 rounded-md text-sm font-medium">
                  Adventure
                </span>
              </div>
            </MetadataText>
            <div className="mt-2">
              <DescriptionText>
                <span className="line-clamp-3 block">
                  {selectedMedia.overview}
                </span>
              </DescriptionText>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaRow;
