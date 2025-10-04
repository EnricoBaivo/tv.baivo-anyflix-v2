import { useSeriesDetail } from "@/lib/api/hooks";
import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { MediaTitle, SectionTitle } from "@/components/typography";
import { Button } from "@/components/ui/button";
import { Play, Info, ChevronDown } from "lucide-react";

const MediaDetail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const mediaUrl = searchParams.get("url");
  const source = searchParams.get("src");
  const [selectedSeason, setSelectedSeason] = useState(1);
  
  const { data, isLoading, error } = useSeriesDetail(source, mediaUrl);
  
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

  const currentSeason = data.series.seasons.find(
    (s) => s.season === selectedSeason
  ) || data.series.seasons[0];

  const handleEpisodeClick = (episodeUrl: string) => {
    navigate(`/watch?url=${encodeURIComponent(episodeUrl)}&src=${source}`);
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Hero Section */}
      <div className="relative h-[70vh] w-full">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent z-10" />
        <div className="absolute inset-0 bg-gradient-to-r from-background via-transparent to-transparent z-10" />
        
        {/* Content */}
        <div className="relative z-20 h-full flex flex-col justify-end p-8 md:p-16 lg:p-20">
          <div className="max-w-2xl space-y-6">
            <MediaTitle>{data.series.slug.split('-').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ')}</MediaTitle>
            
            <div className="flex items-center gap-4">
              <Button
                size="lg"
                className="bg-white text-black hover:bg-white/90 font-semibold px-8"
                onClick={() => {
                  if (currentSeason.episodes.length > 0) {
                    handleEpisodeClick(currentSeason.episodes[0].url);
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
              <span className="text-green-500 font-semibold">
                {data.series.seasons.length} Season{data.series.seasons.length > 1 ? 's' : ''}
              </span>
              <span>•</span>
              <span>{data.type.charAt(0).toUpperCase() + data.type.slice(1)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Episodes Section */}
      <div className="px-8 md:px-16 lg:px-20 mt-8 space-y-8">
        {/* Season Selector */}
        <div className="flex items-center gap-4">
          <SectionTitle className="mb-0">Episodes</SectionTitle>
          
          {data.series.seasons.length > 1 && (
            <div className="relative">
              <select
                value={selectedSeason}
                onChange={(e) => setSelectedSeason(Number(e.target.value))}
                aria-label="Select season"
                className="appearance-none bg-gray-800 text-white border border-gray-600 rounded px-6 py-2 pr-10 cursor-pointer hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-white"
              >
                {data.series.seasons.map((season) => (
                  <option key={season.season} value={season.season}>
                    {season.title}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
            </div>
          )}
        </div>

        {/* Episodes Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {currentSeason.episodes.map((episode, index) => (
            <button
              key={episode.url}
              onClick={() => handleEpisodeClick(episode.url)}
              className="group relative bg-gray-800 rounded-lg overflow-hidden hover:bg-gray-700 transition-all duration-300 hover:scale-105"
            >
              {/* Episode Number Badge */}
              <div className="aspect-video bg-gray-900 relative flex items-center justify-center">
                <span className="text-6xl font-bold text-gray-600 group-hover:text-gray-500 transition-colors">
                  {episode.episode}
                </span>
                
                {/* Play overlay on hover */}
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <div className="w-16 h-16 rounded-full border-2 border-white flex items-center justify-center">
                    <Play className="h-8 w-8 text-white fill-current ml-1" />
                  </div>
                </div>
              </div>
              
              {/* Episode Info */}
              <div className="p-4 space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-semibold text-white text-left line-clamp-1">
                    {episode.episode}. {episode.title}
                  </h3>
                  <span className="text-gray-400 text-sm whitespace-nowrap">
                    {/* Duration placeholder - add if available in data */}
                  </span>
                </div>
                
                {episode.tags && episode.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {episode.tags.map((tag, i) => (
                      <span
                        key={i}
                        className="text-xs text-gray-400 bg-gray-900 px-2 py-1 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MediaDetail;
