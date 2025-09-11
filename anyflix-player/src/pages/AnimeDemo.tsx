/**
 * MVP Demo Component for Anime Backend Integration
 * Demonstrates connectivity to FastAPI backend using SWR
 */

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { ScrollArea } from '@/components/ui/scroll-area';
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
  Star
} from 'lucide-react';

import {
  useSources,
  useSourcePreferences,
  usePopular,
  useLatest,
  useSearch,
  useSeriesDetail,
  useHealthCheck,
  useAnimeOverview,
} from '@/hooks/useAnime';

const AnimeDemo: React.FC = () => {
  const [selectedSource, setSelectedSource] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedAnimeUrl, setSelectedAnimeUrl] = useState<string>('');
  
  // Health check
  const { data: isHealthy, isLoading: healthLoading } = useHealthCheck();
  
  // Sources
  const { data: sourcesData, error: sourcesError, isLoading: sourcesLoading } = useSources();
  
  // Overview data for selected source
  const { 
    popular, 
    latest, 
    preferences, 
    loading, 
    errors 
  } = useAnimeOverview(selectedSource);
  
  // Search results
  const { 
    data: searchResults, 
    error: searchError, 
    isLoading: searchLoading 
  } = useSearch(
    selectedSource, 
    { q: searchQuery, page: 1 },
    { revalidateOnFocus: false }
  );
  
  // Series detail for selected anime
  const { 
    data: seriesData, 
    error: seriesError, 
    isLoading: seriesLoading 
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
            <span className={`font-medium ${isHealthy ? 'text-green-700' : 'text-red-700'}`}>
              {healthLoading ? 'Checking...' : isHealthy ? 'Connected' : 'Disconnected'}
            </span>
            {!healthLoading && (
              <Badge variant={isHealthy ? 'default' : 'destructive'}>
                {isHealthy ? 'FastAPI Backend Online' : 'Backend Offline'}
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
                Failed to load sources: {sourcesError.message}
              </AlertDescription>
            </Alert>
          ) : (
            <div className="flex gap-2 flex-wrap">
              {sourcesData?.sources.map((source) => (
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
              
              {searchError && (
                <Alert variant="destructive" className="mt-4">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription>
                    Search failed: {searchError.message}
                  </AlertDescription>
                </Alert>
              )}
              
              {searchResults && (
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
                            e.currentTarget.src = '/placeholder.svg';
                          }}
                        />
                        <div className="flex-1">
                          <h4 className="font-medium">{anime.name}</h4>
                          <p className="text-sm text-muted-foreground">{anime.link}</p>
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
                {loading.popular ? (
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
                ) : errors.popular ? (
                  <Alert variant="destructive">
                    <XCircle className="h-4 w-4" />
                    <AlertDescription>
                      Failed to load popular anime
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
                              e.currentTarget.src = '/placeholder.svg';
                            }}
                          />
                          <div className="flex-1">
                            <h5 className="font-medium text-sm">{anime.name}</h5>
                            <div className="flex items-center gap-1">
                              <Star className="h-3 w-3 text-yellow-500" />
                              <span className="text-xs text-muted-foreground">Popular</span>
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
                {loading.latest ? (
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
                ) : errors.latest ? (
                  <Alert variant="destructive">
                    <XCircle className="h-4 w-4" />
                    <AlertDescription>
                      Failed to load latest updates
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
                              e.currentTarget.src = '/placeholder.svg';
                            }}
                          />
                          <div className="flex-1">
                            <h5 className="font-medium text-sm">{anime.name}</h5>
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3 text-blue-500" />
                              <span className="text-xs text-muted-foreground">Recent</span>
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
          {selectedAnimeUrl && (
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
                      Failed to load series details: {seriesError.message}
                    </AlertDescription>
                  </Alert>
                ) : seriesData ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold">{seriesData.series.slug}</h3>
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
                              <div key={season.season} className="p-2 border rounded text-sm">
                                <div className="font-medium">{season.title || `Season ${season.season}`}</div>
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
                              <div key={movie.number} className="p-2 border rounded text-sm">
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
          {preferences && (
            <Card>
              <CardHeader>
                <CardTitle>Source Preferences</CardTitle>
                <CardDescription>
                  Configuration options for {selectedSource}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {preferences.preferences.map((pref, index) => {
                    // Handle both list_preference and multi_select_list_preference
                    const preference = pref.list_preference || pref.multi_select_list_preference;
                    const preferenceType = pref.list_preference ? 'Single Select' : 'Multi Select';
                    
                    if (!preference) {
                      return (
                        <div key={index} className="p-3 border rounded">
                          <h5 className="font-medium">{pref.key}</h5>
                          <p className="text-sm text-muted-foreground">No preference data available</p>
                        </div>
                      );
                    }

                    return (
                      <div key={index} className="p-3 border rounded">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="font-medium">{preference.title}</h5>
                          <Badge variant="outline" className="text-xs">
                            {preferenceType}
                          </Badge>
                        </div>
                        <div className="flex gap-1 flex-wrap">
                          {preference.entries.map((entry, entryIndex) => (
                            <Badge key={entryIndex} variant="secondary">
                              {entry}
                            </Badge>
                          ))}
                        </div>
                        {preference.entryValues && preference.entryValues.length > 0 && (
                          <div className="mt-2 text-xs text-muted-foreground">
                            Values: {preference.entryValues.join(', ')}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      <Separator />
      
      {/* Footer */}
      <div className="text-center text-sm text-muted-foreground">
        <p>✅ MVP Demo Complete - FastAPI Backend Integration with SWR</p>
        <p>Backend: <code>http://localhost:8000</code> | Frontend: React + TypeScript + SWR</p>
      </div>
    </div>
  );
};

export default AnimeDemo;
