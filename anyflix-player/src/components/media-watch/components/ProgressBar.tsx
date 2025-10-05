import { useRef } from "react";

interface ProgressBarProps {
  currentTime: number;
  duration: number;
  onSeek: (time: number) => void;
}

export const ProgressBar = ({
  currentTime,
  duration,
  onSeek,
}: ProgressBarProps) => {
  const progressBarRef = useRef<HTMLDivElement>(null);

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const progressBar = progressBarRef.current;
    if (!progressBar) return;

    const rect = progressBar.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    onSeek(pos * duration);
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="px-6 pb-2">
      <div
        ref={progressBarRef}
        onClick={handleProgressClick}
        className="h-1 bg-gray-600 rounded-full cursor-pointer group/progress hover:h-1.5 transition-all"
      >
        <div
          className="h-full bg-red-600 rounded-full relative group-hover/progress:bg-red-500 transition-colors"
          style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
        >
          <div
            className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-red-600 rounded-full opacity-0 group-hover/progress:opacity-100 transition-opacity"
            aria-hidden="true"
          />
        </div>
      </div>
    </div>
  );
};
