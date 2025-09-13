# Anyflix Frontend Types with Zod

This directory contains comprehensive **Zod schemas** for the Anyflix application, providing runtime validation and type inference from the backend Python models.

## File Structure

### `schemas/base.ts`

Contains core data models, enums, and base schemas:

- **Base Enums**: `MovieKindSchema`, `MediaTypeSchema`, `MediaFormatSchema`, etc.
- **Core Data**: `EpisodeSchema`, `SeasonSchema`, `MovieSchema`, `SeriesDetailSchema`, etc.
- **Common Types**: `VideoSourceSchema`, `SearchResultSchema`, `MediaInfoSchema`

### `schemas/anilist.ts`

Complete AniList GraphQL API schemas:

- **Media Models**: `AniListMediaSchema`, `MediaTitleSchema`, `CoverImageSchema`
- **Character/Staff**: `CharacterSchema`, `StaffSchema`, `VoiceActorSchema`
- **Connections**: `CharacterConnectionSchema`, `StaffConnectionSchema`, etc.
- **Metadata**: `MediaTagSchema`, `MediaRankingSchema`, `MediaStatsSchema`

### `schemas/tmdb.ts`

The Movie Database API schemas:

- **Detail Models**: `TMDBMovieDetailSchema`, `TMDBTVDetailSchema`
- **Search**: `TMDBSearchResultSchema`, `TMDBSearchResponseSchema`
- **Media Assets**: `TMDBImageSchema`, `TMDBVideoSchema`, `TMDBImagesSchema`
- **Metadata**: `TMDBGenreSchema`, `TMDBProductionCompanySchema`, etc.

### `zod-responses.ts`

API response schemas with validation helpers:

- **Response Types**: `PopularResponseSchema`, `SearchResponseSchema`, etc.
- **Validation Helpers**: `validateAPIResponse`, `safeValidateAPIResponse`
- **Type Guards**: `isAPISuccess`, `isAPIFailure`
- **Error Handling**: `APIErrorSchema`, `APIFailureSchema`

### `index.ts`

Main export file that re-exports all schemas and types for easy importing.

## Usage Examples

### Basic Schema Validation

```typescript
import { SearchResponseSchema, validateSearchResponse } from '@/types';

// Runtime validation with error handling
const handleAPIResponse = (rawData: unknown) => {
  try {
    const validatedData = validateSearchResponse(rawData);
    console.log('Valid search results:', validatedData.list);
  } catch (error) {
    console.error('Invalid API response:', error.message);
  }
};

// Safe validation without throwing
import { safeValidateAPIResponse } from '@/types';

const handleSafeValidation = (rawData: unknown) => {
  const result = safeValidateAPIResponse(SearchResponseSchema, rawData);
  
  if (result.success) {
    console.log('Valid data:', result.data);
  } else {
    console.error('Validation failed:', result.error);
  }
};
```

### Working with Inferred Types

```typescript
import { 
  SearchResult, 
  VideoSource, 
  SeriesDetail,
  AniListMedia,
  TMDBTVDetail 
} from '@/types';

// Types are automatically inferred from Zod schemas
const processSearchResult = (result: SearchResult) => {
  const { name, image_url, anilist_data, tmdb_data } = result;
  
  // Runtime validation ensures these fields exist and are correct types
  console.log(`Found: ${name}`);
  
  if (anilist_data) {
    // anilist_data is validated as Record<string, any> but can be further validated
  }
};
```

### Schema Composition and Validation

```typescript
import { 
  EpisodeSchema, 
  SeasonSchema, 
  SeriesDetailResponseSchema 
} from '@/types';

// Validate nested data structures
const validateSeriesData = (rawData: unknown) => {
  const result = SeriesDetailResponseSchema.safeParse(rawData);
  
  if (result.success) {
    const { series, type, anilist_data } = result.data;
    
    // All nested data is validated: seasons, episodes, movies
    series.seasons.forEach(season => {
      console.log(`Season ${season.season} has ${season.episodes.length} episodes`);
    });
    
    return result.data;
  } else {
    console.error('Validation errors:', result.error.format());
    return null;
  }
};
```

### Custom Validation with Zod

```typescript
import { z } from 'zod';
import { VideoSourceSchema, MovieKindSchema } from '@/types';

// Extend existing schemas
const ExtendedVideoSourceSchema = VideoSourceSchema.extend({
  customField: z.string().optional(),
  isPreferred: z.boolean().default(false)
});

// Create unions and refinements
const QualityVideoSourceSchema = VideoSourceSchema.refine(
  (data) => ['1080p', '720p', '480p'].includes(data.quality),
  { message: 'Quality must be 1080p, 720p, or 480p' }
);

// Transform data during validation
const ProcessedVideoSourceSchema = VideoSourceSchema.transform((data) => ({
  ...data,
  qualityRank: data.quality === '1080p' ? 1 : data.quality === '720p' ? 2 : 3
}));
```

### API Response Handling

```typescript
import { 
  PopularResponseSchema,
  isAPISuccess,
  isAPIFailure,
  APIResult 
} from '@/types';

const fetchPopularContent = async (): Promise<APIResult<PopularResponse>> => {
  try {
    const response = await fetch('/api/sources/aniworld/popular');
    const rawData = await response.json();
    
    // Validate the response structure
    const validatedData = PopularResponseSchema.parse(rawData);
    
    return {
      success: true,
      data: validatedData
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      status_code: 500
    };
  }
};

// Usage with type guards
const handlePopularContent = async () => {
  const result = await fetchPopularContent();
  
  if (isAPISuccess(result)) {
    // TypeScript knows result.data is PopularResponse
    result.data.list.forEach(item => {
      console.log(item.name, item.image_url);
    });
  } else if (isAPIFailure(result)) {
    // TypeScript knows result has error and status_code
    console.error(`API Error ${result.status_code}: ${result.error}`);
  }
};
```

### Enum Validation

```typescript
import { MovieKindSchema, MediaTypeSchema } from '@/types';

// Validate enum values
const validateMovieKind = (value: unknown) => {
  const result = MovieKindSchema.safeParse(value);
  return result.success ? result.data : null;
};

// Use in forms or user input
const handleUserInput = (movieType: string) => {
  const validMovieKind = validateMovieKind(movieType);
  
  if (validMovieKind) {
    console.log(`Valid movie kind: ${validMovieKind}`);
    // validMovieKind is typed as "movie" | "ova" | "special"
  } else {
    console.error('Invalid movie kind provided');
  }
};
```

## Backend API Endpoints Mapping

All response schemas correspond to these backend endpoints:

| Endpoint | Schema | Type |
|----------|--------|------|
| `GET /sources/` | `SourcesResponseSchema` | `SourcesResponse` |
| `GET /sources/{source}/popular` | `PopularResponseSchema` | `PopularResponse` |
| `GET /sources/{source}/search` | `SearchResponseSchema` | `SearchResponse` |
| `GET /sources/{source}/videos` | `VideoListResponseSchema` | `VideoListResponse` |
| `GET /sources/{source}/series` | `SeriesDetailResponseSchema` | `SeriesDetailResponse` |
| `POST /sources/trailer` | `TrailerResponseSchema` | `TrailerResponse` |

## Validation Helpers

The library provides several validation utilities:

### `validateAPIResponse<T>(schema, data): T`

Validates data against a schema and returns the parsed result or throws an error.

### `safeValidateAPIResponse<T>(schema, data): Result<T>`

Safely validates data and returns a result object with success/failure information.

### Type Guards

- `isAPISuccess(result)`: Checks if an API result is successful
- `isAPIFailure(result)`: Checks if an API result is a failure

## Best Practices

1. **Always validate API responses** using the provided schemas
2. **Use safe validation** (`safeParse`) when you need to handle errors gracefully
3. **Leverage TypeScript inference** - types are automatically generated from schemas
4. **Extend schemas** when you need additional validation or transformation
5. **Use type guards** for runtime type checking in conditional logic
6. **Handle validation errors** appropriately in your UI

## Migration Guide

If you're updating from the old TypeScript-only types:

```typescript
// Old way (no runtime validation)
interface SearchResult {
  name: string;
  image_url: string;
  // ... other fields
}

// New way (with runtime validation)
import { SearchResultSchema, type SearchResult } from '@/types';

// Validate at runtime
const validatedResult = SearchResultSchema.parse(rawData);

// Or use the inferred type for type annotations
const processResult = (result: SearchResult) => {
  // TypeScript knows the exact shape and provides autocomplete
};
```

## Performance Considerations

- Zod validation adds minimal runtime overhead
- Schemas are optimized for common use cases
- Use `safeParse()` instead of `parse()` when performance is critical
- Consider validating only at API boundaries, not internal data transformations

This new structure provides both compile-time type safety and runtime validation, ensuring your application handles API data reliably! 🎉