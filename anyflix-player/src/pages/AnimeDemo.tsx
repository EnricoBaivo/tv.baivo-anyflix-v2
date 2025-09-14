/**
 * MVP Demo Component for Anime Backend Integration
 * Demonstrates connectivity to FastAPI backend using swr-openapi
 */

import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Play,
  Search,
  TrendingUp,
  Clock,
  Server,
  CheckCircle,
  XCircle,
  Loader2,
  Film,
  Tv,
  Star,
  Calendar,
  Users,
  Trophy,
  Globe,
  Heart,
  Eye,
  Info,
  Tag,
  Bookmark,
  ExternalLink,
  PlayCircle,
  Image as ImageIcon,
  User,
  Building,
  MapPin,
  Languages,
  Award,
  Zap,
  ThumbsUp,
  Clock4,
  Palette,
  Monitor,
} from "lucide-react";

// Import new type-safe API hooks
import {
  useSources,
  usePopular,
  useLatest,
  useSearch,
  useSearchConditional,
  useSeriesDetail,
  useSourcePreferences,
} from "@/lib/api/hooks";
import { useQuery } from "@/lib/api/client";

const AnimeDemo: React.FC = () => {
  const [selectedSource, setSelectedSource] = useState<string>("aniworld");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedAnimeUrl, setSelectedAnimeUrl] = useState<string>("");

  // Health check using direct query hook
  const {
    data: healthData,
    error: healthError,
    isLoading: healthLoading,
  } = useQuery("/health", {});
  const isHealthy = !healthError && !healthLoading;

  // Sources - type-safe with new hook
  const {
    data: sourcesData,
    error: sourcesError,
    isLoading: sourcesLoading,
  } = useSources();

  // Popular content for selected source
  const {
    data: popular,
    error: popularError,
    isLoading: popularLoading,
  } = usePopular(selectedSource, 1);

  // Latest content for selected source
  const {
    data: latest,
    error: latestError,
    isLoading: latestLoading,
  } = useLatest(selectedSource, 1);

  // Source preferences
  const {
    data: preferences,
    error: preferencesError,
    isLoading: preferencesLoading,
  } = useSourcePreferences(selectedSource);

  // Search results - only search when query is long enough
  const {
    data: searchResults,
    error: searchError,
    isLoading: searchLoading,
  } = useSearchConditional(
    selectedSource,
    searchQuery,
    1,
    searchQuery.length >= 2
  );

  // Series detail for selected anime - only fetch when URL is selected
  const shouldFetchSeries = selectedAnimeUrl && selectedAnimeUrl.length > 0;
  const {
    data: seriesData,
    error: seriesError,
    isLoading: seriesLoading,
  } = useSeriesDetail(selectedSource, selectedAnimeUrl);
  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Anime Backend Integration Demo</h1>
        <p className="text-muted-foreground">
          MVP demonstration of FastAPI backend connectivity using SWR
        </p>
      </div>

      {/* Health Check */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            Backend Health Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            {healthLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : isHealthy ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <XCircle className="h-4 w-4 text-red-500" />
            )}
            <span
              className={`font-medium ${
                isHealthy ? "text-green-700" : "text-red-700"
              }`}
            >
              {healthLoading
                ? "Checking..."
                : isHealthy
                ? "Connected"
                : "Disconnected"}
            </span>
            {!healthLoading && (
              <Badge variant={isHealthy ? "default" : "destructive"}>
                {isHealthy ? "FastAPI Backend Online" : "Backend Offline"}
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Sources Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Available Anime Sources</CardTitle>
          <CardDescription>
            Select a source to explore anime content
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sourcesLoading ? (
            <div className="flex gap-2">
              <Skeleton className="h-10 w-24" />
              <Skeleton className="h-10 w-32" />
            </div>
          ) : sourcesError ? (
            <Alert variant="destructive">
              <XCircle className="h-4 w-4" />
              <AlertDescription>
                Failed to load sources: {String(sourcesError)}
              </AlertDescription>
            </Alert>
          ) : (
            <div className="flex gap-2 flex-wrap">
              {/* Hard-coded sources for now since the API response structure may vary */}
              {["aniworld", "serienstream"].map((source) => (
                <Button
                  key={source}
                  variant={selectedSource === source ? "default" : "outline"}
                  onClick={() => setSelectedSource(source)}
                  className="capitalize"
                >
                  {source}
                </Button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {selectedSource && (
        <>
          {/* Search */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                Search Anime
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  placeholder="Search for anime..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1"
                />
                <Button disabled={!searchQuery.trim() || searchLoading}>
                  {searchLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                </Button>
              </div>

              {searchError && searchQuery.length >= 2 && (
                <Alert variant="destructive" className="mt-4">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription>
                    Search failed:{" "}
                    {searchError?.detail?.[0]?.msg || "Unknown error"}
                  </AlertDescription>
                </Alert>
              )}

              {searchResults && searchQuery.length >= 2 && (
                <ScrollArea className="h-48 mt-4">
                  <div className="space-y-2">
                    {searchResults.list.map((anime, index) => (
                      <div
                        key={index}
                        className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-accent transition-colors"
                        onClick={() => setSelectedAnimeUrl(anime.link)}
                      >
                        <img
                          src={anime.image_url}
                          alt={anime.name}
                          className="w-16 h-20 object-cover rounded flex-shrink-0"
                          onError={(e) => {
                            e.currentTarget.src = "/placeholder.svg";
                          }}
                        />
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium mb-1 line-clamp-2">
                            {anime.name}
                          </h4>

                          {/* Enhanced metadata display */}
                          <div className="space-y-2">
                            {anime.anilist_data && (
                              <div className="flex items-center gap-3 text-xs">
                                {anime.anilist_data.averageScore && (
                                  <div className="flex items-center gap-1">
                                    <Star className="h-3 w-3 text-yellow-500" />
                                    <span className="font-medium">
                                      {anime.anilist_data.averageScore}%
                                    </span>
                                  </div>
                                )}
                                {anime.anilist_data.episodes && (
                                  <div className="flex items-center gap-1">
                                    <Tv className="h-3 w-3 text-blue-500" />
                                    <span>
                                      {anime.anilist_data.episodes} eps
                                    </span>
                                  </div>
                                )}
                                {anime.anilist_data.status && (
                                  <Badge
                                    variant="outline"
                                    className="text-xs py-0 px-1 h-4"
                                  >
                                    {anime.anilist_data.status.toLowerCase()}
                                  </Badge>
                                )}
                              </div>
                            )}

                            {anime.tmdb_data && (
                              <div className="flex items-center gap-3 text-xs">
                                {anime.tmdb_data.vote_average && (
                                  <div className="flex items-center gap-1">
                                    <ThumbsUp className="h-3 w-3 text-green-500" />
                                    <span className="font-medium">
                                      {anime.tmdb_data.vote_average.toFixed(1)}
                                    </span>
                                  </div>
                                )}
                                {"release_date" in anime.tmdb_data &&
                                  anime.tmdb_data.release_date && (
                                    <div className="flex items-center gap-1">
                                      <Calendar className="h-3 w-3 text-purple-500" />
                                      <span>
                                        {new Date(
                                          anime.tmdb_data.release_date
                                        ).getFullYear()}
                                      </span>
                                    </div>
                                  )}
                                {"first_air_date" in anime.tmdb_data &&
                                  anime.tmdb_data.first_air_date && (
                                    <div className="flex items-center gap-1">
                                      <Calendar className="h-3 w-3 text-purple-500" />
                                      <span>
                                        {new Date(
                                          anime.tmdb_data.first_air_date
                                        ).getFullYear()}
                                      </span>
                                    </div>
                                  )}
                              </div>
                            )}

                            {/* Description preview */}
                            {(anime.anilist_data?.description ||
                              anime.tmdb_data?.overview) && (
                              <p className="text-xs text-muted-foreground line-clamp-2">
                                {anime.anilist_data?.description?.replace(
                                  /<[^>]*>/g,
                                  ""
                                ) || anime.tmdb_data?.overview}
                              </p>
                            )}

                            {/* Genres */}
                            {(anime.anilist_data?.genres ||
                              anime.tmdb_data?.genres) && (
                              <div className="flex flex-wrap gap-1">
                                {(
                                  anime.anilist_data?.genres ||
                                  anime.tmdb_data?.genres?.map((g) =>
                                    "name" in g ? g.name : g
                                  ) ||
                                  []
                                )
                                  .slice(0, 3)
                                  .map((genre, i) => (
                                    <Badge
                                      key={i}
                                      variant="secondary"
                                      className="text-xs py-0 px-1 h-4"
                                    >
                                      {typeof genre === "string"
                                        ? genre
                                        : genre}
                                    </Badge>
                                  ))}
                              </div>
                            )}

                            {anime.match_confidence && (
                              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                <Zap className="h-3 w-3" />
                                <span>
                                  Match:{" "}
                                  {(anime.match_confidence * 100).toFixed(0)}%
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                        <Button size="sm" variant="ghost">
                          <Play className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>

          {/* Popular and Latest */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Popular Anime */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Popular Anime
                </CardTitle>
              </CardHeader>
              <CardContent>
                {popularLoading ? (
                  <div className="space-y-3">
                    {[...Array(3)].map((_, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <Skeleton className="w-12 h-16" />
                        <div className="flex-1 space-y-1">
                          <Skeleton className="h-4 w-full" />
                          <Skeleton className="h-3 w-2/3" />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : popularError ? (
                  <Alert variant="destructive">
                    <XCircle className="h-4 w-4" />
                    <AlertDescription>
                      Failed to load popular anime:{" "}
                      {popularError?.detail?.[0]?.msg || "Unknown error"}
                    </AlertDescription>
                  </Alert>
                ) : (
                  <ScrollArea className="h-64">
                    <div className="space-y-2">
                      {popular?.list.slice(0, 5).map((anime, index) => (
                        <div
                          key={index}
                          className="flex items-start gap-3 p-3 border rounded cursor-pointer hover:bg-accent transition-colors"
                          onClick={() => setSelectedAnimeUrl(anime.link)}
                        >
                          <img
                            src={anime.image_url}
                            alt={anime.name}
                            className="w-12 h-16 object-cover rounded flex-shrink-0"
                            onError={(e) => {
                              e.currentTarget.src = "/placeholder.svg";
                            }}
                          />
                          <div className="flex-1 min-w-0">
                            <h5 className="font-medium text-sm mb-1 line-clamp-2">
                              {anime.name}
                            </h5>

                            {/* Enhanced metadata display */}
                            <div className="space-y-1">
                              {anime.anilist_data && (
                                <div className="flex items-center gap-2 text-xs">
                                  {anime.anilist_data.averageScore && (
                                    <div className="flex items-center gap-1">
                                      <Star className="h-3 w-3 text-yellow-500" />
                                      <span className="font-medium">
                                        {anime.anilist_data.averageScore}%
                                      </span>
                                    </div>
                                  )}
                                  {anime.anilist_data.episodes && (
                                    <div className="flex items-center gap-1">
                                      <Tv className="h-3 w-3 text-blue-500" />
                                      <span>
                                        {anime.anilist_data.episodes} eps
                                      </span>
                                    </div>
                                  )}
                                  {anime.anilist_data.status && (
                                    <Badge
                                      variant="outline"
                                      className="text-xs py-0 px-1 h-4"
                                    >
                                      {anime.anilist_data.status.toLowerCase()}
                                    </Badge>
                                  )}
                                </div>
                              )}

                              {anime.tmdb_data && (
                                <div className="flex items-center gap-2 text-xs">
                                  {anime.tmdb_data?.vote_average && (
                                    <div className="flex items-center gap-1">
                                      <ThumbsUp className="h-3 w-3 text-green-500" />
                                      <span className="font-medium">
                                        {anime.tmdb_data.vote_average.toFixed(
                                          1
                                        )}
                                      </span>
                                    </div>
                                  )}
                                  {"release_date" in anime.tmdb_data &&
                                    anime.tmdb_data?.release_date && (
                                      <div className="flex items-center gap-1">
                                        <Calendar className="h-3 w-3 text-purple-500" />
                                        <span>
                                          {new Date(
                                            anime.tmdb_data.release_date
                                          ).getFullYear()}
                                        </span>
                                      </div>
                                    )}
                                  {"first_air_date" in anime.tmdb_data &&
                                    anime.tmdb_data?.first_air_date && (
                                      <div className="flex items-center gap-1">
                                        <Calendar className="h-3 w-3 text-purple-500" />
                                        <span>
                                          {new Date(
                                            anime.tmdb_data.first_air_date
                                          ).getFullYear()}
                                        </span>
                                      </div>
                                    )}
                                </div>
                              )}

                              {anime.match_confidence && (
                                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                  <Zap className="h-3 w-3" />
                                  <span>
                                    Match:{" "}
                                    {(anime.match_confidence * 100).toFixed(0)}%
                                  </span>
                                </div>
                              )}

                              {/* Genres */}
                              {(anime.anilist_data?.genres ||
                                anime.tmdb_data?.genres) && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {(
                                    anime.anilist_data?.genres ||
                                    anime.tmdb_data?.genres?.map((g) =>
                                      "name" in g ? g.name : g
                                    ) ||
                                    []
                                  )
                                    .slice(0, 2)
                                    .map((genre, i) => (
                                      <Badge
                                        key={i}
                                        variant="secondary"
                                        className="text-xs py-0 px-1 h-4"
                                      >
                                        {typeof genre === "string"
                                          ? genre
                                          : genre}
                                      </Badge>
                                    ))}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </CardContent>
            </Card>

            {/* Latest Updates */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Latest Updates
                </CardTitle>
              </CardHeader>
              <CardContent>
                {latestLoading ? (
                  <div className="space-y-3">
                    {[...Array(3)].map((_, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <Skeleton className="w-12 h-16" />
                        <div className="flex-1 space-y-1">
                          <Skeleton className="h-4 w-full" />
                          <Skeleton className="h-3 w-2/3" />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : latestError ? (
                  <Alert variant="destructive">
                    <XCircle className="h-4 w-4" />
                    <AlertDescription>
                      Failed to load latest updates:{" "}
                      {latestError?.detail?.[0]?.msg || "Unknown error"}
                    </AlertDescription>
                  </Alert>
                ) : (
                  <ScrollArea className="h-64">
                    <div className="space-y-2">
                      {latest?.list.slice(0, 5).map((anime, index) => (
                        <div
                          key={index}
                          className="flex items-start gap-3 p-3 border rounded cursor-pointer hover:bg-accent transition-colors"
                          onClick={() => setSelectedAnimeUrl(anime.link)}
                        >
                          <img
                            src={anime.image_url}
                            alt={anime.name}
                            className="w-12 h-16 object-cover rounded flex-shrink-0"
                            onError={(e) => {
                              e.currentTarget.src = "/placeholder.svg";
                            }}
                          />
                          <div className="flex-1 min-w-0">
                            <h5 className="font-medium text-sm mb-1 line-clamp-2">
                              {anime.name}
                            </h5>

                            {/* Enhanced metadata display */}
                            <div className="space-y-1">
                              {anime.anilist_data && (
                                <div className="flex items-center gap-2 text-xs">
                                  {anime.anilist_data.averageScore && (
                                    <div className="flex items-center gap-1">
                                      <Star className="h-3 w-3 text-yellow-500" />
                                      <span className="font-medium">
                                        {anime.anilist_data.averageScore}%
                                      </span>
                                    </div>
                                  )}
                                  {anime.anilist_data.episodes && (
                                    <div className="flex items-center gap-1">
                                      <Tv className="h-3 w-3 text-blue-500" />
                                      <span>
                                        {anime.anilist_data.episodes} eps
                                      </span>
                                    </div>
                                  )}
                                  {anime.anilist_data.status && (
                                    <Badge
                                      variant="outline"
                                      className="text-xs py-0 px-1 h-4"
                                    >
                                      {anime.anilist_data.status.toLowerCase()}
                                    </Badge>
                                  )}
                                </div>
                              )}

                              {anime.tmdb_data && (
                                <div className="flex items-center gap-2 text-xs">
                                  {anime.tmdb_data?.vote_average && (
                                    <div className="flex items-center gap-1">
                                      <ThumbsUp className="h-3 w-3 text-green-500" />
                                      <span className="font-medium">
                                        {anime.tmdb_data.vote_average.toFixed(
                                          1
                                        )}
                                      </span>
                                    </div>
                                  )}
                                  {"release_date" in anime.tmdb_data &&
                                    anime.tmdb_data?.release_date && (
                                      <div className="flex items-center gap-1">
                                        <Calendar className="h-3 w-3 text-purple-500" />
                                        <span>
                                          {new Date(
                                            anime.tmdb_data.release_date
                                          ).getFullYear()}
                                        </span>
                                      </div>
                                    )}
                                  {"first_air_date" in anime.tmdb_data &&
                                    anime.tmdb_data?.first_air_date && (
                                      <div className="flex items-center gap-1">
                                        <Calendar className="h-3 w-3 text-purple-500" />
                                        <span>
                                          {new Date(
                                            anime.tmdb_data.first_air_date
                                          ).getFullYear()}
                                        </span>
                                      </div>
                                    )}
                                </div>
                              )}

                              {anime.match_confidence && (
                                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                  <Zap className="h-3 w-3" />
                                  <span>
                                    Match:{" "}
                                    {(anime.match_confidence * 100).toFixed(0)}%
                                  </span>
                                </div>
                              )}

                              {/* Genres */}
                              {(anime.anilist_data?.genres ||
                                anime.tmdb_data?.genres) && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {(
                                    anime.anilist_data?.genres ||
                                    anime.tmdb_data?.genres?.map((g) =>
                                      "name" in g ? g.name : g
                                    ) ||
                                    []
                                  )
                                    .slice(0, 2)
                                    .map((genre, i) => (
                                      <Badge
                                        key={i}
                                        variant="secondary"
                                        className="text-xs py-0 px-1 h-4"
                                      >
                                        {typeof genre === "string"
                                          ? genre
                                          : genre}
                                      </Badge>
                                    ))}
                                </div>
                              )}

                              {/* Recent indicator */}
                              <div className="flex items-center gap-1 text-xs text-blue-600">
                                <Clock className="h-3 w-3" />
                                <span>Recent Update</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Enhanced Series Detail */}
          {shouldFetchSeries && (
            <div className="space-y-6">
              {/* Main Series Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Info className="h-5 w-5" />
                    Detailed Series Information
                  </CardTitle>
                  <CardDescription>
                    Comprehensive metadata from multiple sources
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {seriesLoading ? (
                    <div className="space-y-4">
                      <div className="flex gap-4">
                        <Skeleton className="w-32 h-48" />
                        <div className="flex-1 space-y-2">
                          <Skeleton className="h-6 w-3/4" />
                          <Skeleton className="h-4 w-full" />
                          <Skeleton className="h-4 w-full" />
                          <Skeleton className="h-4 w-2/3" />
                        </div>
                      </div>
                    </div>
                  ) : seriesError ? (
                    <Alert variant="destructive">
                      <XCircle className="h-4 w-4" />
                      <AlertDescription>
                        Failed to load series details:{" "}
                        {seriesError?.detail?.[0]?.msg || "Unknown error"}
                      </AlertDescription>
                    </Alert>
                  ) : seriesData ? (
                    <div className="space-y-6">
                      {/* Header with cover and basic info */}
                      <div className="flex gap-6">
                        {/* Cover Image */}
                        <div className="flex-shrink-0">
                          <img
                            src={
                              seriesData.anilist_data?.coverImage?.large ||
                              (seriesData.tmdb_data?.poster_path
                                ? `https://image.tmdb.org/t/p/w500${seriesData.tmdb_data.poster_path}`
                                : "/placeholder.svg")
                            }
                            alt={seriesData.series.slug}
                            className="w-32 h-48 object-cover rounded-lg"
                            onError={(e) => {
                              e.currentTarget.src = "/placeholder.svg";
                            }}
                          />
                        </div>

                        {/* Basic Information */}
                        <div className="flex-1 space-y-4">
                          <div>
                            <h3 className="text-2xl font-bold mb-2">
                              {seriesData.anilist_data?.title?.userPreferred ||
                                seriesData.anilist_data?.title?.english ||
                                seriesData.anilist_data?.title?.romaji ||
                                (seriesData.tmdb_data &&
                                "title" in seriesData.tmdb_data
                                  ? seriesData.tmdb_data.title
                                  : null) ||
                                (seriesData.tmdb_data &&
                                "name" in seriesData.tmdb_data
                                  ? seriesData.tmdb_data.name
                                  : null) ||
                                seriesData.series.slug}
                            </h3>
                          </div>

                          {/* Key Statistics */}
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {/* AniList Score */}
                            {seriesData.anilist_data?.averageScore && (
                              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                                <div className="flex items-center justify-center gap-1 mb-1">
                                  <Star className="h-4 w-4 text-yellow-500" />
                                  <span className="text-xs font-medium">
                                    AniList
                                  </span>
                                </div>
                                <div className="text-lg font-bold text-yellow-700">
                                  {seriesData.anilist_data.averageScore}%
                                </div>
                              </div>
                            )}

                            {/* TMDB Score */}
                            {seriesData.tmdb_data?.vote_average && (
                              <div className="text-center p-3 bg-green-50 rounded-lg">
                                <div className="flex items-center justify-center gap-1 mb-1">
                                  <ThumbsUp className="h-4 w-4 text-green-500" />
                                  <span className="text-xs font-medium">
                                    TMDB
                                  </span>
                                </div>
                                <div className="text-lg font-bold text-green-700">
                                  {seriesData.tmdb_data?.vote_average?.toFixed(
                                    1
                                  )}
                                </div>
                              </div>
                            )}

                            {/* Episodes */}
                            {seriesData.anilist_data?.episodes && (
                              <div className="text-center p-3 bg-blue-50 rounded-lg">
                                <div className="flex items-center justify-center gap-1 mb-1">
                                  <Tv className="h-4 w-4 text-blue-500" />
                                  <span className="text-xs font-medium">
                                    Episodes
                                  </span>
                                </div>
                                <div className="text-lg font-bold text-blue-700">
                                  {seriesData.anilist_data.episodes}
                                </div>
                              </div>
                            )}

                            {/* Popularity */}
                            {seriesData.anilist_data?.popularity && (
                              <div className="text-center p-3 bg-purple-50 rounded-lg">
                                <div className="flex items-center justify-center gap-1 mb-1">
                                  <Heart className="h-4 w-4 text-purple-500" />
                                  <span className="text-xs font-medium">
                                    Popular
                                  </span>
                                </div>
                                <div className="text-lg font-bold text-purple-700">
                                  {seriesData.anilist_data.popularity.toLocaleString()}
                                </div>
                              </div>
                            )}
                          </div>

                          {/* Status and Format */}
                          <div className="flex flex-wrap gap-2">
                            <Badge
                              variant="outline"
                              className="flex items-center gap-1"
                            >
                              <Monitor className="h-3 w-3" />
                              {selectedSource}
                            </Badge>
                            {seriesData.anilist_data?.status && (
                              <Badge
                                variant={
                                  seriesData.anilist_data.status === "RELEASING"
                                    ? "default"
                                    : "secondary"
                                }
                                className="flex items-center gap-1"
                              >
                                <Clock4 className="h-3 w-3" />
                                {seriesData.anilist_data.status
                                  .toLowerCase()
                                  .replace("_", " ")}
                              </Badge>
                            )}
                            {seriesData.match_confidence && (
                              <Badge
                                variant="outline"
                                className="flex items-center gap-1"
                              >
                                <Zap className="h-3 w-3" />
                                {(seriesData.match_confidence * 100).toFixed(0)}
                                % match
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Description */}
                      {(seriesData.anilist_data?.description ||
                        seriesData.tmdb_data?.overview) && (
                        <div>
                          <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <Info className="h-4 w-4" />
                            Synopsis
                          </h4>
                          <p className="text-sm text-muted-foreground leading-relaxed">
                            {seriesData.anilist_data?.description?.replace(
                              /<[^>]*>/g,
                              ""
                            ) || seriesData.tmdb_data?.overview}
                          </p>
                        </div>
                      )}

                      {/* Genres */}
                      {(seriesData.anilist_data?.genres ||
                        seriesData.tmdb_data?.genres) && (
                        <div>
                          <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <Tag className="h-4 w-4" />
                            Genres
                          </h4>
                          <div className="flex flex-wrap gap-1">
                            {(
                              seriesData.anilist_data?.genres ||
                              seriesData.tmdb_data?.genres?.map((g) =>
                                "name" in g ? g.name : g
                              ) ||
                              []
                            ).map((genre, i) => (
                              <Badge key={i} variant="secondary">
                                {typeof genre === "string" ? genre : genre}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : null}
                </CardContent>
              </Card>

              {/* Series Structure */}
              {seriesData && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Tv className="h-5 w-5" />
                      Series Structure
                    </CardTitle>
                    <CardDescription>
                      Hierarchical organization of seasons, episodes, and movies
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 gap-6">
                      {/* Seasons */}
                      <div>
                        <h4 className="font-medium mb-3 flex items-center gap-2">
                          <Tv className="h-4 w-4" />
                          Seasons ({seriesData.series.seasons.length})
                        </h4>
                        <ScrollArea className="h-64">
                          <div className="space-y-2">
                            {seriesData.series.seasons.map((season) => (
                              <div
                                key={season.season}
                                className="p-3 border rounded-lg hover:bg-accent transition-colors"
                              >
                                <div className="flex items-center justify-between mb-2">
                                  <div className="font-medium">
                                    {season.title || `Season ${season.season}`}
                                  </div>
                                  <Badge variant="secondary">
                                    {season.episodes.length} eps
                                  </Badge>
                                </div>
                                <div className="text-xs text-muted-foreground space-y-1">
                                  <div>
                                    Episodes:{" "}
                                    {season.episodes
                                      .map((ep) => `${ep.episode}`)
                                      .join(", ")}
                                  </div>
                                  {season.episodes.some(
                                    (ep) => ep.date_upload
                                  ) && (
                                    <div>
                                      Latest:{" "}
                                      {
                                        season.episodes.find(
                                          (ep) => ep.date_upload
                                        )?.date_upload
                                      }
                                    </div>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </ScrollArea>
                      </div>

                      {/* Movies/OVAs/Specials */}
                      <div>
                        <h4 className="font-medium mb-3 flex items-center gap-2">
                          <Film className="h-4 w-4" />
                          Movies/OVAs/Specials (
                          {seriesData.series.movies.length})
                        </h4>
                        <ScrollArea className="h-64">
                          <div className="space-y-2">
                            {seriesData.series.movies.map((movie) => (
                              <div
                                key={movie.number}
                                className="p-3 border rounded-lg hover:bg-accent transition-colors"
                              >
                                <div className="flex items-start justify-between mb-2">
                                  <div className="font-medium line-clamp-2 flex-1">
                                    {movie.title}
                                  </div>
                                  <Badge
                                    variant={
                                      movie.kind === "movie"
                                        ? "default"
                                        : "secondary"
                                    }
                                    className="ml-2 capitalize"
                                  >
                                    {movie.kind}
                                  </Badge>
                                </div>
                                <div className="text-xs text-muted-foreground space-y-1">
                                  <div>Number: {movie.number}</div>
                                  {movie.date_upload && (
                                    <div>Uploaded: {movie.date_upload}</div>
                                  )}
                                  {movie.tags.length > 0 && (
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {movie.tags.slice(0, 3).map((tag, i) => (
                                        <Badge
                                          key={i}
                                          variant="outline"
                                          className="text-xs py-0 px-1 h-4"
                                        >
                                          {tag}
                                        </Badge>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </ScrollArea>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Source Preferences */}
          {selectedSource && (
            <Card>
              <CardHeader>
                <CardTitle>Source Preferences</CardTitle>
                <CardDescription>
                  Configuration options for {selectedSource}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {preferencesLoading ? (
                  <div className="space-y-3">
                    {[...Array(2)].map((_, i) => (
                      <div key={i} className="p-3 border rounded">
                        <Skeleton className="h-4 w-32 mb-2" />
                        <div className="flex gap-2">
                          <Skeleton className="h-6 w-16" />
                          <Skeleton className="h-6 w-20" />
                          <Skeleton className="h-6 w-14" />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : preferencesError ? (
                  <Alert variant="destructive">
                    <XCircle className="h-4 w-4" />
                    <AlertDescription>
                      Failed to load preferences:{" "}
                      {preferencesError?.detail?.[0]?.msg || "Unknown error"}
                    </AlertDescription>
                  </Alert>
                ) : preferences ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm font-medium">
                        Configuration loaded for {selectedSource}
                      </span>
                    </div>

                    {/* Display preferences in a more readable format */}
                    <div className="grid gap-4">
                      {Object.entries(preferences.preferences || {}).map(
                        ([key, pref]) => {
                          const prefData = pref as Record<string, unknown>; // Type assertion for preferences data
                          return (
                            <div key={key} className="p-4 border rounded-lg">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge variant="outline">{key}</Badge>
                              </div>

                              {/* List preference */}
                              {prefData?.list_preference && (
                                <div className="space-y-2">
                                  <h5 className="text-sm font-medium">
                                    List Options:
                                  </h5>
                                  <div className="flex flex-wrap gap-1">
                                    {(
                                      ((
                                        prefData.list_preference as Record<
                                          string,
                                          unknown
                                        >
                                      )?.entries as string[]) || []
                                    ).map((entry: string, i: number) => (
                                      <Badge
                                        key={i}
                                        variant="secondary"
                                        className="text-xs"
                                      >
                                        {entry}
                                      </Badge>
                                    ))}
                                  </div>
                                  {(
                                    prefData.list_preference as Record<
                                      string,
                                      unknown
                                    >
                                  )?.entry_values && (
                                    <p className="text-xs text-muted-foreground">
                                      Default:{" "}
                                      {
                                        (
                                          (
                                            prefData.list_preference as Record<
                                              string,
                                              unknown
                                            >
                                          ).entry_values as string[]
                                        )[0]
                                      }
                                    </p>
                                  )}
                                </div>
                              )}

                              {/* Multi-select preference */}
                              {prefData?.multi_select_list_preference && (
                                <div className="space-y-2">
                                  <h5 className="text-sm font-medium">
                                    Multi-select Options:
                                  </h5>
                                  <div className="flex flex-wrap gap-1">
                                    {(
                                      ((
                                        prefData.multi_select_list_preference as Record<
                                          string,
                                          unknown
                                        >
                                      )?.entries as string[]) || []
                                    ).map((entry: string, i: number) => (
                                      <Badge
                                        key={i}
                                        variant="outline"
                                        className="text-xs"
                                      >
                                        {entry}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          );
                        }
                      )}
                    </div>

                    {/* Raw JSON for debugging */}
                    <details className="mt-4">
                      <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground">
                        Show raw configuration
                      </summary>
                      <pre className="text-xs bg-muted p-3 rounded mt-2 overflow-auto max-h-40">
                        {JSON.stringify(preferences, null, 2)}
                      </pre>
                    </details>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <Info className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">
                      No preferences available for {selectedSource}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </>
      )}

      <Separator />

      {/* Additional API Capabilities */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5" />
            Additional API Capabilities
          </CardTitle>
          <CardDescription>
            More features available through your comprehensive anime backend
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <PlayCircle className="h-5 w-5 text-blue-500" />
                <h4 className="font-medium">Video Sources</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-2">
                Extract streaming URLs from multiple hosts with quality options
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  Multiple Hosts
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Quality Selection
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Subtitles
                </Badge>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <ExternalLink className="h-5 w-5 text-green-500" />
                <h4 className="font-medium">Trailer Extraction</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-2">
                Convert AniList/TMDB trailer data to streamable URLs
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  YouTube
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Direct URLs
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Quality Info
                </Badge>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Globe className="h-5 w-5 text-purple-500" />
                <h4 className="font-medium">Multi-Language</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-2">
                Support for multiple languages and subtitle options
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  Dub/Sub
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Multi-Lang
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Auto-Detect
                </Badge>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-5 w-5 text-orange-500" />
                <h4 className="font-medium">Smart Matching</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-2">
                AI-powered metadata matching with confidence scores
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  AniList
                </Badge>
                <Badge variant="outline" className="text-xs">
                  TMDB
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Confidence
                </Badge>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Building className="h-5 w-5 text-red-500" />
                <h4 className="font-medium">Multiple Sources</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-2">
                Support for various anime and series streaming sources
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  AniWorld
                </Badge>
                <Badge variant="outline" className="text-xs">
                  SerienStream
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Extensible
                </Badge>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Monitor className="h-5 w-5 text-teal-500" />
                <h4 className="font-medium">Hierarchical Data</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-2">
                Organized season/episode structure with movies and specials
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  Seasons
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Episodes
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Movies/OVAs
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Enhanced Footer */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2">
          <CheckCircle className="h-5 w-5 text-green-500" />
          <span className="text-lg font-semibold">Enhanced Demo Complete</span>
        </div>

        <div className="text-sm text-muted-foreground space-y-2">
          <p>
            <strong>Backend:</strong>{" "}
            <code className="bg-muted px-2 py-1 rounded">
              {import.meta.env.VITE_API_URL || "http://localhost:8000"}
            </code>
          </p>
          <p>
            <strong>Frontend:</strong> React + TypeScript + SWR + Tailwind CSS +
            shadcn/ui
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-4 mt-4 text-xs">
          <div className="p-3 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Zap className="h-4 w-4 text-yellow-500" />
              <span className="font-semibold">Rich Metadata</span>
            </div>
            <p className="text-muted-foreground">
              AniList + TMDB integration with scores, genres, descriptions, and
              more
            </p>
          </div>

          <div className="p-3 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Monitor className="h-4 w-4 text-blue-500" />
              <span className="font-semibold">Comprehensive UI</span>
            </div>
            <p className="text-muted-foreground">
              Enhanced cards, badges, statistics, and hierarchical data display
            </p>
          </div>

          <div className="p-3 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Award className="h-4 w-4 text-purple-500" />
              <span className="font-semibold">Production Ready</span>
            </div>
            <p className="text-muted-foreground">
              Type-safe, cached, error-handled with loading states
            </p>
          </div>
        </div>

        <div className="flex items-center justify-center gap-4 text-xs text-muted-foreground mt-4">
          <div className="flex items-center gap-1">
            <Star className="h-3 w-3" />
            <span>Ratings & Reviews</span>
          </div>
          <div className="flex items-center gap-1">
            <Tag className="h-3 w-3" />
            <span>Genres & Tags</span>
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            <span>Release Dates</span>
          </div>
          <div className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            <span>Popularity Stats</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnimeDemo;
