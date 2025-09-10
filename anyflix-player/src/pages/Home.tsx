import { useMemo } from "react";
import { Media } from "@/types/media";
import { useHomePageData } from "@/hooks/useTMDB";
import Hero from "@/components/Hero";
import MediaRow from "@/components/media/MediaRow";
import { useToast } from "@/hooks/use-toast";

const Home = () => {
  const { toast } = useToast();
  const { trending, popular, topRated, action, isLoading, isError } = useHomePageData();

  // Memoized data extraction
  const { heroMedia, trendingMedia, popularMedia, topRatedMedia, actionMedia } = useMemo(() => {
    const trendingResults = trending.data?.results || [];
    const popularResults = popular.data?.results || [];
    const topRatedResults = topRated.data?.results || [];
    const actionResults = action.data?.results || [];

    return {
      heroMedia: trendingResults.length > 0 ? trendingResults[0] : null,
      trendingMedia: trendingResults,
      popularMedia: popularResults,
      topRatedMedia: topRatedResults,
      actionMedia: actionResults,
    };
  }, [trending.data, popular.data, topRated.data, action.data]);

  // Handle errors
  if (isError) {
    console.error("Error fetching media:", isError);
    toast({
      title: "Error",
      description: "Failed to load media. Please try again later.",
      variant: "destructive",
    });
  }

  const handleMediaClick = (media: Media) => {
    console.log("Media clicked:", media);
    // TODO: Navigate to media detail page or open modal
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading amazing content...</p>
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
        <MediaRow
          title="Trending Now"
          media={trendingMedia}
          onMediaClick={handleMediaClick}
        />

        <MediaRow
          title="Popular Movies"
          media={popularMedia}
          onMediaClick={handleMediaClick}
        />

        <MediaRow
          title="Top Rated"
          media={topRatedMedia}
          onMediaClick={handleMediaClick}
        />

        <MediaRow
          title="Action Movies"
          media={actionMedia}
          onMediaClick={handleMediaClick}
        />
      </div>
    </div>
  );
};

export default Home;
