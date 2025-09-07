import { useState, useRef, useEffect } from 'react'
import Hls from 'hls.js'
import axios from 'axios'
import './App.css'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [selectedAnime, setSelectedAnime] = useState(null)
  const [animeDetails, setAnimeDetails] = useState(null)
  const [selectedEpisode, setSelectedEpisode] = useState(null)
  const [videoSources, setVideoSources] = useState([])
  const [selectedVideoSource, setSelectedVideoSource] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [availableSources] = useState(['aniworld', 'serienstream'])
  const [selectedSource, setSelectedSource] = useState('aniworld')
  const [availableLanguages] = useState([
    { key: 'de', label: 'Deutsch' },
    { key: 'en', label: 'Englisch' },
    { key: 'sub', label: 'Sub' },
    { key: 'all', label: 'All' }
  ])
  const [selectedLanguage, setSelectedLanguage] = useState('de')
  
  const videoRef = useRef(null)
  const hlsRef = useRef(null)

  // Search for anime
  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.get(`${API_BASE_URL}/sources/${selectedSource}/search`, {
        params: { q: searchQuery, page: 1, lang: selectedLanguage }
      })
      setSearchResults(response.data.list || [])
    } catch (err) {
      setError(`Search failed: ${err.response?.data?.detail || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  // Get anime details and episodes using new hierarchical API
  const handleSelectAnime = async (anime) => {
    setSelectedAnime(anime)
    setAnimeDetails(null)
    setSelectedEpisode(null)
    setVideoSources([])
    setSelectedVideoSource(null)
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.get(`${API_BASE_URL}/sources/${selectedSource}/series`, {
        params: { url: anime.link }
      })
      setAnimeDetails(response.data.series)
    } catch (err) {
      setError(`Failed to load anime details: ${err.response?.data?.detail || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  // Get video sources for episode
  const handleSelectEpisode = async (episode) => {
    setSelectedEpisode(episode)
    setVideoSources([])
    setSelectedVideoSource(null)
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.get(`${API_BASE_URL}/sources/${selectedSource}/videos`, {
        params: { url: episode.url }
      })
      setVideoSources(response.data.videos || [])
    } catch (err) {
      setError(`Failed to load video sources: ${err.response?.data?.detail || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  // Play selected video source
  const handlePlayVideo = (videoSource) => {
    setSelectedVideoSource(videoSource)
    
    // Use setTimeout to allow React to render the video element first
    setTimeout(() => {
      const video = videoRef.current
      
      if (!video) {
        console.error('Video element not found after render')
        return
      }

    // Clean up previous HLS instance
    if (hlsRef.current) {
      hlsRef.current.destroy()
      hlsRef.current = null
    }

    // Use direct video URL without proxy
    let videoUrl = videoSource.url
    
    // Check if the URL is a redirect URL
    if (videoUrl.includes('/redirect/')) {
      setError('Video source is a redirect URL. Please select a different source.')
      return
    }

    console.log('Playing video:', videoUrl)

    // Handle M3U8 streams
    if (videoUrl.includes('.m3u8')) {
      if (Hls.isSupported()) {
        const hls = new Hls({
          enableWorker: true,
          lowLatencyMode: false,
          backBufferLength: 90
        })
        
        hlsRef.current = hls
        hls.loadSource(videoUrl)
        hls.attachMedia(video)
        
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          console.log('HLS manifest parsed, starting playback')
          video.play().catch(console.error)
        })
        
        hls.on(Hls.Events.ERROR, (event, data) => {
          console.error('HLS error:', data)
          if (data.fatal) {
            setError(`Video playback error: ${data.details}`)
          }
        })
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        // Native HLS support (Safari)
        video.src = videoUrl
        video.play().catch(console.error)
      } else {
        setError('HLS is not supported in this browser')
      }
    } else {
      // Direct video file
      video.src = videoUrl
      video.play().catch(console.error)
    }
    }, 0) // End setTimeout
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy()
      }
    }
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎌 Anime Video Player</h1>
        <p>Search for anime and play episodes using the anime backend</p>
      </header>

      <main className="app-main">
        {/* Search Section */}
        <section className="search-section">
          <div className="search-controls">
            <select 
              value={selectedSource} 
              onChange={(e) => setSelectedSource(e.target.value)}
              className="source-select"
            >
              {availableSources.map(source => (
                <option key={source} value={source}>{source}</option>
              ))}
            </select>
            
            <select 
              value={selectedLanguage} 
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="language-select"
            >
              {availableLanguages.map(lang => (
                <option key={lang.key} value={lang.key}>{lang.label}</option>
              ))}
            </select>
            
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search for anime (e.g., Solo Leveling)"
              className="search-input"
            />
            
            <button onClick={handleSearch} disabled={loading} className="search-button">
              {loading ? '🔄' : '🔍'} Search
            </button>
          </div>

          {error && <div className="error-message">❌ {error}</div>}
        </section>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <section className="results-section">
            <h3>📺 Search Results ({searchResults.length})</h3>
            <div className="anime-grid">
              {searchResults.map((anime, index) => (
                <div 
                  key={index} 
                  className={`anime-card ${selectedAnime?.link === anime.link ? 'selected' : ''}`}
                  onClick={() => handleSelectAnime(anime)}
                >
                  {anime.imageUrl && (
                    <img src={anime.imageUrl} alt={anime.name} className="anime-image" />
                  )}
                  <div className="anime-info">
                    <h4>{anime.name}</h4>
                    <p className="anime-link">{anime.link}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Anime Details & Episodes */}
        {animeDetails && (
          <section className="details-section">
            <div className="anime-details">
              <h3>📋 {animeDetails.slug}</h3>
              <div className="anime-meta">
                <span className="season-count">📺 {animeDetails.seasons.length} seasons</span>
                {animeDetails.movies && animeDetails.movies.length > 0 && (
                  <span className="movie-count">🎬 {animeDetails.movies.length} movies/OVAs</span>
                )}
              </div>
            </div>

            {/* Seasons Section */}
            {animeDetails.seasons && animeDetails.seasons.length > 0 && (
              <div className="seasons-section">
                <h4>🎬 Seasons</h4>
                {animeDetails.seasons.map((season, seasonIndex) => (
                  <div key={seasonIndex} className="season-container">
                    <h5 className="season-title">
                      {season.title} (Season {season.season})
                    </h5>
                    <div className="episodes-grid">
                      {season.episodes.slice(0, 10).map((episode, episodeIndex) => (
                        <button
                          key={episodeIndex}
                          className={`episode-button ${selectedEpisode?.url === episode.url ? 'selected' : ''}`}
                          onClick={() => handleSelectEpisode(episode)}
                        >
                          <div className="episode-number">E{episode.episode}</div>
                          <div className="episode-title">{episode.title}</div>
                        </button>
                      ))}
                    </div>
                    {season.episodes.length > 10 && (
                      <p className="episode-note">Showing first 10 episodes of {season.title}</p>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Movies/OVAs Section */}
            {animeDetails.movies && animeDetails.movies.length > 0 && (
              <div className="movies-section">
                <h4>🎬 Movies & OVAs</h4>
                <div className="episodes-grid">
                  {animeDetails.movies.slice(0, 10).map((movie, index) => (
                    <button
                      key={index}
                      className={`episode-button movie-button ${selectedEpisode?.url === movie.url ? 'selected' : ''}`}
                      onClick={() => handleSelectEpisode(movie)}
                    >
                      <div className="episode-number">{movie.kind.toUpperCase()}</div>
                      <div className="episode-title">{movie.title}</div>
                    </button>
                  ))}
                </div>
                {animeDetails.movies.length > 10 && (
                  <p className="episode-note">Showing first 10 movies/OVAs</p>
                )}
              </div>
            )}
          </section>
        )}

        {/* Video Sources */}
        {videoSources.length > 0 && (
          <section className="video-sources-section">
            <h4>🎯 Video Sources for: {selectedEpisode?.title || selectedEpisode?.name}</h4>
            <div className="video-sources-grid">
              {videoSources.map((source, index) => (
                <button
                  key={index}
                  className={`video-source-button ${selectedVideoSource === source ? 'selected' : ''}`}
                  onClick={() => handlePlayVideo(source)}
                >
                  <div className="source-quality">{source.quality}</div>
                  <div className="source-url">{source.url.substring(0, 50)}...</div>
                </button>
              ))}
            </div>
          </section>
        )}

        {/* Video Player */}
        {selectedVideoSource && (
          <section className="video-player-section">
            <h4>▶️ Now Playing: {selectedEpisode?.title || selectedEpisode?.name}</h4>
            <div className="video-container">
              <video
                ref={videoRef}
                controls
                className="video-player"
                onError={(e) => setError(`Video error: ${e.target.error?.message || 'Unknown error'}`)}
              >
                Your browser does not support the video tag.
              </video>
            </div>
            <div className="video-info">
              <p><strong>Quality:</strong> {selectedVideoSource.quality}</p>
              <p><strong>Source:</strong> {selectedVideoSource.url.substring(0, 80)}...</p>
            </div>
          </section>
        )}

        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner">🔄 Loading...</div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          🚀 Backend: <code>{API_BASE_URL}</code> | 
          🎬 Player: React + HLS.js | 
          🌐 Language: {availableLanguages.find(lang => lang.key === selectedLanguage)?.label || selectedLanguage} |
          🔗 Direct: No proxy, direct video streaming
        </p>
      </footer>
    </div>
  )
}

export default App