import { useLatest } from "@/lib/api/hooks";
import MediaRow from "./MediaRow";
import { mapSearchResultsToMediaSpotlight, type MediaSpotlightCompat } from "@/lib/utils/mediaMapper";

const LatestUpdateMediaRow = ({
  source,
  title,
  onMediaClick,
  page = 1,
}: {
  source: string;
  title: string;
  page?: number;
  onMediaClick: (media: MediaSpotlightCompat) => void;
}) => {
  const { data, error, isLoading } = useLatest(source, page ?? 1);
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
  if (error) {
    return <div>Error loading latest updates</div>;
  }
  if (!data?.items || data.items.length === 0) {
    return <div>No content found</div>;
  }
  
  // Map SearchResult[] to MediaSpotlightCompat[] for MediaRow compatibility
  const mappedMedia = mapSearchResultsToMediaSpotlight(data.items);
  
  return (
    <MediaRow
      title={title}
      media={mappedMedia}
      onMediaClick={onMediaClick}
    />
  );
};
export default LatestUpdateMediaRow;
