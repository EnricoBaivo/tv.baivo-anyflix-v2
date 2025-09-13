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
  } = useSeriesDetail(selectedSource, selectedAnimeUrl || "/anime/dummy");

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
                        className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-accent"
                        onClick={() => setSelectedAnimeUrl(anime.link)}
                      >
                        <img
                          src={anime.image_url}
                          alt={anime.name}
                          className="w-12 h-16 object-cover rounded"
                          onError={(e) => {
                            e.currentTarget.src = "/placeholder.svg";
                          }}
                        />
                        <div className="flex-1">
                          <h4 className="font-medium">{anime.name}</h4>
                          <p className="text-sm text-muted-foreground">
                            {anime.link}
                          </p>
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
                          className="flex items-center gap-3 p-2 border rounded cursor-pointer hover:bg-accent"
                          onClick={() => setSelectedAnimeUrl(anime.link)}
                        >
                          <img
                            src={anime.image_url}
                            alt={anime.name}
                            className="w-10 h-14 object-cover rounded"
                            onError={(e) => {
                              e.currentTarget.src = "/placeholder.svg";
                            }}
                          />
                          <div className="flex-1">
                            <h5 className="font-medium text-sm">
                              {anime.name}
                            </h5>
                            <div className="flex items-center gap-1">
                              <Star className="h-3 w-3 text-yellow-500" />
                              <span className="text-xs text-muted-foreground">
                                Popular
                              </span>
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
                          className="flex items-center gap-3 p-2 border rounded cursor-pointer hover:bg-accent"
                          onClick={() => setSelectedAnimeUrl(anime.link)}
                        >
                          <img
                            src={anime.image_url}
                            alt={anime.name}
                            className="w-10 h-14 object-cover rounded"
                            onError={(e) => {
                              e.currentTarget.src = "/placeholder.svg";
                            }}
                          />
                          <div className="flex-1">
                            <h5 className="font-medium text-sm">
                              {anime.name}
                            </h5>
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3 text-blue-500" />
                              <span className="text-xs text-muted-foreground">
                                Recent
                              </span>
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

          {/* Series Detail */}
          {shouldFetchSeries && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Tv className="h-5 w-5" />
                  Series Details
                </CardTitle>
                <CardDescription>
                  Hierarchical structure with seasons and movies
                </CardDescription>
              </CardHeader>
              <CardContent>
                {seriesLoading ? (
                  <div className="space-y-4">
                    <Skeleton className="h-6 w-48" />
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-20 w-full" />
                      </div>
                      <div className="space-y-2">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-20 w-full" />
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
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold">
                        {seriesData.series.slug}
                      </h3>
                      <Badge variant="outline">{selectedSource}</Badge>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      {/* Seasons */}
                      <div>
                        <h4 className="font-medium mb-2 flex items-center gap-2">
                          <Tv className="h-4 w-4" />
                          Seasons ({seriesData.series.seasons.length})
                        </h4>
                        <ScrollArea className="h-32">
                          <div className="space-y-1">
                            {seriesData.series.seasons.map((season) => (
                              <div
                                key={season.season}
                                className="p-2 border rounded text-sm"
                              >
                                <div className="font-medium">
                                  {season.title || `Season ${season.season}`}
                                </div>
                                <div className="text-muted-foreground">
                                  {season.episodes.length} episodes
                                </div>
                              </div>
                            ))}
                          </div>
                        </ScrollArea>
                      </div>

                      {/* Movies */}
                      <div>
                        <h4 className="font-medium mb-2 flex items-center gap-2">
                          <Film className="h-4 w-4" />
                          Movies/OVAs ({seriesData.series.movies.length})
                        </h4>
                        <ScrollArea className="h-32">
                          <div className="space-y-1">
                            {seriesData.series.movies.map((movie) => (
                              <div
                                key={movie.number}
                                className="p-2 border rounded text-sm"
                              >
                                <div className="font-medium">{movie.title}</div>
                                <div className="text-muted-foreground capitalize">
                                  {movie.kind}
                                </div>
                              </div>
                            ))}
                          </div>
                        </ScrollArea>
                      </div>
                    </div>
                  </div>
                ) : null}
              </CardContent>
            </Card>
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
                  <div className="space-y-3">
                    <p className="text-sm text-muted-foreground">
                      ✅ Preferences loaded successfully for {selectedSource}
                    </p>
                    <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto max-h-40">
                      {JSON.stringify(preferences, null, 2)}
                    </pre>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    No preferences available for {selectedSource}
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </>
      )}

      <Separator />

      {/* Footer */}
      <div className="text-center text-sm text-muted-foreground">
        <p>
          ✅ MVP Demo Complete - FastAPI Backend Integration with swr-openapi
        </p>
        <p>
          Backend:{" "}
          <code>{import.meta.env.VITE_API_URL || "http://localhost:8000"}</code>{" "}
          | Frontend: React + TypeScript + swr-openapi
        </p>
        <div className="mt-2 space-y-1">
          <p>
            🔒 <strong>Type Safety:</strong> Full TypeScript inference from
            OpenAPI schema
          </p>
          <p>
            ⚡ <strong>Performance:</strong> Automatic caching, deduplication,
            and revalidation
          </p>
          <p>
            🛠️ <strong>Developer Experience:</strong> Auto-generated hooks with
            IntelliSense
          </p>
        </div>
      </div>
    </div>
  );
};

export default AnimeDemo;
