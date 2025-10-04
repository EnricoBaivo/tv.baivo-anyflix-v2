import { usePopular } from "@/lib/api/hooks";
import MediaRow from "./MediaRow";
import { components } from "@/lib/api/types";

const PopularMediaRow = ({
  title,
  source,
  onMediaClick,
  page = 1,
}: {
  title: string;
  source: string;
  onMediaClick: (media: components["schemas"]["MediaSpotlight"]) => void;
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
  if (!data?.list || data.list.length === 0) {
    return <div>No content found</div>;
  }

  if (error) {
    return <div>Error loading popular media</div>;
  }
  return (
    <MediaRow title={title} media={data.list} onMediaClick={onMediaClick} />
  );
};

export default PopularMediaRow;
