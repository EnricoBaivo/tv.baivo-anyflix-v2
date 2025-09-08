import { useEffect, useState } from "react";
import { Movie } from "@/types/movie";
import {
  getTrendingMovies,
  getPopularMovies,
  getTopRatedMovies,
  getMoviesByGenre,
} from "@/services/tmdb";
import Hero from "@/components/Hero";
import MovieRow from "@/components/MovieRow";
import { useToast } from "@/hooks/use-toast";

const Home = () => {
  const [heroMovie, setHeroMovie] = useState<Movie | null>(null);
  const [trendingMovies, setTrendingMovies] = useState<Movie[]>([]);
  const [popularMovies, setPopularMovies] = useState<Movie[]>([]);
  const [topRatedMovies, setTopRatedMovies] = useState<Movie[]>([]);
  const [actionMovies, setActionMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        setLoading(true);

        const [trending, popular, topRated, action] = await Promise.all([
          getTrendingMovies(),
          getPopularMovies(),
          getTopRatedMovies(),
          getMoviesByGenre(28), // Action genre ID
        ]);

        setTrendingMovies(trending.results);
        setPopularMovies(popular.results);
        setTopRatedMovies(topRated.results);
        setActionMovies(action.results);

        // Set hero movie to first trending movie
        if (trending.results.length > 0) {
          setHeroMovie(trending.results[0]);
        }
      } catch (error) {
        console.error("Error fetching movies:", error);
        toast({
          title: "Error",
          description: "Failed to load movies. Please try again later.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, [toast]);

  const handleMovieClick = (movie: Movie) => {
    console.log("Movie clicked:", movie);
    // TODO: Navigate to movie detail page or open modal
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
      {heroMovie && <Hero movie={heroMovie} />}

      {/* Movie Rows */}
      <div className="relative z-10 -mt-32 pb-16">
        <MovieRow
          title="Trending Now"
          movies={trendingMovies}
          onMovieClick={handleMovieClick}
        />

        <MovieRow
          title="Popular Movies"
          movies={popularMovies}
          onMovieClick={handleMovieClick}
        />

        <MovieRow
          title="Top Rated"
          movies={topRatedMovies}
          onMovieClick={handleMovieClick}
        />

        <MovieRow
          title="Action Movies"
          movies={actionMovies}
          onMovieClick={handleMovieClick}
        />
      </div>
    </div>
  );
};

export default Home;
