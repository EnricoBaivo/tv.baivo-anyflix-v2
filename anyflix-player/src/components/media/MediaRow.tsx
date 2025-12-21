import { useRef, useState, useEffect, useCallback, useMemo } from "react";
import MediaCard from "./MediaCard";
import { SectionTitle } from "../typography";
import MediaInfo from "./MediaInfo";
import MediaRowNavigationButton from "./MediaRowNavigationButton";
import { FocusZone } from "../navigation/FocusZone";
import type { MediaSpotlightCompat } from "@/lib/utils/mediaMapper";

// TV-optimized card dimensions (1920x1080 target)
// Netflix-style: Selected card is wider (16:9), unselected are narrower (2:3)
// Cards stay in original order, row scrolls to show selected card
const CARD_SIZES = {
  height: 270,                // Common height for all cards
  selected: { width: 480 },   // 16:9 aspect ratio for backdrop (wider)
  unselected: { width: 180 }, // 2:3 poster ratio (narrower)
  gap: 12,                    // Gap between cards
  padding: 48,                // TV safe area padding
} as const;

interface MediaRowProps {
  /** Unique ID for focus zone registration */
  id?: string;
  /** Row title displayed above cards */
  title: string;
  /** Media items to display */
  media: MediaSpotlightCompat[];
  /** Callback when media is clicked/selected */
  onMediaClick?: (media: MediaSpotlightCompat) => void;
  /** Focus zone priority (lower = higher priority) */
  priority?: number;
}

const MediaRow = ({ id, title, media, onMediaClick, priority = 0 }: MediaRowProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cardRefsRef = useRef<Map<number, HTMLButtonElement>>(new Map());
  const zoneId = id || `media-row-${title.toLowerCase().replace(/\s+/g, '-')}`;

  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  // PERFORMANCE FIX #2: Convert hover state to useRef to avoid re-renders
  // Hover state doesn't need to trigger React re-renders since MediaCard handles its own hover styles
  const hoveredIndexRef = useRef<number | null>(null);
  const [isRowHovered, setIsRowHovered] = useState<boolean>(false);

  const selectedMedia = media[selectedIndex];

  // Calculate scroll offset to align selected card with MediaInfo (48px padding)
  // Previous cards appear in the left gap, creating Netflix-style layout
  const scrollOffset = useMemo(() => {
    if (selectedIndex === 0) return 0;

    // Calculate total width of all cards before the selected one
    // All cards before selected are in unselected (narrower) state
    let offset = 0;
    for (let i = 0; i < selectedIndex; i++) {
      offset += CARD_SIZES.unselected.width + CARD_SIZES.gap;
    }
    // Add TV safe area padding to align selected card with MediaInfo
    // This creates a gap on the left showing part of the previous card
    return -offset + CARD_SIZES.padding;
  }, [selectedIndex]);

  // Register card ref for programmatic focus
  const setCardRef = useCallback((index: number, ref: HTMLButtonElement | null) => {
    if (ref) {
      cardRefsRef.current.set(index, ref);
    } else {
      cardRefsRef.current.delete(index);
    }
  }, []);

  // Navigate to a specific index and focus the element
  const navigateToIndex = useCallback((newIndex: number) => {
    if (newIndex < 0 || newIndex >= media.length) return;

    setSelectedIndex(newIndex);
    onMediaClick?.(media[newIndex]);

    // Use requestAnimationFrame to ensure element is rendered before focusing
    requestAnimationFrame(() => {
      const cardRef = cardRefsRef.current.get(newIndex);
      if (cardRef) {
        cardRef.focus();
      }
    });
  }, [media, onMediaClick]);

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
        navigateToIndex(newIndex);
      }
    },
    [selectedIndex, media.length, navigateToIndex]
  );

  // Handle keyboard events for index-based navigation (overrides spatial navigation)
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    // Only handle left/right arrow keys
    if (e.key === 'ArrowRight' || e.keyCode === 39) {
      e.preventDefault();
      e.stopPropagation();
      handleKeyNavigation('right');
    } else if (e.key === 'ArrowLeft' || e.keyCode === 37) {
      e.preventDefault();
      e.stopPropagation();
      handleKeyNavigation('left');
    }
  }, [handleKeyNavigation]);

  // PERFORMANCE FIX #8: Create stable memoized event handlers using data attributes
  // These handlers are created once and reused for all cards, preventing React.memo from breaking
  const handleCardMouseEnter = useCallback((e: React.MouseEvent<HTMLButtonElement>) => {
    const index = parseInt(e.currentTarget.dataset.index || '0', 10);
    hoveredIndexRef.current = index;
  }, []);

  const handleCardMouseLeave = useCallback(() => {
    hoveredIndexRef.current = null;
  }, []);

  const handleCardFocus = useCallback((e: React.FocusEvent<HTMLButtonElement>) => {
    const index = parseInt(e.currentTarget.dataset.index || '0', 10);
    // Only update selection if not already selected
    if (selectedIndex !== index) {
      setSelectedIndex(index);
      onMediaClick?.(media[index]);
    }
  }, [selectedIndex, media, onMediaClick]);

  const handleCardClick = useCallback((e: React.MouseEvent<HTMLButtonElement>) => {
    const index = parseInt(e.currentTarget.dataset.index || '0', 10);
    // Only update selection if not already selected
    if (selectedIndex !== index) {
      setSelectedIndex(index);
      onMediaClick?.(media[index]);
    }
  }, [selectedIndex, media, onMediaClick]);

  // Initialize first media as selected
  useEffect(() => {
    if (media.length > 0) {
      setSelectedIndex(0);
    }
  }, [media]);

  // Cleanup cardRefsRef Map when media array changes to prevent memory leak
  useEffect(() => {
    return () => {
      cardRefsRef.current.clear();
    };
  }, [media]);

  // Row height: card height + title + info section
  const rowHeight = CARD_SIZES.height + 140; // Extra space for title and info

  return (
    <div
      ref={containerRef}
      className="relative group focus:outline-none overflow-hidden"
      style={{
        height: `${rowHeight}px`,
        marginBottom: '3rem',
      }}
      onMouseEnter={() => setIsRowHovered(true)}
      onMouseLeave={() => setIsRowHovered(false)}
    >
      <SectionTitle
        className="mb-4"
        style={{ paddingLeft: `${CARD_SIZES.padding}px` }}
      >
        {title}
      </SectionTitle>

      <div className="relative overflow-hidden">
        {/* Left navigation button */}
        <MediaRowNavigationButton
          direction="left"
          onClick={() => handleKeyNavigation("left")}
          ariaLabel="Navigate to previous media"
          title="Navigate to previous media"
        />

        {/* Movies container - FocusZone with custom index-based navigation */}
        <FocusZone
          id={zoneId}
          type="row"
          priority={priority}
          rememberFocus
          navigationAxis="horizontal"
          className="overflow-hidden group-hover:opacity-100 opacity-90 transition-all duration-300"
          style={{ paddingLeft: `${CARD_SIZES.padding}px`, paddingRight: `${CARD_SIZES.padding}px` }}
        >
          {/* Wrapper div to capture keyboard events before spatial navigation */}
          <div onKeyDown={handleKeyDown}>
          <div
            className="flex items-stretch transition-transform duration-300 ease-out"
            style={{
              gap: `${CARD_SIZES.gap}px`,
              // Scroll offset to position selected card at left edge
              transform: `translateX(${scrollOffset}px)`,
            }}
          >
            {media.map((item, index) => {
              // Selected card is wider, others are narrower
              const isSelected = index === selectedIndex;
              const cardWidth = isSelected ? CARD_SIZES.selected.width : CARD_SIZES.unselected.width;

              return item?.id ? (
                <div
                  key={item.id}
                  className="flex-none transition-all duration-300 relative rounded-md overflow-hidden"
                  style={{
                    width: `${cardWidth}px`,
                    height: `${CARD_SIZES.height}px`,
                    zIndex: isSelected ? 50 : 10,
                    // Netflix-style border for selected card
                    border: isSelected ? '3px solid rgba(255, 255, 255, 0.8)' : '3px solid transparent',
                    boxShadow: isSelected ? '0 0 20px rgba(0, 0, 0, 0.8)' : 'none',
                    // Hardware acceleration
                    willChange: 'width',
                  }}
                >
                  <MediaCard
                    ref={(ref) => setCardRef(index, ref)}
                    media={item}
                    index={index}
                    isSelected={isSelected}
                    isHovered={hoveredIndexRef.current === index}
                    isAnyHovered={isRowHovered}
                    onMouseEnter={handleCardMouseEnter}
                    onMouseLeave={handleCardMouseLeave}
                    onFocus={handleCardFocus}
                    onClick={handleCardClick}
                  />
                </div>
              ) : null;
            })}
          </div>
          </div>
        </FocusZone>

        {/* Right navigation button */}
        <MediaRowNavigationButton
          direction="right"
          onClick={() => handleKeyNavigation("right")}
          ariaLabel="Navigate to next media"
          title="Navigate to next media"
        />
      </div>

      {/* Media Info Section - positioned below cards */}
      {selectedMedia && (
        <div style={{ paddingLeft: `${CARD_SIZES.padding}px`, marginTop: '1rem' }}>
          <MediaInfo media={selectedMedia} />
        </div>
      )}
    </div>
  );
};

export default MediaRow;
