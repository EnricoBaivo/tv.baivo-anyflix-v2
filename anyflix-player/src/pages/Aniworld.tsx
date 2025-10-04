import Hero from "@/components/Hero";
import MediaRow from "@/components/media/MediaRow";
import { useToast } from "@/hooks/use-toast";
import { usePopular, useLatest } from "@/lib/api/hooks";
import { components } from "@/lib/api/types";

const Aniworld = () => {
  const { toast } = useToast();
  const source = "aniworld"; // Using aniworld as the primary source

  // Fetch data from anime backend API
  const {
    data: popularMedia,
    error: popularError,
    isLoading: popularLoading,
  } = usePopular(source, 1);

  const {
    data: latestMedia,
    error: latestError,
    isLoading: latestLoading,
  } = useLatest(source, 1);

  // Handle errors
  if (popularError || latestError) {
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

  const handleMediaClick = (media: components["schemas"]["MediaSpotlight"]) => {
    console.log("Anime clicked:", media);
    // TODO: Navigate to anime detail page or open modal
  };

  if (popularLoading || latestLoading || !popularMedia || !latestMedia) {
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
      {popularMedia.list && <Hero media={popularMedia.list.at(0)} />}

      {/* Media Rows */}
      <div className="relative z-10 pb-16">
        {/* Default Content - only show when not searching */}
        <MediaRow
          title="Popular Anime"
          media={popularMedia.list.slice(1, -1)}
          onMediaClick={handleMediaClick}
        />

        <MediaRow
          title="Latest Episodes"
          media={latestMedia.list}
          onMediaClick={handleMediaClick}
        />
      </div>
    </div>
  );
};

export default Aniworld;
