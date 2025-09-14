import { useMemo } from "react";
import { Media, convertAnimeListToMedia } from "@/types/media";
import Hero from "@/components/Hero";
import MediaRow from "@/components/media/MediaRow";
import { useToast } from "@/hooks/use-toast";
import { usePopular, useLatest } from "@/lib/api/hooks";

const Aniworld = () => {
  const { toast } = useToast();
  const source = "aniworld"; // Using aniworld as the primary source

  // Fetch data from anime backend API
  const {
    data: popularData,
    error: popularError,
    isLoading: popularLoading,
  } = usePopular(source, 1);

  const {
    data: latestData,
    error: latestError,
    isLoading: latestLoading,
  } = useLatest(source, 1);

  // Combined loading and error states
  const isLoading = popularLoading || latestLoading;
  const isError = popularError || latestError;

  // Memoized data extraction using unified media converter
  const { heroMedia, popularMedia, latestMedia } = useMemo(() => {
    const popularList = popularData?.list || [];
    const latestList = latestData?.list || [];

    // Convert anime data to unified Media format
    const popularUnified = convertAnimeListToMedia(popularList);
    const latestUnified = convertAnimeListToMedia(latestList);

    return {
      heroMedia: popularUnified.length > 0 ? popularUnified[0] : null,
      popularMedia: popularUnified,
      latestMedia: latestUnified,
    };
  }, [popularData, latestData]);

  // Handle errors
  if (isError) {
    console.error("Error fetching anime data:", {
      popularError,
      latestError,
    });
    toast({
      title: "Error",
      description: "Failed to load anime content. Please try again later.",
      variant: "destructive",
    });
  }

  const handleMediaClick = (media: Media) => {
    console.log("Anime clicked:", media);
    console.log("Data source:", media.dataSource);
    console.log("Original data:", media.originalData);
    // TODO: Navigate to anime detail page or open modal
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading amazing anime content...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      {heroMedia && <Hero media={heroMedia} />}

      {/* Media Rows */}
      <div className="relative z-10 pb-16">
        {/* Default Content - only show when not searching */}
        <MediaRow
          title="Popular Anime"
          media={popularMedia}
          onMediaClick={handleMediaClick}
        />

        <MediaRow
          title="Latest Episodes"
          media={latestMedia}
          onMediaClick={handleMediaClick}
        />
      </div>
    </div>
  );
};

export default Aniworld;
