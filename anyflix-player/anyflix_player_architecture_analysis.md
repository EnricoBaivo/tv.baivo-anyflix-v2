---
name: Anyflix Player Architecture Analysis
overview: Comprehensive analysis document describing the styling, layout patterns, component structure, and design system of the Anyflix Player application
todos: []
---

# Anyflix Player

- Architecture & Design System Analysis

## Executive Summary

The Anyflix Player is a React-based streaming application designed for webOS TV platforms, featuring a Netflix-inspired dark theme UI with horizontal scrolling media rows, full-screen video playback, and TV-optimized navigation. The application uses Tailwind CSS with a custom design system, TypeScript for type safety, and React 18+ with modern hooks patterns.

## Design System & Styling

### Color Palette

The application uses a dark theme with a custom Anyflix color system defined in `index.css`:

- **Primary Red**: `hsl(0 100% 45%)` - Used for branding, buttons, and accents
- **Background**: `hsl(0 0% 8%)` - Deep black (`--anyflix-black`)
- **Dark Gray**: `hsl(0 0% 14%)` - Cards and elevated surfaces
- **Gray**: `hsl(0 0% 25%)` - Borders and secondary elements
- **Light Gray**: `hsl(0 0% 45%)` - Muted text and icons
- **White**: `hsl(0 0% 100%)` - Primary text

### Typography System

Custom typography components in `typography.tsx`:

- **BoldH1**: Large hero titles (4xl-7xl responsive)
- **MediaTitle**: Red-accented titles for media cards (xl-4xl)
- **SectionTitle**: Row section headers (lg-3xl)
- **MetadataText**: Gray secondary text (sm-lg)
- **DescriptionText**: White body text (sm-lg)

### Layout Patterns

#### 1. **Full-Screen Pages**

- All pages use `min-h-screen bg-background` for full viewport coverage
- Vertical scrolling enabled with `overflow-y-auto` where needed
- Fixed navbar at top (80px height) with backdrop blur

#### 2. **Horizontal Scrolling Rows**

The core browsing pattern uses horizontal scrolling media rows:

- **MediaRow Component**: Container with horizontal scroll
- **Card Sizing**: Dynamic width based on selection state
- Unselected: `w-movie-md` (300px)
- Selected: `w-movie-2xl` (1200px)
- **Smooth Scrolling**: Auto-scrolls to keep selected card in view
- **Navigation Buttons**: Left/right arrows for row navigation

#### 3. **Hero Sections**

- **MediaDetail Page**: 70vh hero section with gradient overlays
- **Gradient Overlays**: 
- Bottom gradient: `from-background via-background/60 to-transparent`
- Side gradient: `from-background via-transparent to-transparent`
- Content positioned at bottom with `justify-end`

#### 4. **Grid Layouts**

- **Search Results**: Responsive grid (1-5 columns based on screen size)
- **Episode Grid**: 1-3 columns (md:2, lg:3)
- **Movies Grid**: 1-3 columns with aspect-video cards

## Component Architecture

### Page Structure

```javascript
App.tsx
├── Navbar (fixed top, z-50)
└── Routes
    ├── Home.tsx (placeholder)
    ├── Aniworld.tsx (browse page)
    ├── SerienStream.tsx (browse page)
    ├── MediaDetail.tsx (detail page)
    ├── WatchMedia.tsx (video player page)
    └── Auth.tsx (authentication)
```



### Core Component Hierarchy

#### **Media Browsing Components**

```javascript
MediaRow (horizontal scroll container)
├── SectionTitle
├── MediaRowNavigationButton (left/right)
├── MediaCard[] (scrollable cards)
│   ├── Image (cover/backdrop based on selection)
│   ├── VideoTrailer (on focus)
│   ├── Metadata overlay (on hover)
│   └── Title/Logo (on selection)
└── MediaInfo (below selected card)
```



#### **Media Detail Components**

```javascript
MediaDetail Page
├── Hero Section (70vh)
│   ├── Gradient overlays
│   ├── MediaTitle
│   ├── Action buttons (Play, More Info)
│   └── Metadata badges
└── Content Section
    ├── ContentTypeToggle (Series/Movies)
    ├── SeasonEpisodeSelector
    │   ├── SeasonSelector
    │   └── EpisodeGrid
    │       └── EpisodeCard[]
    └── MoviesGrid (if movies available)
        └── MovieCard[]
```



#### **Video Player Components**

```javascript
VideoPlayer
├── video element (fullscreen)
├── LoadingSpinner
├── ErrorMessage
├── PlayOverlay
├── TopBar (back button, video info)
├── ProgressBar (seekable)
└── ControlBar
    ├── Play/Pause
    ├── Skip controls
    ├── VolumeControl
    ├── QualitySelector
    ├── NextEpisodeButton
    └── EpisodeSelector button
```



### Component Patterns

#### **State Management**

- **Local State**: `useState` for UI state (selection, hover, modals)
- **Data Fetching**: SWR hooks (`usePopular`, `useLatest`, `useSearch`, `useSeriesDetail`)
- **URL State**: `useSearchParams` for navigation parameters
- **Custom Hooks**: 
- `useVideoPlayer` - Video playback logic
- `useVideoControls` - Player controls
- `useControlsVisibility` - Auto-hide controls
- `useWebOSFocus` - TV navigation

#### **Responsive Design**

- Mobile-first approach with Tailwind breakpoints
- Custom width/height utilities for media cards
- Responsive typography scaling
- Grid layouts adapt from 1-5 columns

#### **WebOS TV Optimization**

- **Focus Management**: Custom `useWebOSFocus` hook
- **5-Way Navigation**: Arrow key handling
- **Focus Rings**: Visible focus indicators for TV remotes
- **Enter Key**: Triggers navigation/playback
- **Back Button**: Handles modal dismissal and navigation

## Styling Patterns

### Utility Classes

- **Transitions**: `transition-all duration-300` for smooth animations
- **Transforms**: `transform-gpu` for hardware acceleration
- **Gradients**: Multiple gradient overlays for depth
- **Backdrop Blur**: `backdrop-blur-sm` for glassmorphism effects
- **Scrollbar Hiding**: Custom `.scrollbar-hide` utility

### Animation Patterns

- **Card Selection**: Scale transform + width change
- **Hover Effects**: Scale (1.05x) + shadow glow
- **Control Visibility**: Slide up/down with opacity transition
- **Loading States**: Spinning indicators with fade
- **Modal Transitions**: Backdrop blur + fade in

### Z-Index Layering

- **Navbar**: z-50
- **Modals**: z-50
- **Selected Cards**: z-50
- **Hovered Cards**: z-50
- **Normal Cards**: z-10
- **Video Overlays**: z-10-20

## Layout Specifics

### Browse Pages (Aniworld, SerienStream)

```javascript
Container: min-h-screen bg-background overflow-y-auto
└── Content: relative z-10 pb-16
    └── MediaRow[] (vertical stack)
        └── Each row: h-screen with horizontal scroll
```



### Media Detail Page

```javascript
Container: flex flex-col h-[calc(100vh-80px)] overflow-y-auto
├── Hero: relative h-[70vh] w-full
│   ├── Gradients (absolute, z-10)
│   └── Content (relative, z-20, justify-end)
└── Content: px-8 md:px-16 lg:px-20 mt-8 space-y-8
    ├── Toggle buttons
    └── Episode/Movie grid
```



### Video Player Page

```javascript
Container: min-h-screen bg-black
└── VideoPlayer: relative bg-black w-full h-screen
    ├── video element (fullscreen)
    └── Overlays (absolute positioned)
        ├── TopBar (top)
        └── Controls (bottom, slide up/down)
```



### Search Modal

```javascript
Container: fixed h-[calc(100vh)] w-full z-50
├── Backdrop: bg-background/95 backdrop-blur-sm
└── Content: max-w-7xl mx-18 py-8
    ├── SearchInput
    └── Results: grid layout (1-5 columns)
```



## Navigation Flow

### Current Navigation Patterns

1. **Browse** → Click card → **MediaDetail**

- Navigation: `navigate('/media-detail?url=...&src=...')`
- Data: Fetches series detail on MediaDetail mount

2. **MediaDetail** → Click episode → **WatchMedia**

- Navigation: `navigate('/watch?url=...&src=...&seriesUrl=...&episode=...&season=...')`
- Data: Fetches video sources + re-fetches series detail

3. **WatchMedia** → Back button → **MediaDetail**

- Navigation: `navigate('/media-detail?url=...&src=...')` or `window.history.back()`
- Data: Re-fetches series detail (even if already cached)

4. **WatchMedia** → Next episode → **WatchMedia** (same route)

- Navigation: Full page navigation to same route with new params
- Data: Re-fetches video sources, series data already cached

5. **Navbar** → Search icon → **SearchModal**

- Navigation: Modal overlay (no route change)
- Data: Fetches search results on query

6. **SearchModal** → Click result → **MediaDetail**

- Navigation: `navigate('/media-detail?url=...&src=...')`
- Data: Fetches series detail on MediaDetail mount

### Navigation Flow Optimization Opportunities

#### 1. **Route-Based Code Splitting** (High Impact)

**Current Issue**: All page components are imported directly in `App.tsx`, loading all code upfront.**Optimization**:

- Use `React.lazy()` for route components
- Implement `Suspense` boundaries for loading states
- Reduces initial bundle size significantly
- Improves Time to Interactive (TTI)

**Implementation**:

```typescript
const MediaDetail = lazy(() => import('./pages/MediaDetail'));
const WatchMedia = lazy(() => import('./pages/WatchMedia'));
// Wrap routes in <Suspense fallback={<Loading />}>
```

**Expected Impact**: 30-50% reduction in initial bundle size

#### 2. **Data Prefetching on Hover/Focus** (High Impact)

**Current Issue**: No prefetching when user hovers/focuses on media cards. Click triggers full loading state.**Optimization**:

- Prefetch series detail data when card receives focus/hover
- Use SWR's `mutate` function to prefetch
- Prefetch video sources when episode card is focused
- Implement debounced prefetching to avoid excessive requests

**Implementation Points**:

- `MediaCard`: Prefetch on `onFocus` or `onMouseEnter` (with delay)
- `EpisodeCard`: Prefetch video sources on focus
- Use SWR cache to avoid duplicate requests

**Expected Impact**: 50-80% reduction in perceived loading time

#### 3. **Eliminate Redundant Data Fetching** (Medium Impact)

**Current Issue**:

- Series detail fetched in both MediaDetail and WatchMedia
- WatchMedia re-fetches even when navigating from MediaDetail
- SWR cache exists but not fully utilized

**Optimization**:

- Pass series data via React Router state instead of re-fetching
- Use SWR cache more effectively (data already available)
- Only fetch if cache miss or stale

**Implementation**:

```typescript
// In MediaDetail when navigating to WatchMedia
navigate('/watch', { 
  state: { seriesData: data },
  search: `?url=...&src=...`
});

// In WatchMedia, check state first
const location = useLocation();
const cachedSeriesData = location.state?.seriesData;
```

**Expected Impact**: Eliminates unnecessary API calls, faster navigation

#### 4. **In-Place Episode Navigation** (High Impact)

**Current Issue**: Changing episodes in WatchMedia triggers full page navigation, causing:

- Video player remount
- Loading spinner
- Loss of playback state
- Unnecessary re-renders

**Optimization**:

- Update video source in-place without navigation
- Use state management to update episode
- Only navigate when necessary (different series)
- Preserve playback position and settings

**Implementation**:

- Replace `navigate('/watch?...)` with state update
- Update `selectedVideo` state directly
- Keep video element mounted
- Update URL without full navigation (using `replace`)

**Expected Impact**: Instant episode switching, better UX

#### 5. **Navigation State Persistence** (Medium Impact)

**Current Issue**:

- Scroll position lost on navigation
- Selected card state lost
- Season selection reset
- No "back to where you were" functionality

**Optimization**:

- Use React Router's `location.state` to persist UI state
- Implement scroll restoration
- Save selected season/episode in URL or state
- Use browser's scroll restoration API

**Implementation**:

- Store scroll position in sessionStorage
- Pass selected card index via navigation state
- Use URL hash for season selection persistence

**Expected Impact**: Better user experience, feels more native

#### 6. **Centralized URL Parameter Management** (Low Impact, High Maintainability)

**Current Issue**: URL parameter parsing and construction duplicated across multiple files.**Optimization**:

- Create utility functions for URL param management
- Type-safe parameter handling
- Centralized validation
- Easier to maintain and test

**Implementation**:

```typescript
// lib/utils/navigation.ts
export const buildMediaDetailUrl = (url: string, source: string) => ...
export const buildWatchUrl = (params: WatchParams) => ...
export const parseMediaDetailParams = (searchParams: URLSearchParams) => ...
```

**Expected Impact**: Reduced code duplication, easier maintenance

#### 7. **Optimistic Navigation with Loading States** (Medium Impact)

**Current Issue**: Navigation feels abrupt, no transition feedback.**Optimization**:

- Show loading skeleton immediately on navigation
- Use SWR's optimistic updates
- Implement route transition animations
- Show cached data immediately while fetching fresh data

**Implementation**:

- Use Framer Motion or CSS transitions for route changes
- Show skeleton loaders matching final layout
- Display cached data with "updating" indicator

**Expected Impact**: Perceived performance improvement, smoother UX

#### 8. **Link Prefetching for Likely Next Pages** (Low-Medium Impact)

**Current Issue**: No prefetching of likely next pages.**Optimization**:

- Prefetch next episode's video sources when current episode is 80% complete
- Prefetch adjacent media cards in rows
- Prefetch popular content on app load
- Use `<link rel="prefetch">` for critical routes

**Implementation**:

- Monitor video playback progress
- Prefetch next episode data automatically
- Prefetch media detail for adjacent cards in row

**Expected Impact**: Near-instant navigation for common paths

#### 9. **Eliminate Duplicate Season Finding Logic** (Low Impact, High Maintainability)

**Current Issue**: Logic to find season for episode duplicated in:

- `MediaDetail.handleEpisodeClick`
- `WatchMedia.handleEpisodeChange`
- Potentially other places

**Optimization**:

- Extract to utility function
- Memoize season lookup
- Create episode navigation helper

**Implementation**:

```typescript
// lib/utils/episodeNavigation.ts
export const findEpisodeSeason = (episodeUrl: string, seasons: Season[]) => ...
export const buildEpisodeNavigationParams = (episode: Episode, season: Season, ...) => ...
```

**Expected Impact**: DRY principle, easier to maintain

#### 10. **Smart Caching Strategy** (Medium Impact)

**Current Issue**: SWR cache configuration is basic, no custom cache invalidation.**Optimization**:

- Implement cache tags for related data
- Invalidate related caches on mutations
- Use longer cache times for stable data
- Implement cache warming on app start

**Implementation**:

- Tag series data with series ID
- Invalidate all related caches when series updates
- Pre-warm cache with popular content
- Use `keepPreviousData` for pagination

**Expected Impact**: Better cache hit rates, fewer API calls

#### 11. **Parallel Data Fetching** (Medium Impact)

**Current Issue**: Some pages fetch data sequentially when it could be parallel.**Optimization**:

- Fetch video sources and series data in parallel in WatchMedia
- Use Promise.all or parallel SWR hooks
- Don't wait for one to complete before starting another

**Current**: WatchMedia waits for video sources, then fetches series data**Optimized**: Both fetch simultaneously**Expected Impact**: 30-50% faster page load when both needed

#### 12. **Route Transition Optimization** (Low Impact, High Polish)

**Current Issue**: No visual feedback during route transitions.**Optimization**:

- Implement page transition animations
- Show progress indicator during navigation
- Use React Router's `useNavigation` hook
- Add loading bar at top of page

**Expected Impact**: More polished, professional feel

### Priority Ranking

**High Priority (Implement First)**:

1. Route-based code splitting
2. Data prefetching on hover/focus
3. In-place episode navigation
4. Eliminate redundant data fetching

**Medium Priority**:

5. Navigation state persistence
6. Optimistic navigation with loading states
7. Smart caching strategy
8. Parallel data fetching

**Low Priority (Nice to Have)**:

9. Centralized URL parameter management
10. Eliminate duplicate logic
11. Link prefetching
12. Route transition optimization

### Implementation Complexity vs Impact Matrix

```javascript
High Impact, Low Complexity:
- Route-based code splitting
- Eliminate duplicate logic
- Centralized URL params

High Impact, Medium Complexity:
- Data prefetching
- In-place episode navigation
- Eliminate redundant fetching

Medium Impact, Low Complexity:
- Route transitions
- Link prefetching

Medium Impact, Medium Complexity:
- State persistence
- Optimistic navigation
- Smart caching
- Parallel fetching
```



## Key Design Features

1. **Netflix-Style Card Selection**: Selected cards expand to 4x width
2. **Auto-Scrolling Rows**: Rows automatically scroll to keep selection in view
3. **Gradient Overlays**: Multiple layered gradients for depth
4. **TV-Optimized Focus**: Large, visible focus rings for remote navigation
5. **Smooth Transitions**: 300ms transitions throughout
6. **Responsive Typography**: Scales from mobile to 4K displays
7. **Dark Theme**: Consistent dark background with red accents
8. **Loading States**: Centered spinners with descriptive text
9. **Error States**: Red-bordered error cards with retry options
10. **Empty States**: Centered messages with helpful suggestions

## Responsive Breakpoints

- **Mobile**: Default (1 column grids, smaller text)
- **sm**: 640px (2 column grids)
- **md**: 768px (3 column grids, larger text, desktop nav)
- **lg**: 1024px (4 column grids, full typography)
- **xl**: 1280px (5 column grids, maximum width containers)

## Performance Optimizations

- **Lazy Loading**: Images use `loading="lazy"`
- **GPU Acceleration**: `transform-gpu` for animations
- **Memoization**: `useMemo` for computed values
- **Callback Optimization**: `useCallback` for event handlers
- **Code Splitting**: Route-based splitting with React Router
- **SWR Caching**: Automatic request deduplication and caching

## Accessibility Features

- **Focus Management**: Custom WebOS focus system
- **Keyboard Navigation**: Full keyboard support
- **ARIA Labels**: Proper labeling for screen readers
- **Semantic HTML**: Proper heading hierarchy

## User-Facing Data & Content Display

This section describes all data displayed to users using common sense naming conventions, organized by where it appears in the UI.

### Browse Pages (Aniworld, SerienStream)

#### Media Cards in Horizontal Rows

**Currently Displayed:**

- **Title**: Media name/title (from `name` field)
- **Card Image**: Cover/poster image (from `image_url` or `cover_image_url`)
- **Background Image**: Backdrop image when card is selected (from `backdrop_url` or `image_backdrop_url`)
- **Release Year**: Year the media was released (from `start_year` or `release_year`)
- **Rating**: User rating percentage or score (from `rating_value` or `average_rating`)
- **Rating Count**: Number of user ratings (from `rating_count` or `votes`)
- **Seasons Count**: Number of seasons (from `seasons_length` or `seasons_count`)
- **Status**: Media status (e.g., "ongoing", "completed") (from `media_status`)
- **Ranking Badges**: Top rankings (e.g., "#1 Rated", "#5 Popular") (from `best_ranking`)
- **Logo**: Series logo image when available (from `logo_urls`)

**Available but Not Currently Displayed:**

- **Description**: Full media description/synopsis (from `description` in `MediaInfo`)
- **Genres**: List of genres (from `genres` array)
- **Alternative Titles**: Titles in different languages (from `alternative_titles`)
- **End Year**: Year the series ended (from `end_year`)
- **Age Rating**: FSK rating (German age rating system) (from `fsk_rating`)
- **IMDB ID**: Link to IMDB page (from `imdb_id`)
- **Country of Origin**: Production country (from `country_of_origin`)
- **Main Genre**: Primary genre classification (from `main_genre`)
- **Directors**: List of directors (from `directors` array)
- **Actors**: List of main actors (from `actors` array)
- **Producers**: List of production companies (from `producers` array)
- **Trailer URL**: Link to trailer video (from `trailer_url`)
- **Available Languages**: Supported audio/subtitle languages (from `available_languages`)
- **Provider Name**: Source provider name (from `provider`)

#### Media Info Panel (Below Selected Card)

**Currently Displayed:**

- **Title**: Media title
- **Release Year**: Year of release
- **Content Type**: "Series" label
- **Rating**: Percentage score or vote count
- **Ranking**: Top ranking badges if available
- **Status**: Media status (ongoing, completed, etc.)
- **Seasons Count**: Number of seasons

**Available but Not Currently Displayed:**

- **Description**: Full synopsis text
- **Genres**: Genre badges/tags
- **Directors**: Director names
- **Actors**: Cast list
- **Producers**: Production companies
- **Country**: Country of origin
- **Age Rating**: FSK/MPAA rating
- **IMDB Link**: External link to IMDB
- **Alternative Titles**: Other language titles

### Media Detail Page

#### Hero Section

**Currently Displayed:**

- **Title**: Series title (formatted from `slug`)
- **Play Button**: Primary action button
- **More Info Button**: Secondary action button
- **Season Count**: Number of seasons badge
- **Movie Count**: Number of movies/OVAs badge
- **Content Type**: Type label (anime, series_movie, adult)

**Available but Not Currently Displayed:**

- **Background Image**: Large backdrop image for hero section (from `backdrop_url` in `MediaInfo`)
- **Description**: Full synopsis in hero section
- **Release Year**: Start and end years
- **Genres**: Genre tags
- **Rating**: User rating with star display
- **Age Rating**: FSK/MPAA rating badge
- **Directors**: Director names
- **Actors**: Main cast list
- **Country**: Production country
- **IMDB Link**: External link
- **Trailer**: Embedded trailer video
- **Logo**: Series logo image

#### Episode/Movie Selection Area

**Currently Displayed:**

- **Season Selector**: Dropdown/buttons to select season
- **Episode Cards**: Grid of episode cards showing:
- **Episode Number**: Episode number within season
- **Episode Title**: Episode name/title
- **Episode Thumbnail**: Episode still image (if available from TMDB)
- **Movie Cards**: Grid of movie/OVA cards showing:
- **Movie Number**: Movie number in series
- **Movie Title**: Movie name
- **Movie Type**: Kind (movie, ova, special)

**Available but Not Currently Displayed:**

- **Episode Description**: Episode synopsis (from TMDB `overview`)
- **Episode Air Date**: Original air date (from TMDB `air_date`)
- **Episode Runtime**: Episode duration in minutes (from TMDB `runtime`)
- **Episode Rating**: Episode-specific rating (from TMDB `vote_average`)
- **Episode Images**: Episode stills and screenshots (from TMDB `stills`)
- **Episode Crew**: Directors, writers for episode (from TMDB `crew`)
- **Episode Guest Stars**: Guest cast (from TMDB `guest_stars`)
- **Season Title**: Season name/title
- **Season Description**: Season overview (from TMDB)
- **Season Poster**: Season poster image (from TMDB)
- **Season Air Date**: Season premiere date
- **Movie Upload Date**: When movie was uploaded (from `date_upload`)
- **Movie Tags**: Content tags (from `tags` array)

### Video Player Page

#### Video Display

**Currently Displayed:**

- **Video Stream**: Main video playback
- **Video Quality**: Selected quality label (e.g., "1080p", "720p")
- **Video Language**: Audio language (e.g., "de", "en", "de_sub")
- **Video Format**: Stream format (e.g., "hls", "mp4")
- **Current Time**: Playback position (MM:SS format)
- **Duration**: Total video length (MM:SS format)
- **Progress Bar**: Seekable progress indicator
- **Volume Level**: Current volume (0-100%)
- **Mute Status**: Muted/unmuted indicator

**Available but Not Currently Displayed:**

- **Episode Title**: Current episode name
- **Episode Number**: Season and episode numbers
- **Episode Description**: Episode synopsis
- **Next Episode Preview**: Preview of next episode
- **Video Source URL**: Original provider URL (for debugging)
- **Stream Type**: Dub/Sub/Original indicator (from `type` field)

#### Control Bar

**Currently Displayed:**

- **Play/Pause Button**: Toggle playback
- **Skip Forward**: Skip ahead (typically 10 seconds)
- **Skip Backward**: Skip back (typically 10 seconds)
- **Volume Slider**: Volume control
- **Mute Button**: Toggle mute
- **Quality Selector**: Dropdown to change video quality
- **Fullscreen Toggle**: Enter/exit fullscreen
- **Episode List Button**: Open episode selector
- **Next Episode Button**: Jump to next episode (if available)
- **Time Display**: Current time / Total duration

**Available but Not Currently Displayed:**

- **Playback Speed**: Speed control (0.5x, 1x, 1.5x, 2x)
- **Subtitle Toggle**: Enable/disable subtitles
- **Audio Track Selector**: Switch between audio languages
- **Chapter Navigation**: Jump to chapters/markers
- **Picture-in-Picture**: PiP mode toggle

### Search Modal

**Currently Displayed:**

- **Search Query**: User's search text
- **Search Results**: Grid of media cards showing:
- **Title**: Media name
- **Card Image**: Cover image
- **Provider**: Source provider name
- **Result Count**: Number of results found
- **Pagination Info**: Current page, total pages (available but not displayed)

**Available but Not Currently Displayed:**

- **Available Languages**: Language badges for each result
- **Media Type Badge**: Content type indicator
- **Rating Preview**: Quick rating display
- **Release Year**: Year badge
- **Genre Tags**: Quick genre indicators
- **Match Confidence**: How well result matches query (from API)

### Navigation & UI Elements

#### Navbar

**Currently Displayed:**

- **Logo**: "ANYFLIX" brand text
- **Navigation Links**: Home, Aniworld, SerienStream, etc.
- **Search Icon**: Opens search modal
- **Notifications Icon**: Placeholder
- **User Icon**: Links to auth page

**Available but Not Currently Displayed:**

- **User Profile**: User name/avatar
- **Notification Badge**: Unread count
- **Source Selector**: Switch between content sources
- **Language Selector**: Change UI language

### Additional Data Available from API

#### TMDB Enrichment Data (Available but Not Fully Utilized)

The API provides extensive TMDB (The Movie Database) enrichment data that could enhance the UI:**Series-Level TMDB Data:**

- **Overview**: Detailed series description
- **Poster Images**: High-quality poster images
- **Backdrop Images**: Wide background images
- **Videos**: Trailers, teasers, clips
- **Images**: Production stills, posters, backdrops
- **Cast**: Full cast list with photos
- **Crew**: Directors, writers, producers with details
- **External IDs**: Links to IMDB, TVDB, etc.
- **Networks**: Broadcasting networks
- **Production Companies**: Studio information
- **Spoken Languages**: Available languages
- **Origin Country**: Production countries
- **First Air Date**: Premiere date
- **Last Air Date**: Finale date
- **Number of Episodes**: Total episode count
- **Number of Seasons**: Total season count
- **Status**: Production status
- **Type**: Show type
- **Genres**: Detailed genre information
- **Created By**: Show creators
- **Vote Average**: TMDB rating
- **Vote Count**: Number of TMDB votes
- **Popularity Score**: TMDB popularity metric
- **Content Ratings**: Age ratings by country

**Season-Level TMDB Data:**

- **Season Overview**: Season description
- **Season Poster**: Season-specific poster
- **Season Air Date**: Premiere date
- **Episode Count**: Episodes in season
- **Season Number**: Season identifier
- **Videos**: Season trailers
- **Images**: Season-specific images

**Episode-Level TMDB Data:**

- **Episode Overview**: Episode synopsis
- **Episode Still**: Episode screenshot
- **Air Date**: Original air date
- **Episode Number**: Episode identifier
- **Runtime**: Episode duration
- **Vote Average**: Episode rating
- **Vote Count**: Number of votes
- **Crew**: Episode directors, writers
- **Guest Stars**: Guest cast with photos
- **Videos**: Episode clips/trailers
- **Images**: Episode stills

#### Pagination Data

**Available from API:**

- **Current Page**: Current page number
- **Items Per Page**: Results per page
- **Total Items**: Total number of results
- **Total Pages**: Total number of pages
- **Has Next Page**: Boolean for next page availability
- **Has Previous Page**: Boolean for previous page availability

**Currently Used:**

- Basic pagination in API hooks

**Not Currently Displayed:**

- Page numbers in UI
- "Load More" buttons
- Pagination controls
- Result count displays

#### Source & Provider Data

**Available:**

- **Source List**: All available content sources (aniworld, serienstream, etc.)
- **Source Preferences**: Configuration for each source
- **Source Status**: Health/availability status of sources
- **Provider Name**: Content provider identifier
- **Provider URL**: Link to original content page

**Currently Used:**

- Source selection for API calls
- Provider name display in search results

**Not Currently Displayed:**

- Source selector UI
- Source status indicators
- Provider links/attribution

#### Admin & Debug Data

**Available (for development):**

- **Cache Statistics**: Cache hit/miss rates
- **Source Status**: Detailed source health
- **Match Confidence**: TMDB matching confidence scores
- **Content Type**: Classification (anime, series_movie, adult, unknown)

**Currently Used:**

- Content type for conditional rendering

**Not Currently Displayed:**