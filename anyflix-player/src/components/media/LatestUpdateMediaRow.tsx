import { useLatest } from "@/lib/api/hooks";
import { components } from "@/lib/api/types";
import MediaRow from "./MediaRow";

const LatestUpdateMediaRow = ({
  source,
  title,
  onMediaClick,
  page = 1,
}: {
  source: string;
  title: string;
  page?: number;
  onMediaClick: (media: components["schemas"]["MediaSpotlight"]) => void;
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
  return (
    <MediaRow
      title={title}
      media={data.list}
      onMediaClick={onMediaClick}
    />
  );
};
export default LatestUpdateMediaRow;
