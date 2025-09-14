import { Media } from "@/types/media";
import { Badge } from "@/components/ui/badge";
import { MetadataText, DescriptionText } from "../typography";

interface MediaInfoProps {
  media: Media;
}

const MediaInfo = ({ media }: MediaInfoProps) => {
  // Use actual genres from media object with fallback
  const genres = media.genres || [];
  
  // Determine content type and duration info
  const getContentInfo = () => {
    if (media.episodes) {
      return `${media.episodes} Episodes`;
    }
    if (media.dataSource === 'tmdb') {
      return media.video ? 'Movie' : 'Series';
    }
    return 'Series';
  };

  // Get rating info
  const getRatingInfo = () => {
    if (media.averageScore) {
      return `${media.averageScore}% Score`;
    }
    if (media.vote_average > 0) {
      return `${media.vote_average.toFixed(1)}/10 Rating`;
    }
    return null;
  };

  return (
    <div
      key={media.id}
      className="relative max-w-5xl h-48 ml-16 transition-all duration-700 ease-in-out animate-in fade-in slide-in-from-right-4"
    >
      {/* Media Info Section with Netflix-style typography */}
      <div className="absolute -top-4 left-0">
        <MetadataText>
          <div className="flex items-center space-x-4 mb-2">
            {media.release_date && (
              <>
                <span>{new Date(media.release_date).getFullYear()}</span>
                <span>•</span>
              </>
            )}
            <span>{getContentInfo()}</span>
            {getRatingInfo() && (
              <>
                <span>•</span>
                <span>{getRatingInfo()}</span>
              </>
            )}
            {(media.dataSource === 'anilist' || media.dataSource === 'hybrid') && media.rankings?.highestRated && (
              <>
                <span>•</span>
                <span>#{media.rankings.highestRated} Rated</span>
              </>
            )}
            {media.status && (
              <>
                <span>•</span>
                <span className="capitalize">{media.status.toLowerCase()}</span>
              </>
            )}
          </div>
        </MetadataText>
        
        {genres.length > 0 && (
          <MetadataText>
            <div className="flex items-center space-x-4 mb-6 flex-wrap">
              {genres.slice(0, 5).map((genre, index) => (
                <Badge 
                  key={index}
                  variant="secondary"
                  className="px-3 py-2 bg-gray-600 hover:bg-gray-500 text-sm font-medium"
                >
                  {genre}
                </Badge>
              ))}
            </div>
          </MetadataText>
        )}
        
        {media.overview && (
          <div className="mt-2">
            <DescriptionText>
              <span className="line-clamp-3 block">
                {media.overview}
              </span>
            </DescriptionText>
          </div>
        )}
      </div>
    </div>
  );
};

export default MediaInfo;
