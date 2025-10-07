import { useEffect, useCallback } from "react";
import { useToast } from "@/hooks/use-toast";
import { components } from "@/lib/api/types";
import PopularMediaRow from "@/components/media/PopularMediaRow";
import LatestUpdateMediaRow from "@/components/media/LatestUpdateMediaRow";

const Aniworld = () => {
  const { toast } = useToast();
  const source = "aniworld"; // Using aniworld as the primary source

  const handleMediaClick = useCallback(
    (media: components["schemas"]["MediaSpotlight"]) => {
      console.log("Anime clicked:", media);
      // TODO: Navigate to anime detail page or open modal
    },
    []
  );

  return (
    <div className="min-h-screen bg-background overflow-y-auto">
      {/* Hero Section */}
      {/*       {popularMedia.list && <Hero media={popularMedia.list.at(0)} />}
       */}
      {/* Media Rows */}
      <div className="relative z-10 pb-16">
        <PopularMediaRow
          title="Lust auf mehr"
          source={source}
          onMediaClick={handleMediaClick}
          page={2}
        />
        {/* Default Content - only show when not searching */}
        <PopularMediaRow
          title="Richtig beliebt"
          source={source}
          onMediaClick={handleMediaClick}
          page={1}
        />
        <LatestUpdateMediaRow
          title="Frisch reingekommen"
          source={source}
          onMediaClick={handleMediaClick}
          page={1}
        />
      </div>
    </div>
  );
};

export default Aniworld;
