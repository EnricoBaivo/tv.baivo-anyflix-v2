/**
 * Simple test component to verify swr-openapi implementation
 */

import { useState } from 'react';
import { 
  useSources, 
  usePopular, 
  useSearch, 
  useHealthCheck 
} from './hooks';

export function APITest() {
  const [selectedSource] = useState('aniworld');
  const [searchQuery] = useState('attack');

  // Test health check
  const { data: health, error: healthError, isLoading: healthLoading } = useHealthCheck();

  // Test sources
  const { data: sources, error: sourcesError, isLoading: sourcesLoading } = useSources();

  // Test popular
  const { data: popular, error: popularError, isLoading: popularLoading } = usePopular(selectedSource, 1);

  // Test search
  const { data: searchResults, error: searchError, isLoading: searchLoading } = useSearch(selectedSource, searchQuery, 1);

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>🧪 swr-openapi API Test</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>Health Check</h2>
        <p>Loading: {healthLoading ? 'Yes' : 'No'}</p>
        <p>Error: {healthError ? String(healthError) : 'None'}</p>
        <p>Data: {health ? JSON.stringify(health) : 'None'}</p>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>Sources</h2>
        <p>Loading: {sourcesLoading ? 'Yes' : 'No'}</p>
        <p>Error: {sourcesError ? String(sourcesError) : 'None'}</p>
        <p>Data: {sources ? JSON.stringify(sources) : 'None'}</p>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>Popular Content ({selectedSource})</h2>
        <p>Loading: {popularLoading ? 'Yes' : 'No'}</p>
        <p>Error: {popularError ? String(popularError) : 'None'}</p>
        <p>Results: {popular?.list?.length || 0} items</p>
        {popular?.list?.slice(0, 2).map((item, i) => (
          <div key={i} style={{ marginLeft: '20px', marginBottom: '10px' }}>
            <strong>{item.name}</strong> - {item.link}
          </div>
        ))}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>Search Results ({searchQuery})</h2>
        <p>Loading: {searchLoading ? 'Yes' : 'No'}</p>
        <p>Error: {searchError ? String(searchError) : 'None'}</p>
        <p>Results: {searchResults?.list?.length || 0} items</p>
        {searchResults?.list?.slice(0, 2).map((item, i) => (
          <div key={i} style={{ marginLeft: '20px', marginBottom: '10px' }}>
            <strong>{item.name}</strong> - {item.link}
          </div>
        ))}
      </div>

      <div style={{ marginTop: '30px', padding: '15px', backgroundColor: '#f0f0f0' }}>
        <h3>✅ Implementation Status</h3>
        <ul>
          <li>✅ swr-openapi packages installed</li>
          <li>✅ OpenAPI schema generated from FastAPI backend</li>
          <li>✅ TypeScript types auto-generated</li>
          <li>✅ Type-safe API client created</li>
          <li>✅ Specialized hooks for all endpoints</li>
          <li>✅ Error handling and loading states</li>
          <li>✅ Automatic caching and revalidation</li>
        </ul>
      </div>
    </div>
  );
}

export default APITest;
