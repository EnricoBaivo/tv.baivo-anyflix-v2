import { useState } from "react";
import { Settings } from "lucide-react";
import { cn } from "@/lib/utils";
import { VideoSource, GroupedVideos } from "../types";

interface QualitySelectorProps {
  groupedVideos: GroupedVideos;
  selectedVideo: VideoSource;
  onVideoSelect: (video: VideoSource) => void;
}

export const QualitySelector = ({
  groupedVideos,
  selectedVideo,
  onVideoSelect,
}: QualitySelectorProps) => {
  const [showQualityMenu, setShowQualityMenu] = useState(false);

  const handleVideoSelect = (video: VideoSource) => {
    onVideoSelect(video);
    setShowQualityMenu(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowQualityMenu(!showQualityMenu)}
        className="flex items-center gap-2 text-white hover:text-gray-300 transition-colors px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg"
        aria-label="Quality settings"
      >
        <Settings className="w-5 h-5" />
        <span className="text-sm font-medium">Quality</span>
      </button>

      {showQualityMenu && (
        <div className="absolute bottom-full right-0 mb-2 bg-black/95 backdrop-blur-sm rounded-lg border border-white/10 shadow-2xl overflow-hidden min-w-[280px] max-h-[400px] overflow-y-auto">
          {Object.entries(groupedVideos).map(([lang, langVideos]) => (
            <div
              key={lang}
              className="border-b border-white/10 last:border-b-0"
            >
              <div className="px-4 py-2 bg-white/5 text-white/60 text-xs font-semibold uppercase tracking-wider">
                {lang === "EN"
                  ? "English"
                  : lang === "DE"
                  ? "German"
                  : lang}
              </div>
              {langVideos.map((video, idx) => (
                <button
                  key={`${video.url}-${idx}`}
                  onClick={() => handleVideoSelect(video)}
                  className={cn(
                    "w-full text-left px-4 py-3 text-sm transition-colors hover:bg-white/10",
                    selectedVideo.url === video.url
                      ? "bg-red-600/30 text-white font-medium"
                      : "text-white/80"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span>{video.quality}</span>
                    {selectedVideo.url === video.url && (
                      <span className="text-red-500">✓</span>
                    )}
                  </div>
                  <div className="text-xs text-white/50 mt-0.5">
                    {video.host.toUpperCase()} • {video.type}
                  </div>
                </button>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
