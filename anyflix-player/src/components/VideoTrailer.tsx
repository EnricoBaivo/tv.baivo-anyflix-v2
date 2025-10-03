import { useMutate } from "@/lib/api/client";
import { useTrailerExtraction, useVideoSources } from "@/lib/api/hooks";
import { components } from "@/lib/api/types";
import { cn } from "@/lib/utils";
import { useCallback, useEffect, useRef, useState } from "react";

interface VideoTrailerProps {
  trailers: string[];
  clips: string[];
  teasers: string[];
}

export const VideoTrailer = ({
  trailers,
  clips,
  teasers,
}: VideoTrailerProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const { data: trailerExtraction } = useTrailerExtraction(
    [...trailers, ...clips, ...teasers].at(0)
  );
  useEffect(() => {
    console.log(trailerExtraction);
  }, [trailerExtraction]);

  useEffect(() => {
    const video = videoRef.current;
    if (trailerExtraction && video) {
      console.log(trailerExtraction);
      video.src = trailerExtraction.streamable_url;
      video.play();
      setPlaying(true);
    }
  }, [trailerExtraction]);

  return (
    <video
      ref={videoRef}
      className={cn(
        "w-full h-full object-cover origin-center transform-gpu absolute bottom-0 left-0 transition-opacity duration-300",
        playing ? "opacity-100" : "opacity-0"
      )}
    />
  );
};
