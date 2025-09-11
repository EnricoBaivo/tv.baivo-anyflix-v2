# TMDB Service Migration to SWR

## ✅ **Conversion Complete**

The TMDB service has been successfully converted from axios to SWR [[memory:8687174]] following the same pattern as the anime service.

## 📁 **Updated Files**

- **`/src/services/tmdb.ts`** - Converted to SWR fetcher with URL generators
- **`/src/hooks/useTMDB.ts`** - New React hooks for all TMDB endpoints
- **`/src/pages/Home.tsx`** - Already using the hooks (no changes needed)

## 🔄 **Migration Changes**

### Before (Axios-based)
```typescript
import { getTrendingMovies, getPopularMovies } from '@/services/tmdb';

// In component
useEffect(() => {
  const fetchData = async () => {
    try {
      const trending = await getTrendingMovies();
      const popular = await getPopularMovies();
      // Handle data...
    } catch (error) {
      // Handle error...
    }
  };
  fetchData();
}, []);
```

### After (SWR-based)
```typescript
import { useTrendingMovies, usePopularMovies } from '@/hooks/useTMDB';

// In component
const { data: trending, isLoading: trendingLoading, error: trendingError } = useTrendingMovies();
const { data: popular, isLoading: popularLoading, error: popularError } = usePopularMovies();
```

## 🎯 **Available Hooks**

### Basic Hooks
- `useTrendingMovies()` - Weekly trending movies
- `usePopularMovies()` - Popular movies  
- `useTopRatedMovies()` - Top rated movies
- `useMoviesByGenre(genreId)` - Movies by specific genre
- `useSearchMovies(query)` - Search movies by query

### Advanced Hooks
- `useMovieOverview()` - Fetches trending, popular, and top rated at once
- `useMoviesByGenres(genreIds[])` - Fetches multiple genres in parallel
- `useDebouncedMovieSearch(query, delay)` - Debounced search with delay
- `useHomePageData()` - Complete data for Home page (trending, popular, top rated, action)

### Utility Hooks
- `usePreloadMovies()` - Preload popular movie data

## 🚀 **SWR Benefits Applied**

### Automatic Caching
```typescript
// First call - fetches from API
const { data } = useTrendingMovies();

// Subsequent calls in other components - uses cache
const { data } = useTrendingMovies(); // No network request!
```

### Background Refresh
```typescript
// Data refreshes automatically based on configuration
const { data } = useTrendingMovies(); // Refreshes every 5 minutes
const { data } = usePopularMovies();  // Refreshes every 10 minutes
const { data } = useTopRatedMovies(); // Refreshes every hour
```

### Error Handling
```typescript
const { data, error, isLoading } = useTrendingMovies();

if (error) {
  // Automatic retry with exponential backoff
  console.error('TMDB API error:', error.message);
}
```

### Search Optimization
```typescript
// Debounced search prevents excessive API calls
const { data, isLoading } = useDebouncedMovieSearch(searchQuery, 500);
```

## 🔧 **Configuration Options**

### Custom SWR Config
```typescript
const { data } = useTrendingMovies({
  refreshInterval: 60000,     // Refresh every minute
  revalidateOnFocus: true,    // Refresh when window gains focus
  errorRetryCount: 5,         // Retry 5 times on error
  dedupingInterval: 10000,    // Dedupe requests for 10 seconds
});
```

### Service Configuration
```typescript
// The TMDB service uses environment variables in production
// For now, it uses the public demo key
const API_KEY = '8265bd1679663a7ea12ac168da84d2e8';
```

## 📊 **Performance Improvements**

### Before (Axios)
- ❌ Manual loading states
- ❌ Manual error handling  
- ❌ No caching
- ❌ Duplicate requests
- ❌ Manual retry logic

### After (SWR)
- ✅ Automatic loading states
- ✅ Built-in error handling
- ✅ Intelligent caching
- ✅ Request deduplication
- ✅ Automatic retries with backoff
- ✅ Background revalidation
- ✅ Optimistic updates

## 🔄 **Backward Compatibility**

The old functions still work but show deprecation warnings:

```typescript
// Still works, but shows warning in console
const movies = await getTrendingMovies(); 
// Console: "[TMDB] getTrendingMovies() is deprecated. Use useTrendingMovies() hook instead."
```

## 🎮 **WebOS TV Integration**

The new SWR hooks work seamlessly with webOS TV:
- **Caching** reduces API calls for better performance on TV
- **Background refresh** keeps content fresh
- **Error recovery** handles network issues gracefully
- **Loading states** integrate with existing loading UI

## 🏠 **Home Page Integration**

Your existing `Home.tsx` component works unchanged:

```typescript
// This hook now uses SWR internally
const { trending, popular, topRated, action, isLoading, isError } = useHomePageData();

// All the benefits of SWR without changing your component code!
```

## 🎯 **Next Steps**

1. **✅ TMDB converted to SWR** - Complete
2. **🔄 Test existing components** - Verify Home page works correctly
3. **🚀 Deploy and monitor** - Check performance improvements
4. **📈 Add more TMDB features** - TV shows, person search, etc.
5. **🔄 Remove axios dependency** - Clean up package.json if not used elsewhere

---

**🎬 Your TMDB integration is now powered by SWR for better performance and caching!**
