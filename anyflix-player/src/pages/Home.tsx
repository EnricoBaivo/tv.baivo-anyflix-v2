/**
 * Home Page - WebOS TV Optimized
 *
 * Features:
 * - Horizontal scrolling MediaRow components with card expansion
 * - Spatial navigation with FocusZone and FocusableItem
 * - SWR data fetching for Popular and Latest Updates
 * - WebOS TV 6.x (Chromium 79) compatible
 * - Margin-based spacing (mr-8) instead of CSS gap
 * - Hardware acceleration for smooth scrolling
 * - Loading skeletons and error states
 *
 * Navigation:
 * - Arrow keys: Navigate between cards (left/right) and rows (up/down)
 * - Enter key: Select card and navigate to detail page
 * - Focus memory: Returns to last focused card in each row
 * - Priority-based row ordering: Row 0 (Popular) -> Row 1 (Latest)
 *
 * Architecture Analysis Compliance:
 * - Uses MediaRow component from components/media/MediaRow.tsx
 * - MediaRow wraps with FocusZone for spatial navigation
 * - MediaCard uses useWebOSFocus which integrates with FocusContext
 * - Card sizing: Unselected w-movie-md (300px), Selected w-movie-2xl (1200px)
 * - Auto-scrolling to keep selected card in view
 */

import { useMemo, useState } from "react";
import MediaRow from "../components/media/MediaRow";
import { usePopular, useLatest } from "../lib/api/hooks";
import { mapSearchResultsToMediaSpotlight } from "../lib/utils/mediaMapper";

// Loading skeleton for rows
const MediaRowSkeleton = ({ id }: { id: string }) => {
  return (
    <section className="mb-16">
      <div className="h-8 w-48 bg-gray-800 rounded mb-6 ml-8 animate-pulse" />
      <div className="flex overflow-x-auto pb-4 scrollbar-hide px-8">
        {[...Array(6)].map((_, i) => (
          <div
            key={`${id}-skeleton-${i}`}
            className="flex-shrink-0 w-[300px] h-[500px] mr-8 rounded-lg bg-gray-800 animate-pulse"
          />
        ))}
      </div>
    </section>
  );
};

// Error display component
const ErrorDisplay = ({ message }: { message: string }) => {
  return (
    <div className="flex items-center justify-center min-h-[200px] px-8">
      <div className="text-center">
        <p className="text-red-500 font-semibold mb-2">Error loading content</p>
        <p className="text-gray-400 text-sm">{message}</p>
      </div>
    </div>
  );
};

// Main Home Page Content Component
const HomeContent = () => {
  // Default source - can be made configurable later
  const [source] = useState("aniworld");

  // Fetch popular content
  const {
    data: popularData,
    error: popularError,
    isLoading: popularLoading,
  } = usePopular(source, 1);

  // Fetch latest updates
  const {
    data: latestData,
    error: latestError,
    isLoading: latestLoading,
  } = useLatest(source, 1);

  // Map API data to MediaSpotlightCompat format
  const popularItems = useMemo(() => {
    if (!popularData?.items) return [];
    return mapSearchResultsToMediaSpotlight(popularData.items);
  }, [popularData]);

  const latestItems = useMemo(() => {
    if (!latestData?.items) return [];
    return mapSearchResultsToMediaSpotlight(latestData.items);
  }, [latestData]);

  return (
    <div className="min-h-screen bg-background pt-20 pb-16 overflow-y-auto">
        {/* Page Title */}
        <div className="px-8 mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Home</h1>
          <p className="text-gray-400">
            Browse popular content and latest updates
          </p>
        </div>

        {/* Popular Row */}
        {popularLoading ? (
          <MediaRowSkeleton id="popular-skeleton" />
        ) : popularError ? (
          <ErrorDisplay message="Failed to load popular content" />
        ) : popularItems.length > 0 ? (
          <MediaRow
            id="popular-row"
            title="Popular"
            media={popularItems}
            priority={0}
          />
        ) : null}

        {/* Latest Updates Row */}
        {latestLoading ? (
          <MediaRowSkeleton id="latest-skeleton" />
        ) : latestError ? (
          <ErrorDisplay message="Failed to load latest updates" />
        ) : latestItems.length > 0 ? (
          <MediaRow
            id="latest-row"
            title="Latest Updates"
            media={latestItems}
            priority={1}
          />
        ) : null}

        {/* Empty State - when both are empty */}
        {!popularLoading &&
          !latestLoading &&
          popularItems.length === 0 &&
          latestItems.length === 0 && (
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <p className="text-gray-400 text-lg mb-2">No content available</p>
                <p className="text-gray-500 text-sm">
                  Please check your connection and try again
                </p>
              </div>
            </div>
          )}
    </div>
  );
};

// Main Home Page Component - uses FocusProvider from App.tsx
const Home = () => {
  return <HomeContent />;
};

export default Home;
