import { useEffect, useRef, useState } from "react";
import Hls from "hls.js";
import { VideoSource } from "../types";
import { getProxiedVideoUrl } from "@/lib/proxy";

export const useVideoPlayer = (
  selectedVideo: VideoSource,
  autoPlay: boolean,
  onNetworkFailure?: () => void
) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);
  const networkRetryCountRef = useRef(0);
  const maxNetworkRetries = 1;

  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [proxiedUrl, setProxiedUrl] = useState<string | null>(null);

  const videoUrl = proxiedUrl || selectedVideo?.url;
  const isHLS = videoUrl?.includes(".m3u8") || false;

  // Get proxied URL if needed
  useEffect(() => {
    if (!selectedVideo) return;

    let isMounted = true;

    async function fetchProxiedUrl() {
      try {
        const url = await getProxiedVideoUrl(selectedVideo);
        if (isMounted) {
          setProxiedUrl(url);
        }
      } catch (error) {
        console.error("Failed to get proxied URL:", error);
        if (isMounted) {
          setProxiedUrl(selectedVideo.url);
        }
      }
    }

    fetchProxiedUrl();

    return () => {
      isMounted = false;
    };
  }, [selectedVideo]);

  // Load and setup video source
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
    // Reset network retry counter when loading a new video
    networkRetryCountRef.current = 0;

    // If it's an HLS stream and the browser doesn't support it natively
    if (isHLS && Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: false,
        backBufferLength: 90,
        // Only set custom headers if not using proxy (proxy handles headers)
        xhrSetup: selectedVideo.headers && !selectedVideo.requires_proxy
          ? (xhr) => {
              Object.entries(selectedVideo.headers!).forEach(([key, value]) => {
                xhr.setRequestHeader(key, value);
              });
            }
          : undefined,
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
            case Hls.ErrorTypes.NETWORK_ERROR: {
              // Check if it's a CORS error or 403/401 error - these can't be fixed by retry
              const isManifestOrFragError = data.details === 'manifestLoadError' || 
                                            data.details === 'fragLoadError';
              const isCorsError = isManifestOrFragError && data.response?.code === 0;
              const isForbiddenError = data.response?.code === 403 || 
                                       data.response?.code === 401 ||
                                       data.response?.code === 404;
              
              // For CORS or auth errors, skip retries and switch quality immediately
              if (isCorsError || isForbiddenError) {
                const errorType = isCorsError ? 'CORS' : 
                                 data.response?.code === 404 ? 'Not Found' : 'Access Denied';
                console.log(`${errorType} error detected, switching quality immediately`);
                setError(`${errorType} error - switching to next quality`);
                setIsLoading(false);
                hls.destroy();
                
                if (onNetworkFailure) {
                  onNetworkFailure();
                }
              } else {
                // For other network errors, try to recover once
                networkRetryCountRef.current++;
                console.log(`Network error retry attempt: ${networkRetryCountRef.current}/${maxNetworkRetries}`);
                
                if (networkRetryCountRef.current <= maxNetworkRetries) {
                  setError("Network error - trying to recover");
                  hls.startLoad();
                } else {
                  console.log("Max network retries reached, attempting to switch quality");
                  setError("Network error - switching to next quality");
                  setIsLoading(false);
                  hls.destroy();
                  
                  // Call the callback to switch to next quality
                  if (onNetworkFailure) {
                    onNetworkFailure();
                  }
                }
              }
              break;
            }
            case Hls.ErrorTypes.MEDIA_ERROR:
              setError("Media error - trying to recover");
              hls.recoverMediaError();
              break;
            default:
              setError("Fatal error - cannot play video");
              setIsLoading(false);
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

      const handleError = (e: Event) => {
        const videoElement = e.target as HTMLVideoElement;
        const error = videoElement.error;
        
        // Check for CORS or network errors
        const isNetworkError = error?.code === MediaError.MEDIA_ERR_NETWORK;
        const shouldSkipRetry = isNetworkError;
        
        if (shouldSkipRetry) {
          console.log('Network/CORS error detected for video, switching quality immediately');
          setError("Network error - switching to next quality");
          setIsLoading(false);
          
          if (onNetworkFailure) {
            onNetworkFailure();
          }
        } else {
          networkRetryCountRef.current++;
          console.log(`Video load error, retry attempt: ${networkRetryCountRef.current}/${maxNetworkRetries}`);
          
          if (networkRetryCountRef.current <= maxNetworkRetries) {
            setError("Failed to load video - trying to recover");
            // Try to reload the video
            setTimeout(() => {
              video.load();
            }, 1000);
          } else {
            setError("Failed to load video - switching to next quality");
            setIsLoading(false);
            
            // Call the callback to switch to next quality
            if (onNetworkFailure) {
              onNetworkFailure();
            }
          }
        }
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
  }, [videoUrl, autoPlay, isHLS, selectedVideo.headers, selectedVideo.requires_proxy, onNetworkFailure]);

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

  return {
    videoRef,
    isPlaying,
    setIsPlaying,
    isLoading,
    error,
    currentTime,
    duration,
    volume,
    setVolume,
    isMuted,
    setIsMuted,
  };
};
