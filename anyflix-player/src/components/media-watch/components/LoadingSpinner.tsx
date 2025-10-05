import { Loader2 } from "lucide-react";

export const LoadingSpinner = () => {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-20">
      <div className="text-center">
        <Loader2 className="w-16 h-16 text-white animate-spin mx-auto mb-4" />
        <p className="text-white text-sm">Loading video...</p>
      </div>
    </div>
  );
};
