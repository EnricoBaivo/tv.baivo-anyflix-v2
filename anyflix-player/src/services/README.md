# Anime Backend Service Integration

## 🎯 Overview

This service integration connects your React frontend to the FastAPI anime backend using **SWR** for optimal caching and data fetching. The integration provides TypeScript-safe access to all anime sources, search, and streaming functionality.

## 📁 File Structure

```
src/
├── services/
│   ├── anime.ts          # Main service with SWR fetcher and URL generators
│   └── tmdb.ts           # Existing TMDB service
├── hooks/
│   └── useAnime.ts       # React hooks for anime data fetching
├── types/
│   └── anime.ts          # TypeScript types matching FastAPI models
└── components/
    └── AnimeDemo.tsx     # MVP demo component
```

## 🚀 Quick Start

### 1. Import and Use Hooks

```typescript
import { useSources, usePopular, useSeriesDetail } from '@/hooks/useAnime';

function MyComponent() {
  // Get available sources
  const { data: sources, isLoading, error } = useSources();
  
  // Get popular anime from a source
  const { data: popular } = usePopular('aniworld');
  
  // Get series details (hierarchical structure)
  const { data: series } = useSeriesDetail('aniworld', '/anime/attack-on-titan');
  
  return (
    <div>
      {/* Your UI here */}
    </div>
  );
}
```

### 2. Configure Backend URL

```typescript
import { updateAnimeServiceConfig } from '@/services/anime';

// Update backend URL if needed
updateAnimeServiceConfig({
  baseURL: 'http://your-backend-url:8000',
  timeout: 30000,
});
```

### 3. Use the Demo Component

```typescript
import AnimeDemo from '@/components/AnimeDemo';

function App() {
  return <AnimeDemo />;
}
```

## 🔧 Available Hooks

### Source Management
- `useSources()` - Get available anime sources
- `useSourcePreferences(source)` - Get source configuration

### Content Discovery
- `usePopular(source, params)` - Popular anime
- `useLatest(source, params)` - Latest updates
- `useSearch(source, searchParams)` - Search anime

### Hierarchical API (Modern)
- `useSeriesDetail(source, url)` - Complete series with seasons/movies
- `useSeriesSeasons(source, url)` - All seasons
- `useSeriesSeason(source, seasonNum, url)` - Specific season
- `useSeriesEpisode(source, seasonNum, episodeNum, url)` - Specific episode
- `useSeriesMovies(source, url)` - All movies/OVAs
- `useSeriesMovie(source, movieNum, url)` - Specific movie/OVA

### Video Sources
- `useVideoSources(source, url, lang?)` - Get video streaming links

### Utilities
- `useHealthCheck()` - Backend connectivity status
- `useAnimeOverview(source)` - Combined popular, latest, preferences
- `useAnimeSeries(source, url)` - Combined series, seasons, movies

## 🎨 SWR Benefits

- **Automatic Caching**: Responses are cached and shared across components
- **Background Revalidation**: Data stays fresh automatically
- **Error Handling**: Built-in error retry and recovery
- **Loading States**: Automatic loading state management
- **Deduplication**: Prevents duplicate requests
- **Optimistic Updates**: Fast UI updates with background sync

## 🔗 Backend Endpoints

The service connects to these FastAPI endpoints:

### Core Endpoints
- `GET /sources` - List available sources
- `GET /sources/{source}/preferences` - Source configuration
- `GET /sources/{source}/popular` - Popular anime
- `GET /sources/{source}/latest` - Latest updates
- `GET /sources/{source}/search` - Search anime

### Hierarchical API (Recommended)
- `GET /sources/{source}/series` - Series with seasons/movies
- `GET /sources/{source}/series/seasons` - All seasons
- `GET /sources/{source}/series/seasons/{season_num}` - Specific season
- `GET /sources/{source}/series/movies` - All movies/OVAs
- `GET /sources/{source}/videos` - Video streaming sources

### Legacy Endpoints (Deprecated)
- `GET /sources/{source}/detail` - Flat episode structure
- `GET /sources/{source}/episodes` - Legacy episodes endpoint

## 🛠️ Error Handling

The service includes comprehensive error handling:

```typescript
const { data, error, isLoading } = usePopular('aniworld');

if (error) {
  // Handle different error types
  if (error.statusCode === 404) {
    // Source not found
  } else if (error.statusCode === 0) {
    // Network/connection error
  }
}
```

## 🔧 Configuration

### SWR Configuration
```typescript
const { data } = usePopular('aniworld', {}, {
  refreshInterval: 60000, // Refresh every minute
  revalidateOnFocus: true,
  errorRetryCount: 5,
});
```

### Service Configuration
```typescript
import { updateAnimeServiceConfig } from '@/services/anime';

updateAnimeServiceConfig({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  retries: 3,
});
```

## 📊 TypeScript Support

All responses are fully typed with interfaces matching the FastAPI backend:

```typescript
interface SeriesDetailResponse {
  series: {
    slug: string;
    seasons: Season[];
    movies: Movie[];
  };
}

interface Season {
  season: number;
  title: string;
  episodes: Episode[];
}
```

## 🎮 WebOS TV Integration

The service works seamlessly with the existing webOS TV navigation system. All components using these hooks will automatically benefit from:

- **5-way navigation** support
- **Remote control** compatibility  
- **Focus management** integration
- **Back button** handling

## 🚀 Next Steps

1. **Replace TMDB calls** with anime backend calls in existing components
2. **Add video player integration** using the video sources endpoints
3. **Implement user preferences** with source configuration
4. **Add offline support** with SWR's built-in persistence
5. **Optimize performance** with selective data fetching

## 📝 Example Usage in Existing Components

Update your existing components to use the anime backend:

```typescript
// Before (TMDB)
import { getTrendingMovies } from '@/services/tmdb';

// After (Anime Backend)
import { usePopular } from '@/hooks/useAnime';

function Home() {
  const { data: popular, isLoading } = usePopular('aniworld');
  
  return (
    <div>
      {popular?.list.map(anime => (
        <MediaCard key={anime.link} media={anime} />
      ))}
    </div>
  );
}
```

---

**🎌 Ready to stream anime with your FastAPI backend!**
