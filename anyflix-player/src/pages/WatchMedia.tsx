import VideoPlayer from "@/components/VideoPlayer";
import { useVideoSources } from "@/lib/api/hooks";
import { useSearchParams } from "react-router-dom";
import { Loader2 } from "lucide-react";

const WatchMedia = () => {
  const [searchParams] = useSearchParams();
  const mediaUrl = searchParams.get("url");
  const source = searchParams.get("src");
  const lang = searchParams.get("lang");
  
  const { data, isLoading, error } = useVideoSources(
    source || "",
    mediaUrl || "",
    lang || undefined
  );

  // Check for missing parameters first
  if (!mediaUrl || !source) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center px-4">
          <h1 className="text-2xl font-bold text-white mb-4">
            Missing Parameters
          </h1>
          <p className="text-gray-400 mb-6">
            Both 'url' and 'src' search parameters are required to play video.
          </p>
          <button
            onClick={() => window.history.back()}
            className="px-6 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-16 h-16 text-white animate-spin mx-auto mb-4" />
          <p className="text-white text-lg">Loading video sources...</p>
          <p className="text-gray-400 text-sm mt-2">Please wait</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center px-4 max-w-md">
          <div className="bg-red-500/20 rounded-lg p-6 border border-red-500/50">
            <h1 className="text-2xl font-bold text-red-500 mb-4">
              Error Loading Video
            </h1>
            <p className="text-white mb-4">
              {error instanceof Error ? error.message : "Failed to load video sources"}
            </p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Retry
              </button>
              <button
                onClick={() => window.history.back()}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Check if data exists and has videos
  if (!data || !data.videos || data.videos.length === 0) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center px-4">
          <h1 className="text-2xl font-bold text-white mb-4">
            No Video Sources Found
          </h1>
          <p className="text-gray-400 mb-6">
            No playable video sources are available for this media.
          </p>
          <button
            onClick={() => window.history.back()}
            className="px-6 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Render the video player with all available video sources
  return <VideoPlayer videos={data.videos} autoPlay={true} />;
};

export default WatchMedia;
