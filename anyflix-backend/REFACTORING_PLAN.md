# API Refactoring Plan - Remove Deprecated Fields & Fix Documentation

**Branch:** `ref/remove-backend-side-anylist-and-tmdb`
**Date:** 2025-12-19
**Objective:** Remove all backwards compatibility code, deprecated fields, and fix API documentation inconsistencies

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Phase 1: Critical - Documentation Fixes](#phase-1-critical---documentation-fixes)
3. [Phase 2: High Priority - Remove Deprecated Fields](#phase-2-high-priority---remove-deprecated-fields)
4. [Phase 3: Medium Priority - Code Quality](#phase-3-medium-priority---code-quality)
5. [Phase 4: Testing & Validation](#phase-4-testing--validation)
6. [Files to Modify](#files-to-modify)
7. [Breaking Changes Summary](#breaking-changes-summary)

---

## Executive Summary

### Issues Found: 23 Total
- **3 Critical**: API documentation doesn't match actual responses
- **8 High Priority**: Deprecated fields that should be removed
- **9 Medium**: Code quality and security issues
- **3 Low**: Minor improvements

### Current API Structure Issues

**Problem:** The codebase has two conflicting response structures:

**OLD (Deprecated - still in EXAMPLES.md):**
```json
{
  "tmdb_enrichment": {
    "tmdb_data": { ... },
    "match_confidence": 0.95
  }
}
```

**NEW (v1.1.0+ - in API.md and actual code):**
```json
{
  "tmdb_series_data": { ... },
  "match_confidence": 0.95
}
```

---

## Phase 1: Critical - Documentation Fixes

**Priority:** MUST BE DONE FIRST
**Impact:** Prevents frontend developers from implementing wrong API structure

### Task 1.1: Update EXAMPLES.md

**File:** `EXAMPLES.md`

**Changes Required:**

#### Line 291-308: Series Overview Response
**Current (WRONG):**
```json
{
  "content_type": "anime",
  "series": { ... },
  "tmdb_enrichment": {
    "tmdb_data": { ... },
    "match_confidence": 0.95
  },
  "season_count": 4
}
```

**Should be:**
```json
{
  "content_type": "anime",
  "series": { ... },
  "season_count": 4,
  "tmdb_series_data": { ... },
  "match_confidence": 0.95
}
```

#### Line 346-350: All Seasons Response
**Remove:** `tmdb_enrichment` nested structure
**Replace with:** `tmdb_series_data` and `match_confidence` at root level

#### Line 336-340: Episode Structure in Seasons
**Current (WRONG):**
```json
{
  "season": 1,
  "episode": 1,
  "title": "To You, in 2000 Years",
  "tmdb_id": 63056,
  "tmdb_overview": "...",
  "tmdb_vote_average": 8.2,
  "tmdb_air_date": "2013-04-07"
}
```

**Should be:**
```json
{
  "season": 1,
  "episode": 1,
  "title": "To You, in 2000 Years",
  "url": "/anime/stream/attack-on-titan/staffel-1/episode-1",
  "tmdb_episode_data": {
    "id": 63056,
    "name": "To You, in 2000 Years",
    "overview": "...",
    "vote_average": 8.2,
    "air_date": "2013-04-07",
    "still_path": "/path/to/still.jpg",
    "runtime": 24
  }
}
```

#### Line 388-400: Specific Season Response
**Remove:** `tmdb_enrichment` and `tmdb_season` at root level
**Replace with:** `tmdb_series_data` at root, `tmdb_season_data` inside season object

#### Line 432-444: Specific Episode Response
**Remove:** `tmdb_enrichment` and `tmdb_episode` at root level
**Replace with:** `tmdb_series_data` at root, `tmdb_episode_data` inside episode object

**Action Items:**
- [ ] Update all 5 series endpoint examples in EXAMPLES.md
- [ ] Ensure all examples show nested TMDB data structure
- [ ] Remove all references to deprecated `tmdb_enrichment` wrapper

---

### Task 1.2: Update current_structure.json

**File:** `current_structure.json`

**Current content (Line 17):** Uses deprecated `tmdb_enrichment` structure

**Action Items:**
- [ ] Replace entire file content with structure from `goal_structure.json`
- [ ] Verify it matches actual API responses from `series.py`

---

### Task 1.3: Verify API.md Accuracy

**File:** `docs/API.md`

**Status:** ✅ ALREADY CORRECT (shows v1.1.0+ structure)

**Action Items:**
- [ ] Verify all examples match actual endpoint implementations
- [ ] Add version notes indicating when the new structure was introduced

---

## Phase 2: High Priority - Remove Deprecated Fields

**Priority:** HIGH
**Impact:** Removes dead code and prevents confusion

### Task 2.1: Remove Deprecated Pagination Fields

**File:** `lib/models/responses.py`
**Lines to DELETE:** 102-106

**Current:**
```python
# Deprecated fields (kept for backward compatibility, will be removed in v2.0.0)
page: int | None = Field(None, ge=1, description="DEPRECATED: Use pagination.page instead")
per_page: int | None = Field(None, ge=1, description="DEPRECATED: Use pagination.per_page instead")
has_next: bool | None = Field(None, description="DEPRECATED: Use pagination.has_next instead")
has_previous: bool | None = Field(None, description="DEPRECATED: Use pagination.has_previous instead")
```

**Action:** DELETE these 5 lines entirely

**Related Changes Required:**

**File:** `lib/providers/base.py`
**Lines to MODIFY:** 322-326

**Current:**
```python
return PaginatedSearchResultResponse(
    content_type=self.content_type,
    items=paginated_items,
    pagination=pagination,
    # Deprecated fields (for backward compatibility)
    page=page,
    per_page=self.ITEMS_PER_PAGE,
    has_next=pagination.has_next,
    has_previous=pagination.has_previous,
)
```

**Should be:**
```python
return PaginatedSearchResultResponse(
    content_type=self.content_type,
    items=paginated_items,
    pagination=pagination,
)
```

**Action Items:**
- [ ] Delete deprecated pagination fields from `PaginatedSearchResultResponse` model
- [ ] Remove deprecated field population in `_create_paginated_response()`
- [ ] Update EXAMPLES.md to remove deprecated pagination fields (lines 59-63, 104-107, 149-151)

---

### Task 2.2: Remove tmdb_enrichment from SeriesDetailResponse

**File:** `lib/models/responses.py`
**Lines to DELETE:** 178-182

**Current:**
```python
# Deprecated (maintained for backward compatibility)
tmdb_enrichment: TMDBEnrichmentData | None = Field(
    None,
    description="DEPRECATED: Use tmdb_series_data and match_confidence instead",
)
```

**Action:** DELETE these lines

**Action Items:**
- [ ] Remove `tmdb_enrichment` field from `SeriesDetailResponse`
- [ ] Verify endpoints don't populate this field (already verified - they don't)

---

### Task 2.3: Remove tmdb_enrichment from SeasonsResponse

**File:** `lib/models/responses.py`
**Lines to DELETE:** 207-211

**Action:** DELETE deprecated `tmdb_enrichment` field

---

### Task 2.4: Remove tmdb_enrichment from SeasonResponse

**File:** `lib/models/responses.py`
**Lines to DELETE:** 236-240

**Action:** DELETE deprecated `tmdb_enrichment` field

---

### Task 2.5: Remove tmdb_season from SeasonResponse

**File:** `lib/models/responses.py`
**Lines to DELETE:** 241-244

**Current:**
```python
tmdb_season: TMDBSeasonDetail | None = Field(
    None,
    description="DEPRECATED: Use season.tmdb_season_data instead",
)
```

**Action:** DELETE these lines

**Replacement:** Data is now in `season.tmdb_season_data` (inside the EnrichedSeason model)

---

### Task 2.6: Remove tmdb_enrichment from EpisodeResponse

**File:** `lib/models/responses.py`
**Lines to DELETE:** 269-273

**Action:** DELETE deprecated `tmdb_enrichment` field

---

### Task 2.7: Remove tmdb_episode from EpisodeResponse

**File:** `lib/models/responses.py`
**Lines to DELETE:** 274-277

**Current:**
```python
tmdb_episode: TMDBEpisodeDetail | None = Field(
    None,
    description="DEPRECATED: Use episode.tmdb_episode_data instead",
)
```

**Action:** DELETE these lines

**Replacement:** Data is now in `episode.tmdb_episode_data` (inside the EnrichedEpisode model)

---

### Task 2.8: Remove tmdb_enrichment from MoviesResponse

**File:** `lib/models/responses.py`
**Lines to DELETE:** 299-303

**Action:** DELETE deprecated `tmdb_enrichment` field

---

### Task 2.9: Remove tmdb_enrichment from MovieResponse

**File:** `lib/models/responses.py`
**Lines to DELETE:** 325-329

**Action:** DELETE deprecated `tmdb_enrichment` field

---

### Task 2.10: Remove TMDBEnrichmentData Class

**File:** `lib/models/responses.py`
**Lines to DELETE:** 150-154

**Current:**
```python
class TMDBEnrichmentData(BaseModel):
    """TMDB enrichment metadata."""
    tmdb_data: TMDBMovieDetail | TMDBTVDetail | None = Field(None, description="TMDB movie or TV show details")
    match_confidence: float | None = Field(None, ge=0, le=1, description="Confidence score of TMDB match (0-1)")
```

**Action:** DELETE entire class

**Reason:** This class is never instantiated anywhere in the codebase. All endpoints use the new flat structure with `tmdb_series_data` and `match_confidence` as separate root-level fields.

---

## Phase 3: Medium Priority - Code Quality

### Task 3.1: Fix Type Inconsistency in SeriesDetailResponse

**File:** `lib/models/responses.py`
**Lines to MODIFY:** 171-173

**Current:**
```python
tmdb_series_data: TMDBTVDetail | TMDBMovieDetail | None = Field(
    None, description="Complete TMDB series or movie details"
)
```

**Issue:** The series endpoints only ever return `TMDBTVDetail`, never `TMDBMovieDetail`

**Evidence:** `app/routers/series.py` line 123:
```python
tmdb_series_data=enriched_data.tmdb_tv_detail,  # This is TMDBTVDetail
```

**Should be:**
```python
tmdb_series_data: TMDBTVDetail | None = Field(
    None, description="Complete TMDB TV series details"
)
```

**Action Items:**
- [ ] Change type from `TMDBTVDetail | TMDBMovieDetail | None` to `TMDBTVDetail | None`
- [ ] Update description to reflect it's TV-only

---

### Task 3.2: Add Null Checks in episode_from_element

**File:** `lib/providers/base.py`
**Lines to MODIFY:** 643-707

**Current Issue:**
```python
title_anchor = element.select_first("td.seasonEpisodeTitle a")
episode_span = title_anchor.select_first("span")  # Could crash if title_anchor is None
url = title_anchor.attr("href")  # Could crash if title_anchor is None
```

**Should be:**
```python
title_anchor = element.select_first("td.seasonEpisodeTitle a")
if not title_anchor:
    logger.warning("Missing title anchor in episode element")
    return None

episode_span = title_anchor.select_first("span")
url = title_anchor.attr("href")
```

**Action Items:**
- [ ] Add defensive null checks before accessing attributes
- [ ] Return `None` or skip malformed episodes gracefully
- [ ] Add warning logs for debugging

---

### Task 3.3: Replace Broad Exception Catching

**File:** `lib/providers/aniworld.py`
**Lines to MODIFY:** 78-82

**Current:**
```python
except Exception:
    self.logger.exception("Failed to fetch detail for search result %s", link)
    media_info = None
```

**Should be:**
```python
except (httpx.HTTPError, ValueError, AttributeError) as e:
    self.logger.exception("Failed to fetch detail for search result %s: %s", link, e)
    media_info = None
```

**File:** `lib/providers/serienstream.py`
**Lines to MODIFY:** 81-85

**Same fix**

**Action Items:**
- [ ] Replace bare `Exception` catches with specific exception types
- [ ] Use the same pattern as `series.py` (lines 161-164, 232-235)
- [ ] Apply consistently across both provider files

---

### Task 3.4: Add Type Annotation for _extract_videos_from_host

**File:** `lib/providers/base.py`
**Lines to MODIFY:** 814

**Current:**
```python
async def _extract_videos_from_host(
    self, redirect: str, host: str, lang: str, type_str: str, headers: dict
) -> list:  # Too vague
```

**Should be:**
```python
async def _extract_videos_from_host(
    self, redirect: str, host: str, lang: str, type_str: str, headers: dict
) -> list[VideoSource]:
```

**Action Items:**
- [ ] Change return type from `list` to `list[VideoSource]`

---

### Task 3.5: Clean Up Empty Test File

**File:** `tests/providers/__init__.py`

**Current:** 14 blank lines

**Should be:** Either add docstring or reduce to 1 blank line

**Action Items:**
- [ ] Either add proper package docstring or reduce to single blank line

---

### Task 3.6: Security - Add URL Validation

**File:** `lib/providers/base.py`
**Functions:** `get_detail()`, `get_video_list()`, multiple internal methods

**Current Issue:** URLs from user input are used without validation

**Action Items:**
- [ ] Add domain validation to ensure URLs belong to expected provider domains
- [ ] Validate URL format before making requests
- [ ] Consider adding URL sanitization utility function

---

## Phase 4: Testing & Validation

### Task 4.1: Update Test Expectations

**File:** `tests/providers/test_api_endpoints.py`
**Lines to MODIFY:** 335-340, 380-386

**Current Issue:** Tests validate episode structure but don't check for nested TMDB data

**Action Items:**
- [ ] Update test assertions to validate new response structure
- [ ] Add checks for `tmdb_episode_data` presence and structure
- [ ] Verify tests validate absence of deprecated fields
- [ ] Add validation for `tmdb_series_data` instead of `tmdb_enrichment`

---

### Task 4.2: Run Full Test Suite

**Action Items:**
- [ ] Run `pytest` to ensure all tests pass
- [ ] Fix any failing tests due to removed deprecated fields
- [ ] Verify pagination tests work without deprecated fields
- [ ] Test all series endpoints return correct structure

---

### Task 4.3: Manual API Testing

**Endpoints to Test:**

1. **Series Overview**
   ```bash
   GET /sources/aniworld/series?url=/anime/stream/attack-on-titan
   ```
   - [ ] Verify `tmdb_series_data` is present
   - [ ] Verify `match_confidence` is present
   - [ ] Verify `tmdb_enrichment` is ABSENT

2. **All Seasons**
   ```bash
   GET /sources/aniworld/series/seasons?url=/anime/stream/attack-on-titan
   ```
   - [ ] Verify each season has `tmdb_season_data`
   - [ ] Verify each episode has `tmdb_episode_data`
   - [ ] Verify deprecated fields are ABSENT

3. **Specific Season**
   ```bash
   GET /sources/aniworld/series/seasons/1?url=/anime/stream/attack-on-titan
   ```
   - [ ] Verify `season.tmdb_season_data` is present
   - [ ] Verify `tmdb_season` at root is ABSENT

4. **Specific Episode**
   ```bash
   GET /sources/aniworld/series/seasons/1/episodes/1?url=/anime/stream/attack-on-titan
   ```
   - [ ] Verify `episode.tmdb_episode_data` is present
   - [ ] Verify `tmdb_episode` at root is ABSENT

5. **Pagination Endpoints**
   ```bash
   GET /sources/aniworld/popular?page=1
   GET /sources/aniworld/latest?page=2
   GET /sources/aniworld/search?q=attack&page=1
   ```
   - [ ] Verify `pagination` object is present
   - [ ] Verify deprecated `page`, `per_page`, `has_next`, `has_previous` at root are ABSENT

---

## Files to Modify

### Documentation Files (3 files)
1. `EXAMPLES.md` - Update all API response examples
2. `current_structure.json` - Replace with correct structure
3. `docs/API.md` - Verify accuracy (likely already correct)

### Source Code Files (2 files)
1. `lib/models/responses.py` - Remove all deprecated fields and TMDBEnrichmentData class
2. `lib/providers/base.py` - Remove deprecated field population, add null checks, improve type hints

### Provider Files (2 files)
1. `lib/providers/aniworld.py` - Replace broad exception catching
2. `lib/providers/serienstream.py` - Replace broad exception catching

### Test Files (2 files)
1. `tests/providers/test_api_endpoints.py` - Update test assertions
2. `tests/providers/__init__.py` - Clean up empty file

**Total Files to Modify: 9**

---

## Breaking Changes Summary

### For API Consumers

**BREAKING CHANGES - These fields are REMOVED:**

#### 1. Paginated Responses
**Removed root-level fields:**
- `page` (use `pagination.page` instead)
- `per_page` (use `pagination.per_page` instead)
- `has_next` (use `pagination.has_next` instead)
- `has_previous` (use `pagination.has_previous` instead)

**Migration:**
```javascript
// OLD
const page = response.page;
const hasNext = response.has_next;

// NEW
const page = response.pagination.page;
const hasNext = response.pagination.has_next;
```

#### 2. Series Endpoints
**Removed root-level fields:**
- `tmdb_enrichment` (use `tmdb_series_data` and `match_confidence` instead)
- `tmdb_season` in SeasonResponse (use `season.tmdb_season_data` instead)
- `tmdb_episode` in EpisodeResponse (use `episode.tmdb_episode_data` instead)

**Migration for Series Overview:**
```javascript
// OLD
const tmdbData = response.tmdb_enrichment.tmdb_data;
const confidence = response.tmdb_enrichment.match_confidence;

// NEW
const tmdbData = response.tmdb_series_data;
const confidence = response.match_confidence;
```

**Migration for Episode Data:**
```javascript
// OLD
const episodeName = response.tmdb_episode.name;
const episodeOverview = response.tmdb_episode.overview;

// NEW
const episodeName = response.episode.tmdb_episode_data.name;
const episodeOverview = response.episode.tmdb_episode_data.overview;
```

#### 3. Episode Structure in Season Lists
**Old structure (flat TMDB fields):**
```json
{
  "episode": 1,
  "title": "Episode Title",
  "tmdb_id": 12345,
  "tmdb_overview": "...",
  "tmdb_vote_average": 8.2
}
```

**New structure (nested tmdb_episode_data):**
```json
{
  "episode": 1,
  "title": "Episode Title",
  "tmdb_episode_data": {
    "id": 12345,
    "overview": "...",
    "vote_average": 8.2
  }
}
```

---

## Validation Checklist

Before marking this refactoring complete, verify:

- [ ] All deprecated fields removed from response models
- [ ] No code populates deprecated fields
- [ ] `TMDBEnrichmentData` class deleted
- [ ] EXAMPLES.md shows correct structure for all endpoints
- [ ] API.md verified accurate
- [ ] current_structure.json matches actual responses
- [ ] All tests pass
- [ ] Manual API testing confirms correct structure
- [ ] No breaking changes to non-deprecated fields
- [ ] Documentation clearly indicates this is v2.0.0 (breaking changes)

---

## Additional Improvements (Optional - Not Blocking)

### Low Priority Tasks

1. **Performance Optimization** (`series.py` lines 152-160)
   - Consider parallelizing TMDB API calls when enriching multiple seasons
   - Current implementation is sequential


---

## Next Steps

1. Review this plan with team
2. Create feature branch from current branch
3. Execute Phase 1 (Documentation) first
4. Execute Phase 2 (Remove deprecated fields)
5. Execute Phase 3 (Code quality improvements)
6. Execute Phase 4 (Testing)
7. Code review
8. Merge to main
9. Update API version to v2.0.0
10. Notify frontend team of breaking changes

---

**Plan Created By:** Claude Code Review Agent
**Last Updated:** 2025-12-19
