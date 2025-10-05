interface ErrorMessageProps {
  error: string;
}

export const ErrorMessage = ({ error }: ErrorMessageProps) => {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-black/80 z-20">
      <div className="text-center px-4 max-w-md">
        <div className="bg-red-500/20 rounded-lg p-6 border border-red-500/50">
          <p className="text-red-500 text-lg font-semibold mb-2">
            Playback Error
          </p>
          <p className="text-white text-sm mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Reload Page
          </button>
        </div>
      </div>
    </div>
  );
};
