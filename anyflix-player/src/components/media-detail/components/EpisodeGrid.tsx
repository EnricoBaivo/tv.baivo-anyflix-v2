import { EpisodeCard } from "./EpisodeCard";
import { EpisodeGridProps } from "../types";

export const EpisodeGrid = ({
  episodes,
  onEpisodeClick,
}: EpisodeGridProps) => {
  if (episodes.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        No episodes available
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {episodes.map((episode) => (
        <EpisodeCard
          key={episode.url}
          episode={episode}
          onClick={() => onEpisodeClick(episode.url, episode)}
        />
      ))}
    </div>
  );
};
