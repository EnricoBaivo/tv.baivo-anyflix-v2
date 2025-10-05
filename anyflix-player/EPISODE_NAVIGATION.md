# Episode Navigation Integration Guide

This document explains how episode navigation works across the application.

## Overview

The episode navigation feature allows users to browse and switch between episodes while watching a video, similar to Netflix. It includes:
- Full-screen episode selector overlay
- Next episode button in video controls
- Automatic episode detection across seasons
- Seamless navigation with URL state management

## URL Parameters

### WatchMedia Page

The `/watch` route now accepts these parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `url` | ✅ | Episode video URL |
| `src` | ✅ | Source provider (e.g., "aniworld") |
| `lang` | ❌ | Language preference |
| `seriesUrl` | ❌ | Series base URL for fetching episode list |
| `episode` | ❌ | Current episode number |
| `season` | ❌ | Current season number |

### Example URLs

**Without episode navigation:**
```
/watch?url=https%3A%2F%2Fexample.com%2Fepisode1&src=aniworld
```

**With episode navigation:**
```
/watch?url=https%3A%2F%2Fexample.com%2Fepisode1&src=aniworld&seriesUrl=https%3A%2F%2Fexample.com%2Fseries&episode=1&season=1
```

## Component Flow

### 1. MediaDetail.tsx

The detail page shows all episodes and handles navigation to the watch page:

```tsx
const handleEpisodeClick = (episodeUrl: string, episode: Episode) => {
  const season = data.series.seasons.find((s) =>
    s.episodes.some((ep) => ep.url === episodeUrl)
  );

  const params = new URLSearchParams({
    url: episodeUrl,
    src: source || "",
    seriesUrl: mediaUrl || "",        // Pass series URL
    episode: episode.episode.toString(),
    season: season.season.toString(),
  });

  navigate(`/watch?${params.toString()}`);
};
```

### 2. WatchMedia.tsx

The watch page fetches both video sources and series data:

```tsx
// Fetch video sources
const { data } = useVideoSources(source, mediaUrl, lang);

// Fetch series data if seriesUrl is provided
const { data: seriesData } = useSeriesDetail(source, seriesUrl);

// Find current episode and season
const currentEpisode = useMemo(() => {
  if (!seriesData || !episodeNum || !seasonNum) return undefined;
  const season = seriesData.series.seasons.find(
    (s) => s.season === Number(seasonNum)
  );
  return season?.episodes.find((ep) => ep.episode === Number(episodeNum));
}, [seriesData, episodeNum, seasonNum]);

// Handle episode changes
const handleEpisodeChange = (episodeUrl: string, episode: Episode) => {
  const season = seriesData?.series.seasons.find((s) =>
    s.episodes.some((ep) => ep.url === episodeUrl)
  );

  const params = new URLSearchParams({
    url: episodeUrl,
    src: source || "",
    seriesUrl: seriesUrl || "",
    episode: episode.episode.toString(),
    season: season.season.toString(),
  });

  navigate(`/watch?${params.toString()}`);
};
```

### 3. VideoPlayer Component

The video player receives episode data and renders navigation controls:

```tsx
<VideoPlayer
  videos={data.videos}
  autoPlay={true}
  // Episode navigation props
  currentEpisode={currentEpisode}
  currentSeason={currentSeason}
  allSeasons={seriesData?.series.seasons}
  onEpisodeChange={handleEpisodeChange}
/>
```

## Features

### Episode Selector Overlay

- Opens when clicking "Episodes" button in control bar
- Shows grid of all episodes with:
  - Episode numbers
  - Episode titles
  - Current episode highlighted
  - Play button on hover
- Season switcher at the top
- Click anywhere to close

### Next Episode Button

- Automatically detects next episode
- Works across seasons (e.g., S1E12 → S2E1)
- Hidden when no next episode exists
- Quick one-click navigation

### Smart Episode Detection

The VideoPlayer automatically calculates the next episode:

```typescript
const nextEpisode = useMemo(() => {
  if (!currentEpisode || !currentSeason || !allSeasons) return null;

  const currentEpisodeIndex = currentSeason.episodes.findIndex(
    (ep) => ep.episode === currentEpisode.episode
  );

  // Check if there's a next episode in the current season
  if (currentEpisodeIndex < currentSeason.episodes.length - 1) {
    return currentSeason.episodes[currentEpisodeIndex + 1];
  }

  // Check if there's a next season
  const currentSeasonIndex = allSeasons.findIndex(
    (s) => s.season === currentSeason.season
  );
  if (currentSeasonIndex < allSeasons.length - 1) {
    const nextSeason = allSeasons[currentSeasonIndex + 1];
    return nextSeason.episodes[0] || null;
  }

  return null;
}, [currentEpisode, currentSeason, allSeasons]);
```

## Backwards Compatibility

The episode navigation is **completely optional**. The VideoPlayer works perfectly fine without episode data:

```tsx
// Works without episode navigation
<VideoPlayer videos={videoSources} autoPlay={true} />

// Works with episode navigation
<VideoPlayer
  videos={videoSources}
  autoPlay={true}
  currentEpisode={episode}
  currentSeason={season}
  allSeasons={seasons}
  onEpisodeChange={handleChange}
/>
```

When episode data is not provided:
- Episode selector button is hidden
- Next episode button is hidden
- Video player functions normally with quality controls

## Data Flow Diagram

```text
MediaDetail Page
    │
    ├─ User clicks episode
    │
    ├─ Navigate to /watch with params:
    │   • url (episode URL)
    │   • src (source)
    │   • seriesUrl (series base URL)
    │   • episode (number)
    │   • season (number)
    │
    ↓
WatchMedia Page
    │
    ├─ Fetch video sources (useVideoSources)
    ├─ Fetch series data (useSeriesDetail)
    │
    ├─ Calculate current episode
    ├─ Calculate current season
    │
    ├─ Pass to VideoPlayer
    │
    ↓
VideoPlayer Component
    │
    ├─ Calculate next episode
    ├─ Render episode controls
    │   • Episodes button → EpisodeSelectorOverlay
    │   • Next Episode button → handleNextEpisode
    │
    ├─ User changes episode
    │
    ├─ Call onEpisodeChange callback
    │
    ↓
WatchMedia Page
    │
    ├─ Navigate to new episode URL
    │
    └─ (Loop continues)
```

## API Hooks Used

### useSeriesDetail

Fetches complete series structure:

```typescript
const { data } = useSeriesDetail(source: string, url: string);

// Returns:
{
  series: {
    slug: string;
    seasons: [
      {
        season: number;
        title: string;
        episodes: [
          {
            episode: number;
            title: string;
            url: string;
            tags?: string[];
          }
        ];
      }
    ];
  };
  type: string;
}
```

### useVideoSources

Fetches video streaming links:

```typescript
const { data } = useVideoSources(source: string, url: string, lang?: string);

// Returns:
{
  videos: [
    {
      url: string;
      quality: string;
      host: string;
      language: string;
      type: string;
      headers?: Record<string, string>;
    }
  ];
}
```

## Testing the Feature

### Test Case 1: Watch without episode navigation
1. Navigate directly to `/watch?url=EPISODE_URL&src=SOURCE`
2. Video should play normally
3. Episode selector and next episode buttons should not appear

### Test Case 2: Watch with episode navigation
1. Go to a series detail page
2. Click on any episode
3. Video should play with episode controls visible
4. Click "Episodes" button to see episode grid
5. Click "Next Episode" to skip to next episode

### Test Case 3: Cross-season navigation
1. Watch the last episode of a season
2. "Next Episode" button should show
3. Click it to jump to first episode of next season
4. Episode selector should show new season

## Performance Considerations

- Series data is only fetched when `seriesUrl` is provided
- Episode calculations are memoized with `useMemo`
- URL parameters are properly encoded/decoded
- Only necessary data is passed to components

## Future Enhancements

Potential improvements:
- Auto-play next episode countdown (5 seconds)
- Episode progress tracking
- "Continue watching" from last episode
- Episode thumbnails in selector
- Keyboard shortcuts (N for next episode)
- Episode search/filter in overlay
