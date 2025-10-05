import { cn } from "@/lib/utils";
import { VideoSource } from "../types";

interface TopBarProps {
  selectedVideo: VideoSource;
  showControls: boolean;
  onBack?: () => void;
}

export const TopBar = ({ selectedVideo, showControls, onBack }: TopBarProps) => {
  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      window.history.back();
    }
  };

  return (
    <div
      className={cn(
        "absolute top-0 left-0 right-0 bg-gradient-to-b from-black/80 via-black/40 to-transparent p-6 transition-all duration-300 z-10",
        showControls
          ? "translate-y-0 opacity-100"
          : "-translate-y-full opacity-0"
      )}
    >
      <div className="flex items-center justify-between">
        <button
          onClick={handleBack}
          className="text-white hover:text-gray-300 transition-colors text-2xl font-bold"
        >
          ←
        </button>
        <div className="text-white text-sm bg-black/50 px-3 py-1 rounded-full">
          {selectedVideo.quality} • {selectedVideo.host.toUpperCase()}
        </div>
      </div>
    </div>
  );
};
