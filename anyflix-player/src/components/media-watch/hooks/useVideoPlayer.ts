import { useEffect, useRef, useState } from "react";
import Hls from "hls.js";
import { VideoSource } from "../types";

export const useVideoPlayer = (
  selectedVideo: VideoSource,
  autoPlay: boolean
) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);

  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);

  const videoUrl = selectedVideo?.url;
  const isHLS = videoUrl?.includes(".m3u8") || false;

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

    // If it's an HLS stream and the browser doesn't support it natively
    if (isHLS && Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: false,
        backBufferLength: 90,
        xhrSetup: selectedVideo.headers
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
