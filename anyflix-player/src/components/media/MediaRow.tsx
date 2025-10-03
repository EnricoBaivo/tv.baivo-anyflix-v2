import { useRef, useState, useEffect, useCallback } from "react";
// No longer need these imports as they're handled in NavigationButton
import { Media } from "@/types/media";
import MediaCard from "./MediaCard";
import { SectionTitle } from "../typography";
import MediaInfo from "./MediaInfo";
import MediaRowNavigationButton from "./MediaRowNavigationButton";
import { components } from "@/lib/api/types";

interface MediaRowProps {
  title: string;
  media: components["schemas"]["MediaSpotlight"][];
  onMediaClick?: (media: components["schemas"]["MediaSpotlight"]) => void;
}

const MediaRow = ({ title, media, onMediaClick }: MediaRowProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedMedia, setSelectedMedia] = useState<
    components["schemas"]["MediaSpotlight"] | null
  >(null);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [isRowHovered, setIsRowHovered] = useState<boolean>(false);

  // WebOS focus is now handled within NavigationButton components

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
      setSelectedMedia(media.at(0));
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
        {/* Left navigation button */}
        <MediaRowNavigationButton
          direction="left"
          onClick={() => handleKeyNavigation("left")}
          ariaLabel="Navigate to previous media"
          title="Navigate to previous media"
        />

        {/* Movies container - overflow-y must be visible for focus rings and hover effects */}
        <div
          ref={scrollRef}
          className="flex space-x-8 overflow-x-auto overflow-y-visible scrollbar-hide px-8 pt-6 pb-12 group-hover:opacity-100 opacity-90 transition-all duration-300"
        >
          {media.map((item, index) =>
            item?.id ? (
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
            ) : (
              <div className="text-white">{item?.id}</div>
            )
          )}
        </div>

        {/* Right navigation button */}
        <MediaRowNavigationButton
          direction="right"
          onClick={() => handleKeyNavigation("right")}
          ariaLabel="Navigate to next media"
          title="Navigate to next media"
        />
      </div>

      {/* Media Info Section - positioned below selected card */}
      {selectedMedia && <MediaInfo media={selectedMedia} />}
    </div>
  );
};

export default MediaRow;
