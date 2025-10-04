import { useEffect, useCallback } from "react";
import { useToast } from "@/hooks/use-toast";
import { components } from "@/lib/api/types";
import PopularMediaRow from "@/components/media/PopularMediaRow";
import LatestUpdateMediaRow from "@/components/media/LatestUpdateMediaRow";

const SerienStream = () => {
  const { toast } = useToast();
  const source = "serienstream"; // Using aniworld as the primary source

  const handleMediaClick = useCallback(
    (media: components["schemas"]["MediaSpotlight"]) => {
      console.log("SerienStream clicked:", media);
      // TODO: Navigate to anime detail page or open modal
    },
    []
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      {/*       {popularMedia.list && <Hero media={popularMedia.list.at(0)} />}
       */}
      {/* Media Rows */}
      <div className="relative z-10 pb-16">
        {/* Default Content - only show when not searching */}
        <PopularMediaRow
          title="Richtig beliebt"
          source={source}
          onMediaClick={handleMediaClick}
        />
        <LatestUpdateMediaRow
          title="Frisch reingekommen"
          source={source}
          onMediaClick={handleMediaClick}
        />
      </div>
    </div>
  );
};

export default SerienStream;
