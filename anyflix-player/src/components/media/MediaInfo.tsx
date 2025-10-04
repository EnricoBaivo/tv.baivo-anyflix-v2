import { components } from "@/lib/api/types";
import { Badge } from "@/components/ui/badge";
import { MetadataText, DescriptionText, MediaTitle } from "../typography";

interface MediaInfoProps {
  media: components["schemas"]["MediaSpotlight"];
}

const MediaInfo = ({ media }: MediaInfoProps) => {
  // Use actual genres from media object with fallback
  const genres = media.genres || [];

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
      className="relative max-w-5xl h-48 ml-16 transition-all duration-700 ease-in-out animate-in fade-in slide-in-from-right-4"
    >
      {/* Media Info Section with Netflix-style typography */}
      <div className="absolute -top-4 left-0">
        <MediaTitle>{media.title}</MediaTitle>

        <MetadataText>
          <div className="flex items-center space-x-4 mb-2">
            {media.release_year && (
              <>
                <span>{media.release_year}</span>
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
            {media.best_ranking?.context === "highest Rated" && (
              <>
                <span>•</span>
                <span>#{media.best_ranking.rank} Rated</span>
              </>
            )}
            {media.media_status && (
              <>
                <span>•</span>
                <span className="capitalize">
                  {media.media_status.toLowerCase()}
                </span>
              </>
            )}
            {media.media_status && (
              <>
                <span>•</span>
                <span className="capitalize">
                  {media.seasons_count >= 1
                    ? `${media.seasons_count}seasons`
                    : `${media.episodes_count} episodes`}
                </span>
              </>
            )}
            {media.anilist_id && (
              <>
                <span>•</span>
                <a
                  href={`https://anilist.co/anime/${media.anilist_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  More Info
                </a>
              </>
            )}
            {media.tmdb_id && (
              <>
                <span>•</span>
                <a
                  href={`https://www.themoviedb.org/${media.media_source_type === "series" ? "tv" : "movie"}/${media.tmdb_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  More Info
                </a>
              </>
            )}
          </div>
        </MetadataText>
        <div>{media.provider_url}</div>
        {genres.length > 0 && (
          <MetadataText>
            <div className="flex items-center space-x-4 mb-6 flex-wrap">
              {genres.slice(0, 5).map((genre, index) => (
                <Badge
                  key={index}
                  variant="outline"
                  className="px-3 py-2 hover:bg-gray-500 text-sm font-medium"
                >
                  {genre}
                </Badge>
              ))}
            </div>
          </MetadataText>
        )}

        {media.description && (
          <DescriptionText>
            <span
              dangerouslySetInnerHTML={{
                __html: media.description.split("\n").at(0),
              }}
              className="line-clamp-3 block text-md"
            />
          </DescriptionText>
        )}
      </div>
    </div>
  );
};

export default MediaInfo;
