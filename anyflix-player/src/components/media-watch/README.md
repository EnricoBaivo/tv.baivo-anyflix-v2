# VideoPlayer Component

A modular, feature-rich video player component with episode navigation built with React best practices.

## Structure

```text
media-watch/
├── VideoPlayer.tsx                   # Main component orchestrator
├── index.ts                          # Public exports
├── types.ts                          # Shared TypeScript types
├── README.md                         # Documentation
├── hooks/                            # Custom React hooks
│   ├── useVideoPlayer.ts             # Video loading & HLS logic
│   ├── useVideoControls.ts           # Playback controls
│   ├── useControlsVisibility.ts      # Auto-hide controls
│   └── index.ts
├── components/                       # UI components
│   ├── ProgressBar.tsx               # Video progress bar
│   ├── VolumeControl.tsx             # Volume slider
│   ├── QualitySelector.tsx           # Quality/language selector
│   ├── LoadingSpinner.tsx            # Loading state
│   ├── ErrorMessage.tsx              # Error display
│   ├── PlayOverlay.tsx               # Center play button
│   ├── TopBar.tsx                    # Top info bar
│   ├── ControlBar.tsx                # Bottom controls
│   ├── EpisodeSelectorOverlay.tsx    # Episode selection overlay
│   ├── NextEpisodeButton.tsx         # Next episode button
│   └── index.ts
└── utils/                            # Helper functions
    └── videoUtils.ts                 # Video grouping utilities
```

## Features

### Core Features
- **HLS Streaming**: Full HLS.js integration with fallback support
- **Quality Switching**: Seamless quality changes without losing position
- **Multi-language**: Grouped quality selector by language
- **Custom Controls**: Modern, responsive video controls
- **Fullscreen**: Native fullscreen support
- **Keyboard Shortcuts**: Play/pause, skip, volume control
- **Auto-hide Controls**: Controls fade out during playback

### Episode Navigation (New!)
- **Episode List**: Full-screen overlay with all episodes
- **Season Selector**: Switch between seasons in overlay
- **Next Episode**: Quick button to jump to next episode
- **Auto-detect Next**: Automatically finds next episode (even across seasons)
- **Current Episode Highlight**: Shows which episode is playing

## Usage

### Basic Usage (Single Video)

```tsx
import { VideoPlayer } from "@/components/media-watch";

<VideoPlayer 
  videos={videoSources} 
  autoPlay={true} 
/>
```

### With Episode Navigation

```tsx
import { VideoPlayer } from "@/components/media-watch";
import { useNavigate } from "react-router-dom";

const navigate = useNavigate();

<VideoPlayer 
  videos={videoSources} 
  autoPlay={true}
  currentEpisode={episode}
  currentSeason={season}
  allSeasons={series.seasons}
  onEpisodeChange={(url, episode) => {
    navigate(`/watch?url=${encodeURIComponent(url)}&src=${source}`);
  }}
/>
```

## Props

### VideoPlayerProps

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `videos` | `VideoSource[]` | ✅ | Array of video sources |
| `autoPlay` | `boolean` | ❌ | Auto-play video on load |
| `className` | `string` | ❌ | Additional CSS classes |
| `currentEpisode` | `Episode` | ❌ | Current episode data |
| `currentSeason` | `Season` | ❌ | Current season data |
| `allSeasons` | `Season[]` | ❌ | All available seasons |
| `onEpisodeChange` | `(url: string, episode: Episode) => void` | ❌ | Callback when episode changes |

## New Components

### EpisodeSelectorOverlay

Full-screen overlay displaying all episodes with:
- Grid layout (2/3/4 columns responsive)
- Season switcher
- Current episode highlight
- Play button on hover
- Click anywhere to close

### NextEpisodeButton

Button in the control bar to jump to the next episode:
- Automatically determines next episode
- Works across seasons
- Hidden when no next episode exists
- Shows episode number on hover

## Integration Example

### In MediaDetail.tsx

When navigating from the detail page to the watch page, pass episode information:

```tsx
const handleEpisodeClick = (episodeUrl: string, episode: Episode) => {
  // Encode episode data in URL or use state
  navigate(
    `/watch?url=${encodeURIComponent(episodeUrl)}&src=${source}&episode=${episode.episode}&season=${currentSeason.season}`
  );
};
```

### In WatchMedia.tsx

Fetch series data and pass to VideoPlayer:

```tsx
import { VideoPlayer } from "@/components/media-watch";
import { useSeriesDetail, useVideoSources } from "@/lib/api/hooks";

const WatchMedia = () => {
  const [searchParams] = useSearchParams();
  const mediaUrl = searchParams.get("url");
  const source = searchParams.get("src");
  
  // Get video sources
  const { data: videoData } = useVideoSources(source, mediaUrl);
  
  // Get series data for episode navigation
  const { data: seriesData } = useSeriesDetail(source, seriesUrl);
  
  if (!videoData?.videos) return <Loading />;
  
  return (
    <VideoPlayer
      videos={videoData.videos}
      autoPlay={true}
      currentEpisode={currentEpisode}
      currentSeason={currentSeason}
      allSeasons={seriesData?.series.seasons}
      onEpisodeChange={(url, episode) => {
        navigate(`/watch?url=${encodeURIComponent(url)}&src=${source}`);
      }}
    />
  );
};
```

## Benefits

1. **Backwards Compatible**: Works with or without episode data
2. **Netflix-like UX**: Familiar episode selection interface
3. **Smart Navigation**: Auto-detects next episode across seasons
4. **Modular**: Each piece can be used independently
5. **Type-Safe**: Full TypeScript with OpenAPI types
6. **Accessible**: Proper ARIA labels and keyboard navigation

## Keyboard Shortcuts

- `Space`: Play/Pause
- `←`: Skip backward 10s
- `→`: Skip forward 10s
- `F`: Toggle fullscreen
- `M`: Toggle mute
- `Esc`: Close episode selector (when open)