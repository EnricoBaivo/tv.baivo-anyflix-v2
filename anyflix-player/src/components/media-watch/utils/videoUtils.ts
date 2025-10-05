import { VideoSource, GroupedVideos } from "../types";

export const groupVideosByLanguage = (videos: VideoSource[]): GroupedVideos => {
  const grouped: GroupedVideos = {};
  videos.forEach((video) => {
    const lang = video.language.toUpperCase();
    if (!grouped[lang]) {
      grouped[lang] = [];
    }
    grouped[lang].push(video);
  });
  return grouped;
};
