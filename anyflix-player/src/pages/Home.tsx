import { useEffect, useState } from "react";
import { Media } from "@/types/media";
import {
  getTrendingMovies,
  getPopularMovies,
  getTopRatedMovies,
  getMoviesByGenre,
} from "@/services/tmdb";
import Hero from "@/components/Hero";
import MediaRow from "@/components/media/MediaRow";
import { useToast } from "@/hooks/use-toast";

const Home = () => {
  const [heroMedia, setHeroMedia] = useState<Media | null>(null);
  const [trendingMedia, setTrendingMedia] = useState<Media[]>([]);
  const [popularMedia, setPopularMedia] = useState<Media[]>([]);
  const [topRatedMedia, setTopRatedMedia] = useState<Media[]>([]);
  const [actionMedia, setActionMedia] = useState<Media[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchMedia = async () => {
      try {
        setLoading(true);

        const [trending, popular, topRated, action] = await Promise.all([
          getTrendingMovies(),
          getPopularMovies(),
          getTopRatedMovies(),
          getMoviesByGenre(28), // Action genre ID
        ]);

        setTrendingMedia(trending.results);
        setPopularMedia(popular.results);
        setTopRatedMedia(topRated.results);
        setActionMedia(action.results);

        // Set hero media to first trending item
        if (trending.results.length > 0) {
          setHeroMedia(trending.results[0]);
        }
      } catch (error) {
        console.error("Error fetching media:", error);
        toast({
          title: "Error",
          description: "Failed to load media. Please try again later.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchMedia();
  }, [toast]);

  const handleMediaClick = (media: Media) => {
    console.log("Media clicked:", media);
    // TODO: Navigate to media detail page or open modal
  };

  if (loading) {
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
