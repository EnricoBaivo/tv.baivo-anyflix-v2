import { Play } from "lucide-react";

interface PlayOverlayProps {
  onPlay: () => void;
}

export const PlayOverlay = ({ onPlay }: PlayOverlayProps) => {
  return (
    <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
      <button
        onClick={onPlay}
        className="bg-white/10 backdrop-blur-sm hover:bg-white/20 rounded-full p-8 transition-all pointer-events-auto"
        aria-label="Play video"
      >
        <Play className="w-20 h-20 text-white fill-white" />
      </button>
    </div>
  );
};
