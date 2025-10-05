import { useSeriesDetail } from "@/lib/api/hooks";
import { useState, useEffect, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { MediaTitle } from "@/components/typography";
import { Button } from "@/components/ui/button";
import { Play, Info, Tv, Film } from "lucide-react";
import { SeasonEpisodeSelector, Episode } from "@/components/media-detail";
import { useWebOSFocus } from "@/hooks/useWebOSFocus";
import { cn } from "@/lib/utils";

const MediaDetail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const mediaUrl = searchParams.get("url");
  const source = searchParams.get("src");
  const [selectedSeason, setSelectedSeason] = useState(1);
  const [contentType, setContentType] = useState<"series" | "movies">("series");

  const { data, isLoading, error } = useSeriesDetail(source, mediaUrl);

  // Prevent default scroll behavior when using arrow keys on the document level
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Prevent default scroll for arrow keys (37-40), let focus system handle navigation
      if ([37, 38, 39, 40].includes(e.keyCode)) {
        e.preventDefault();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Auto-switch to movies if no seasons available
  useEffect(() => {
    if (data && data.series.seasons && data.series.movies) {
      const hasSeasons = data.series.seasons.length > 0;
      const hasMovies = data.series.movies.length > 0;
      if (!hasSeasons && hasMovies) {
        setContentType("movies");
      }
    }
  }, [data]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-red-500 text-xl">
          Error: {JSON.stringify(error, null, 2)}
        </div>
      </div>
    );
  }

  if (!data || !mediaUrl || !source) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-white text-xl">
          {!data ? "No data" : "Missing Parameters"}
        </div>
      </div>
    );
  }

  const currentSeason =
    data.series.seasons?.find((s) => s.season === selectedSeason) ||
    data.series.seasons?.[0];

  const hasSeasons = data.series.seasons && data.series.seasons.length > 0;
  const hasMovies = data.series.movies && data.series.movies.length > 0;

  const handleEpisodeClick = (episodeUrl: string, episode: Episode) => {
    // Find which season this episode belongs to
    const season = data.series.seasons?.find((s) =>
      s.episodes.some((ep) => ep.url === episodeUrl)
    );

    if (!season) {
      console.error("Could not find season for episode");
      return;
    }

    // Navigate with all necessary parameters for episode navigation
    const params = new URLSearchParams({
      url: episodeUrl,
      src: source || "",
      seriesUrl: mediaUrl || "",
      episode: episode.episode.toString(),
      season: season.season.toString(),
    });

    navigate(`/watch?${params.toString()}`);
  };

  const handleMovieClick = (movieUrl: string) => {
    const params = new URLSearchParams({
      url: movieUrl,
      src: source || "",
      seriesUrl: mediaUrl || "",
    });

    navigate(`/watch?${params.toString()}`);
  };

  return (
    <div className="flex flex-col overflow-y-auto  h-[calc(100vh-80px)]  bg-background pb-20">
      {/* Hero Section */}
      <div className="relative h-[70vh] w-full">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent z-10" />
        <div className="absolute inset-0 bg-gradient-to-r from-background via-transparent to-transparent z-10" />

        {/* Content */}
        <div className="relative z-20 h-full flex flex-col justify-end p-8 md:p-16 lg:p-20">
          <div className="max-w-2xl space-y-6">
            <MediaTitle>
              {data.series.slug
                .split("-")
                .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                .join(" ")}
            </MediaTitle>

            <div className="flex items-center gap-4">
              <Button
                size="lg"
                className="bg-white text-black hover:bg-white/90 font-semibold px-8"
                onClick={() => {
                  if (currentSeason.episodes.length > 0) {
                    handleEpisodeClick(
                      currentSeason.episodes[0].url,
                      currentSeason.episodes[0]
                    );
                  }
                }}
              >
                <Play className="h-6 w-6 mr-2 fill-current" />
                Play
              </Button>
              <Button
                size="lg"
                variant="secondary"
                className="bg-gray-600/80 text-white hover:bg-gray-600/60 font-semibold px-8"
              >
                <Info className="h-6 w-6 mr-2" />
                More Info
              </Button>
            </div>

            <div className="flex items-center gap-3 text-gray-300 text-sm">
              {hasSeasons && (
                <>
                  <span className="text-green-500 font-semibold">
                    {data.series.seasons.length} Season
                    {data.series.seasons.length > 1 ? "s" : ""}
                  </span>
                  <span>•</span>
                </>
              )}
              {hasMovies && (
                <>
                  <span className="text-green-500 font-semibold">
                    {data.series.movies.length} Movie
                    {data.series.movies.length > 1 ? "s" : ""}
                  </span>
                  <span>•</span>
                </>
              )}
              <span>
                {data.type.charAt(0).toUpperCase() + data.type.slice(1)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="px-8 md:px-16 lg:px-20 mt-8 space-y-8">
        {/* Content Type Toggle (if both available) */}
        {hasSeasons && hasMovies && (
          <div className="flex gap-3">
            <ContentTypeToggle
              type="series"
              active={contentType === "series"}
              onClick={() => setContentType("series")}
              icon={<Tv className="h-5 w-5" />}
              label="Series"
            />
            <ContentTypeToggle
              type="movies"
              active={contentType === "movies"}
              onClick={() => setContentType("movies")}
              icon={<Film className="h-5 w-5" />}
              label="Movies"
            />
          </div>
        )}

        {/* Episodes or Movies Grid */}
        {contentType === "series" && hasSeasons && (
          <SeasonEpisodeSelector
            seasons={data.series.seasons}
            selectedSeason={selectedSeason}
            onSeasonChange={setSelectedSeason}
            onEpisodeClick={handleEpisodeClick}
          />
        )}

        {contentType === "movies" && hasMovies && (
          <MoviesGrid
            movies={data.series.movies}
            onMovieClick={handleMovieClick}
          />
        )}
      </div>
    </div>
  );
};

// Content Type Toggle Button Component
interface ContentTypeToggleProps {
  type: "series" | "movies";
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}

const ContentTypeToggle = ({
  active,
  onClick,
  icon,
  label,
}: ContentTypeToggleProps) => {
  const { ref, focusableProps, isFocused } = useWebOSFocus({
    onEnter: onClick,
  });

  return (
    <button
      ref={ref as React.RefObject<HTMLButtonElement>}
      {...focusableProps}
      onClick={onClick}
      className={cn(
        "flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200",
        active
          ? "bg-white text-black"
          : "bg-gray-800 text-white hover:bg-gray-700",
        isFocused &&
          !active &&
          "ring-2 ring-white ring-offset-2 ring-offset-background"
      )}
    >
      {icon}
      {label}
    </button>
  );
};

// Movies Grid Component
interface MoviesGridProps {
  movies: Array<{ number: number; title: string; url: string; kind: string }>;
  onMovieClick: (url: string) => void;
}

const MoviesGrid = ({ movies, onMovieClick }: MoviesGridProps) => {
  if (movies.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">No movies available</div>
    );
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Movies</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {movies.map((movie) => (
          <MovieCard
            key={movie.url}
            movie={movie}
            onClick={() => onMovieClick(movie.url)}
          />
        ))}
      </div>
    </div>
  );
};

// Movie Card Component
interface MovieCardProps {
  movie: { number: number; title: string; url: string; kind: string };
  onClick: () => void;
}

const MovieCard = ({ movie, onClick }: MovieCardProps) => {
  const { ref, focusableProps, isFocused } = useWebOSFocus({
    onEnter: onClick,
  });

  return (
    <button
      ref={ref as React.RefObject<HTMLButtonElement>}
      {...focusableProps}
      onClick={onClick}
      className={cn(
        "group relative bg-gray-800 rounded-lg overflow-hidden transition-all duration-300",
        "hover:bg-gray-700 hover:scale-105",
        isFocused && "scale-105 bg-gray-700"
      )}
    >
      {/* Movie Number Badge */}
      <div className="aspect-video bg-gray-900 relative flex items-center justify-center">
        <span className="text-6xl font-bold text-gray-600 group-hover:text-gray-500 transition-colors">
          {movie.number}
        </span>

        {/* Play overlay on hover */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <div className="w-16 h-16 rounded-full border-2 border-white flex items-center justify-center">
            <Play className="h-8 w-8 text-white fill-current ml-1" />
          </div>
        </div>
      </div>

      {/* Movie Info */}
      <div className="p-4">
        <h3 className="font-semibold text-white text-left line-clamp-2">
          {movie.title}
        </h3>
      </div>
    </button>
  );
};

export default MediaDetail;
