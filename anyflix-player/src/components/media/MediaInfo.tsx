import { Badge } from "@/components/ui/badge";
import { MetadataText, DescriptionText, MediaTitle } from "../typography";
import type { MediaSpotlightCompat } from "@/lib/utils/mediaMapper";

interface MediaInfoProps {
  media: MediaSpotlightCompat;
}

const MediaInfo = ({ media }: MediaInfoProps) => {
  // Use actual genres from media object with fallback (not available in SearchResult, so empty for now)
  const genres: string[] = [];

  // Determine content type and duration info
  const getContentInfo = () => {
    return "Series";
  };

  // Get rating info
  const getRatingInfo = () => {
    if (media.average_rating) {
      return `${media.average_rating}% Score`;
    }
    if (media.votes > 0) {
      return `${media.votes.toFixed(1)}/10 Rating`;
    }
    return null;
  };

  return (
    <div
      key={media.id}
      className="relative max-w-4xl transition-all duration-500 ease-in-out"
      style={{ paddingLeft: '48px', marginTop: '0.75rem' }}
    >
      {/* Netflix-style metadata - NO title (already on card) */}
      <MetadataText>
        <div className="flex items-center flex-wrap" style={{ gap: '0.75rem' }}>
          {media.release_year && (
            <span className="text-gray-300">{media.release_year}</span>
          )}
          {media.release_year && <span className="text-gray-500">•</span>}

          <span className="text-gray-300">{getContentInfo()}</span>

          {getRatingInfo() && (
            <>
              <span className="text-gray-500">•</span>
              <span className="text-gray-300">{getRatingInfo()}</span>
            </>
          )}

          {media.best_ranking?.context === "highest Rated" && (
            <>
              <span className="text-gray-500">•</span>
              <span className="text-yellow-500 font-medium">
                #{media.best_ranking.rank} Rated
              </span>
            </>
          )}

          {media.seasons_count && media.seasons_count >= 1 && (
            <>
              <span className="text-gray-500">•</span>
              <span className="text-gray-300">
                {media.seasons_count} {media.seasons_count === 1 ? 'Season' : 'Seasons'}
              </span>
            </>
          )}
        </div>
      </MetadataText>

      {genres.length > 0 && (
        <div className="flex items-center flex-wrap mt-3" style={{ gap: '0.5rem' }}>
          {genres.slice(0, 5).map((genre, index) => (
            <Badge
              key={index}
              variant="outline"
              className="px-3 py-1 text-sm font-medium text-gray-300 border-gray-600"
            >
              {genre}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
};

export default MediaInfo;
