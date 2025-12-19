import { usePopular } from "@/lib/api/hooks";
import MediaRow from "./MediaRow";
import { components } from "@/lib/api/types";
import { mapSearchResultsToMediaSpotlight, type MediaSpotlightCompat } from "@/lib/utils/mediaMapper";

const PopularMediaRow = ({
  title,
  source,
  onMediaClick,
  page = 1,
}: {
  title: string;
  source: string;
  onMediaClick: (media: MediaSpotlightCompat) => void;
  page?: number;
}) => {
  // Fetch data from anime backend API
  const { data, error, isLoading } = usePopular(source, page);
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading amazing anime content...</p>
        </div>
      </div>
    );
  }
  if (!data?.items || data.items.length === 0) {
    return <div>No content found</div>;
  }

  if (error) {
    return <div>Error loading popular media</div>;
  }
  
  // Map SearchResult[] to MediaSpotlightCompat[] for MediaRow compatibility
  const mappedMedia = mapSearchResultsToMediaSpotlight(data.items);
  
  return (
    <MediaRow title={title} media={mappedMedia} onMediaClick={onMediaClick} />
  );
};

export default PopularMediaRow;
