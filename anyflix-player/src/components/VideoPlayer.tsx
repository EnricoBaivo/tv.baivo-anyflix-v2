import { useEffect, useRef, useState, useCallback } from "react";
import Hls from "hls.js";
import { Play, Pause, Volume2, VolumeX, Maximize, Loader2, Settings, Minimize, SkipForward, SkipBack } from "lucide-react";
import { cn } from "@/lib/utils";
import { components } from "@/lib/api/types";
type VideoSource = components["schemas"]["VideoSource"];

interface VideoPlayerProps {
    videos: VideoSource [];
    autoPlay?: boolean;
    className?: string;
}

const VideoPlayer = ({
    videos,
    autoPlay = false,
    className,
}: VideoPlayerProps) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const hlsRef = useRef<Hls | null>(null);
    const progressBarRef = useRef<HTMLDivElement>(null);
    const controlsTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    
    const [selectedVideo, setSelectedVideo] = useState<VideoSource>(videos[0]);
    const [isPlaying, setIsPlaying] = useState(autoPlay);
    const [isMuted, setIsMuted] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showControls, setShowControls] = useState(true);
    const [showQualityMenu, setShowQualityMenu] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(1);
    const [isFullscreen, setIsFullscreen] = useState(false);

    const videoUrl = selectedVideo?.url;
    const isHLS = videoUrl?.includes(".m3u8") || false;

    useEffect(() => {
        const video = videoRef.current;
        if (!video || !videoUrl) {
            setError("No video URL provided");
            setIsLoading(false);
            return;
        }

        const currentTimeBeforeSwitch = video.currentTime;
        const wasPlaying = !video.paused;

        setError(null);
        setIsLoading(true);

        // If it's an HLS stream and the browser doesn't support it natively
        if (isHLS && Hls.isSupported()) {
            const hls = new Hls({
                enableWorker: true,
                lowLatencyMode: false,
                backBufferLength: 90,
                xhrSetup: selectedVideo.headers ? (xhr) => {
                    Object.entries(selectedVideo.headers!).forEach(([key, value]) => {
                        xhr.setRequestHeader(key, value);
                    });
                } : undefined,
            });

            hlsRef.current = hls;
            hls.loadSource(videoUrl);
            hls.attachMedia(video);

            hls.on(Hls.Events.MANIFEST_PARSED, () => {
                console.log("HLS manifest parsed");
                setIsLoading(false);
                
                // Restore playback position
                if (currentTimeBeforeSwitch > 0) {
                    video.currentTime = currentTimeBeforeSwitch;
                }
                
                if (autoPlay || wasPlaying) {
                    video.play().catch((err) => {
                        console.error("Autoplay failed:", err);
                        setIsPlaying(false);
                    });
                }
            });

            hls.on(Hls.Events.ERROR, (event, data) => {
                console.error("HLS error:", data);
                if (data.fatal) {
                    switch (data.type) {
                        case Hls.ErrorTypes.NETWORK_ERROR:
                            setError("Network error - trying to recover");
                            hls.startLoad();
                            break;
                        case Hls.ErrorTypes.MEDIA_ERROR:
                            setError("Media error - trying to recover");
                            hls.recoverMediaError();
                            break;
                        default:
                            setError("Fatal error - cannot play video");
                            hls.destroy();
                            break;
                    }
                }
            });

            return () => {
                if (hlsRef.current) {
                    hlsRef.current.destroy();
                    hlsRef.current = null;
                }
            };
        }
        // If it's a native supported format (MP4) or HLS is natively supported
        else if (video.canPlayType("application/vnd.apple.mpegurl") || !isHLS) {
            video.src = videoUrl;
            
            const handleLoadedData = () => {
                setIsLoading(false);
                
                // Restore playback position
                if (currentTimeBeforeSwitch > 0) {
                    video.currentTime = currentTimeBeforeSwitch;
                }
                
                if (autoPlay || wasPlaying) {
                    video.play().catch((err) => {
                        console.error("Autoplay failed:", err);
                        setIsPlaying(false);
                    });
                }
            };

            const handleError = () => {
                setError("Failed to load video");
                setIsLoading(false);
            };

            video.addEventListener("loadeddata", handleLoadedData);
            video.addEventListener("error", handleError);

            return () => {
                video.removeEventListener("loadeddata", handleLoadedData);
                video.removeEventListener("error", handleError);
                video.src = "";
            };
        } else {
            setError("HLS is not supported in this browser");
            setIsLoading(false);
        }
    }, [videoUrl, autoPlay, isHLS, selectedVideo.headers]);

    // Video event listeners
    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        const handleTimeUpdate = () => setCurrentTime(video.currentTime);
        const handleDurationChange = () => setDuration(video.duration);
        const handlePlay = () => setIsPlaying(true);
        const handlePause = () => setIsPlaying(false);
        const handleVolumeChange = () => {
            setVolume(video.volume);
            setIsMuted(video.muted);
        };

        video.addEventListener("timeupdate", handleTimeUpdate);
        video.addEventListener("durationchange", handleDurationChange);
        video.addEventListener("play", handlePlay);
        video.addEventListener("pause", handlePause);
        video.addEventListener("volumechange", handleVolumeChange);

        return () => {
            video.removeEventListener("timeupdate", handleTimeUpdate);
            video.removeEventListener("durationchange", handleDurationChange);
            video.removeEventListener("play", handlePlay);
            video.removeEventListener("pause", handlePause);
            video.removeEventListener("volumechange", handleVolumeChange);
        };
    }, []);

    // Fullscreen change listener
    useEffect(() => {
        const handleFullscreenChange = () => {
            setIsFullscreen(!!document.fullscreenElement);
        };

        document.addEventListener("fullscreenchange", handleFullscreenChange);
        return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
    }, []);

    // Auto-hide controls
    const resetControlsTimeout = useCallback(() => {
        if (controlsTimeoutRef.current) {
            clearTimeout(controlsTimeoutRef.current);
        }
        setShowControls(true);
        
        if (isPlaying) {
            controlsTimeoutRef.current = setTimeout(() => {
                setShowControls(false);
            }, 3000);
        }
    }, [isPlaying]);

    useEffect(() => {
        resetControlsTimeout();
        return () => {
            if (controlsTimeoutRef.current) {
                clearTimeout(controlsTimeoutRef.current);
            }
        };
    }, [isPlaying, resetControlsTimeout]);

    const togglePlay = () => {
        const video = videoRef.current;
        if (!video) return;

        if (video.paused) {
            video.play();
            setIsPlaying(true);
        } else {
            video.pause();
            setIsPlaying(false);
        }
    };

    const toggleMute = () => {
        const video = videoRef.current;
        if (!video) return;

        video.muted = !video.muted;
        setIsMuted(video.muted);
    };

    const toggleFullscreen = () => {
        const video = videoRef.current;
        if (!video) return;

        if (!document.fullscreenElement) {
            video.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    };

    const handleVolumeChange = (newVolume: number) => {
        const video = videoRef.current;
        if (!video) return;

        video.volume = newVolume;
        setVolume(newVolume);
        if (newVolume === 0) {
            setIsMuted(true);
        } else if (isMuted) {
            setIsMuted(false);
        }
    };

    const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
        const video = videoRef.current;
        const progressBar = progressBarRef.current;
        if (!video || !progressBar) return;

        const rect = progressBar.getBoundingClientRect();
        const pos = (e.clientX - rect.left) / rect.width;
        video.currentTime = pos * duration;
    };

    const skip = (seconds: number) => {
        const video = videoRef.current;
        if (!video) return;
        video.currentTime = Math.max(0, Math.min(duration, video.currentTime + seconds));
    };

    const formatTime = (seconds: number) => {
        if (isNaN(seconds)) return "0:00";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    const groupVideosByLanguage = () => {
        const grouped: Record<string, VideoSource[]> = {};
        videos.forEach((video) => {
            const lang = video.language.toUpperCase();
            if (!grouped[lang]) {
                grouped[lang] = [];
            }
            grouped[lang].push(video);
        });
        return grouped;
    };

    if (!videoUrl || videos.length === 0) {
        return (
            <div className={cn("flex items-center justify-center bg-black rounded-lg min-h-screen", className)}>
                <p className="text-white text-center">No video source available</p>
            </div>
        );
    }

    const groupedVideos = groupVideosByLanguage();
    const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

    return (
        <div
            className={cn("relative bg-black w-full h-screen overflow-hidden", className)}
            onMouseMove={resetControlsTimeout}
            onMouseLeave={() => isPlaying && setShowControls(false)}
        >
            <video
                ref={videoRef}
                className="w-full h-full object-contain"
                playsInline
                onClick={togglePlay}
            />

            {/* Loading Spinner */}
            {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-20">
                    <div className="text-center">
                        <Loader2 className="w-16 h-16 text-white animate-spin mx-auto mb-4" />
                        <p className="text-white text-sm">Loading video...</p>
                    </div>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/80 z-20">
                    <div className="text-center px-4 max-w-md">
                        <div className="bg-red-500/20 rounded-lg p-6 border border-red-500/50">
                            <p className="text-red-500 text-lg font-semibold mb-2">Playback Error</p>
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
            )}

            {/* Play/Pause Overlay (center) */}
            {!isPlaying && !isLoading && !error && (
                <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
                    <button
                        onClick={togglePlay}
                        className="bg-white/10 backdrop-blur-sm hover:bg-white/20 rounded-full p-8 transition-all pointer-events-auto"
                        aria-label="Play video"
                    >
                        <Play className="w-20 h-20 text-white fill-white" />
                    </button>
                </div>
            )}

            {/* Top Info Bar */}
            {!isLoading && !error && (
                <div
                    className={cn(
                        "absolute top-0 left-0 right-0 bg-gradient-to-b from-black/80 via-black/40 to-transparent p-6 transition-all duration-300 z-10",
                        showControls ? "translate-y-0 opacity-100" : "-translate-y-full opacity-0"
                    )}
                >
                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => window.history.back()}
                            className="text-white hover:text-gray-300 transition-colors text-2xl font-bold"
                        >
                            ←
                        </button>
                        <div className="text-white text-sm bg-black/50 px-3 py-1 rounded-full">
                            {selectedVideo.quality} • {selectedVideo.host.toUpperCase()}
                        </div>
                    </div>
                </div>
            )}

            {/* Bottom Controls */}
            {!isLoading && !error && (
                <div
                    className={cn(
                        "absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/80 to-transparent transition-all duration-300 z-10",
                        showControls ? "translate-y-0 opacity-100" : "translate-y-full opacity-0"
                    )}
                >
                    {/* Progress Bar */}
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

                    {/* Controls Row */}
                    <div className="px-6 pb-6">
                        <div className="flex items-center gap-4">
                            {/* Left Controls */}
                            <div className="flex items-center gap-3">
                                <button
                                    onClick={togglePlay}
                                    className="text-white hover:text-gray-300 transition-colors"
                                    aria-label={isPlaying ? "Pause" : "Play"}
                                >
                                    {isPlaying ? (
                                        <Pause className="w-8 h-8" />
                                    ) : (
                                        <Play className="w-8 h-8" />
                                    )}
                                </button>

                                <button
                                    onClick={() => skip(-10)}
                                    className="text-white hover:text-gray-300 transition-colors"
                                    aria-label="Skip backward 10 seconds"
                                >
                                    <SkipBack className="w-6 h-6" />
                                </button>

                                <button
                                    onClick={() => skip(10)}
                                    className="text-white hover:text-gray-300 transition-colors"
                                    aria-label="Skip forward 10 seconds"
                                >
                                    <SkipForward className="w-6 h-6" />
                                </button>

                                <div className="flex items-center gap-2 group/volume">
                                    <button
                                        onClick={toggleMute}
                                        className="text-white hover:text-gray-300 transition-colors"
                                        aria-label={isMuted ? "Unmute" : "Mute"}
                                    >
                                        {isMuted || volume === 0 ? (
                                            <VolumeX className="w-6 h-6" />
                                        ) : (
                                            <Volume2 className="w-6 h-6" />
                                        )}
                                    </button>
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.01"
                                        value={isMuted ? 0 : volume}
                                        onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                                        aria-label="Volume control"
                                        className="w-0 group-hover/volume:w-20 transition-all duration-200 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white"
                                    />
                                </div>

                                <div className="text-white text-sm font-medium">
                                    {formatTime(currentTime)} / {formatTime(duration)}
                                </div>
                            </div>

                            {/* Right Controls */}
                            <div className="flex-1" />
                            <div className="flex items-center gap-3">
                                {/* Quality Selector */}
                                <div className="relative">
                                    <button
                                        onClick={() => setShowQualityMenu(!showQualityMenu)}
                                        className="flex items-center gap-2 text-white hover:text-gray-300 transition-colors px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg"
                                        aria-label="Quality settings"
                                    >
                                        <Settings className="w-5 h-5" />
                                        <span className="text-sm font-medium">Quality</span>
                                    </button>

                                    {/* Quality Menu */}
                                    {showQualityMenu && (
                                        <div className="absolute bottom-full right-0 mb-2 bg-black/95 backdrop-blur-sm rounded-lg border border-white/10 shadow-2xl overflow-hidden min-w-[280px] max-h-[400px] overflow-y-auto">
                                            {Object.entries(groupedVideos).map(([lang, langVideos]) => (
                                                <div key={lang} className="border-b border-white/10 last:border-b-0">
                                                    <div className="px-4 py-2 bg-white/5 text-white/60 text-xs font-semibold uppercase tracking-wider">
                                                        {lang === "EN" ? "English" : lang === "DE" ? "German" : lang}
                                                    </div>
                                                    {langVideos.map((video, idx) => (
                                                        <button
                                                            key={`${video.url}-${idx}`}
                                                            onClick={() => {
                                                                setSelectedVideo(video);
                                                                setShowQualityMenu(false);
                                                            }}
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

                                <button
                                    onClick={toggleFullscreen}
                                    className="text-white hover:text-gray-300 transition-colors"
                                    aria-label={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
                                >
                                    {isFullscreen ? (
                                        <Minimize className="w-6 h-6" />
                                    ) : (
                                        <Maximize className="w-6 h-6" />
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default VideoPlayer;