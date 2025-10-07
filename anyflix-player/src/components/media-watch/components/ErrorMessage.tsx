interface ErrorMessageProps {
  error: string;
  provider_url: string;
}

export const ErrorMessage = ({ error, provider_url }: ErrorMessageProps) => {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-5">
      <div className="text-center px-4 max-w-md pointer-events-auto">
        <div className="bg-red-500/20 backdrop-blur-sm rounded-lg p-6 border border-red-500/50 shadow-xl">
          <p className="text-red-500 text-lg font-semibold mb-2">
            Playback Error
          </p>
          <p className="text-white text-sm mb-4">{error}</p>
          <p className="text-white text-sm mb-4">{provider_url}</p>
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
