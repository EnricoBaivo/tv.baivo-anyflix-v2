import { Media } from "@/types/media";
import { Badge } from "@/components/ui/badge";
import { MetadataText, DescriptionText } from "./typography";

interface MediaInfoProps {
  media: Media;
}

const MediaInfo = ({ media }: MediaInfoProps) => {
  // Mock genres - in a real app, you'd get these from the media object or API
  const genres = ["Fantasy", "Action", "Adventure"];
  
  return (
    <div
      key={media.id}
      className="relative max-w-5xl h-48 ml-16 transition-all duration-700 ease-in-out animate-in fade-in slide-in-from-right-4"
    >
      {/* Media Info Section with Netflix-style typography */}
      <div className="absolute -top-4 left-0">
        <MetadataText>
          <div className="flex items-center space-x-4 mb-2">
            <span>{new Date(media.release_date).getFullYear()}</span>
            <span>•</span>
            <span>Staffeln oder Film Länge</span>
            <span>•</span>
            <span className="flex items-center">FSK 18</span>
          </div>
        </MetadataText>
        
        <MetadataText>
          <div className="flex items-center space-x-4 mb-6">
            {genres.map((genre, index) => (
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
        
        <div className="mt-2">
          <DescriptionText>
            <span className="line-clamp-3 block">
              {media.overview}
            </span>
          </DescriptionText>
        </div>
      </div>
    </div>
  );
};

export default MediaInfo;
