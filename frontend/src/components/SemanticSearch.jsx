import React, { useState, useEffect } from 'react';
import { Search, Database, RefreshCw, Layers, FileText, CheckCircle2, Sparkles, Key, Network } from 'lucide-react';
import { realHybridSearch, fetchSearchIndexStatus, rebuildSearchIndex } from '../api';

export default function SemanticSearch() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [mode, setMode] = useState('hybrid'); // 'hybrid' | 'semantic' | 'keyword'
  const [status, setStatus] = useState(null);
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isRebuilding, setIsRebuilding] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    const data = await fetchSearchIndexStatus();
    if (data) setStatus(data);
  };

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    
    setIsSearching(true);
    setMessage(null);
    const data = await realHybridSearch(query, mode, topK);
    setIsSearching(false);
    
    if (data && data.results) {
      setResults(data.results);
      if (data.results.length === 0) {
        setMessage({ type: 'info', text: 'No matching chunks found in the index.' });
      }
    } else {
      setMessage({ type: 'error', text: 'Search failed. Check backend connection.' });
    }
  };

  const handleRebuild = async () => {
    if (!window.confirm('Rebuild both FAISS vector index and SQLite FTS5 keyword index?')) return;
    
    setIsRebuilding(true);
    setMessage(null);
    const data = await rebuildSearchIndex();
    setIsRebuilding(false);
    
    if (data && (data.faiss_count !== undefined || data.indexed_count !== undefined)) {
      setMessage({
        type: 'success',
        text: `Indices rebuilt successfully! FAISS vectors: ${data.faiss_count ?? data.indexed_count}, FTS5 chunks: ${data.fts5_count ?? data.indexed_count}.`
      });
      loadStatus();
    } else {
      setMessage({ type: 'error', text: 'Failed to rebuild search indices.' });
    }
  };

  const getSourceBadge = (type) => {
    if (type === 'hybrid') {
      return (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.7rem', background: 'rgba(139, 92, 246, 0.2)', color: '#c084fc', border: '1px solid rgba(139, 92, 246, 0.4)', borderRadius: '4px', padding: '2px 8px', fontWeight: 600 }}>
          <Sparkles size={12} /> Hybrid
        </span>
      );
    }
    if (type === 'keyword') {
      return (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.7rem', background: 'rgba(234, 179, 8, 0.2)', color: '#fde047', border: '1px solid rgba(234, 179, 8, 0.4)', borderRadius: '4px', padding: '2px 8px', fontWeight: 600 }}>
          <Key size={12} /> Keyword (FTS5)
        </span>
      );
    }
    return (
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.7rem', background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa', border: '1px solid rgba(59, 130, 246, 0.4)', borderRadius: '4px', padding: '2px 8px', fontWeight: 600 }}>
        <Network size={12} /> Semantic (FAISS)
      </span>
    );
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 700 }}>
            Hybrid Intelligence Search
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '4px' }}>
            Dual-engine retrieval combining FAISS dense vector semantics and SQLite FTS5 BM25 keyword matching over real legal chunks.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {status && (
            <div className="badge badge-low" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '6px 12px', borderRadius: '6px' }}>
              <Database size={14} style={{ marginRight: '6px' }} />
              FAISS: {status.vector_count} | FTS5: {status.fts5_count}
            </div>
          )}
          <button 
            className="btn-secondary" 
            onClick={handleRebuild} 
            disabled={isRebuilding}
            style={{ padding: '8px 12px', fontSize: '0.8rem' }}
          >
            <RefreshCw size={14} className={isRebuilding ? "animate-spin" : ""} style={{ marginRight: '6px' }} />
            {isRebuilding ? 'Rebuilding...' : 'Rebuild Indices'}
          </button>
        </div>
      </div>

      {message && (
        <div style={{
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '0.85rem',
          background: message.type === 'error' ? 'rgba(239, 68, 68, 0.15)' : (message.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(59, 130, 246, 0.15)'),
          color: message.type === 'error' ? '#ef4444' : (message.type === 'success' ? '#10b981' : '#60a5fa'),
          border: `1px solid ${message.type === 'error' ? 'rgba(239, 68, 68, 0.3)' : (message.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(59, 130, 246, 0.3)')}`
        }}>
          {message.text}
        </div>
      )}

      {/* Mode Selector & Search Form */}
      <form onSubmit={handleSearch} className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        
        {/* Mode Selector Tabs */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: '8px', fontWeight: 600 }}>Retrieval Mode:</span>
          
          <button
            type="button"
            onClick={() => setMode('hybrid')}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: mode === 'hybrid' ? '1px solid #8b5cf6' : '1px solid var(--border-subtle)',
              background: mode === 'hybrid' ? 'rgba(139, 92, 246, 0.2)' : '#0d1117',
              color: mode === 'hybrid' ? '#c084fc' : 'var(--text-secondary)'
            }}
          >
            Hybrid (FAISS + FTS5)
          </button>

          <button
            type="button"
            onClick={() => setMode('semantic')}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: mode === 'semantic' ? '1px solid #3b82f6' : '1px solid var(--border-subtle)',
              background: mode === 'semantic' ? 'rgba(59, 130, 246, 0.2)' : '#0d1117',
              color: mode === 'semantic' ? '#60a5fa' : 'var(--text-secondary)'
            }}
          >
            Semantic Only
          </button>

          <button
            type="button"
            onClick={() => setMode('keyword')}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: mode === 'keyword' ? '1px solid #eab308' : '1px solid var(--border-subtle)',
              background: mode === 'keyword' ? 'rgba(234, 179, 8, 0.2)' : '#0d1117',
              color: mode === 'keyword' ? '#fde047' : 'var(--text-secondary)'
            }}
          >
            Keyword Only
          </button>
        </div>

        {/* Input Bar */}
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search legal clauses, regulatory obligations, termination terms..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              style={{
                width: '100%',
                background: '#0d1117',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '14px 14px 14px 40px',
                color: '#fff',
                fontSize: '0.95rem',
                outline: 'none'
              }}
            />
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Top K:</label>
            <select 
              value={topK} 
              onChange={e => setTopK(Number(e.target.value))}
              style={{ background: '#0d1117', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '10px', color: '#fff', outline: 'none' }}
            >
              <option value={3}>3</option>
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
            </select>
          </div>

          <button type="submit" className="btn-primary" disabled={isSearching || !query.trim()} style={{ padding: '12px 24px' }}>
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Results Grid */}
      {results.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '10px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>
              Retrieved Chunks ({results.length})
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Mode: <strong style={{ color: '#fff', textTransform: 'capitalize' }}>{mode}</strong>
            </span>
          </div>
          
          <div style={{ display: 'grid', gap: '16px' }}>
            {results.map((res, idx) => (
              <div key={res.chunk_id || idx} className="glass-panel" style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                      padding: '8px',
                      borderRadius: '8px',
                      background: 'rgba(59, 130, 246, 0.12)',
                      color: 'var(--accent-blue)'
                    }}>
                      <Layers size={18} />
                    </div>
                    <div>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '2px' }}>
                        {res.document_name}
                      </h4>
                      <div style={{ display: 'flex', gap: '12px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <span>v{res.version_number}</span>
                        <span style={{ textTransform: 'capitalize' }}>{res.document_type ? res.document_type.replace('_', ' ') : 'document'}</span>
                        {res.jurisdiction && <span>{res.jurisdiction}</span>}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                    {getSourceBadge(res.retrieval_type)}
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>
                      Score: {res.score !== undefined ? res.score.toFixed(4) : (res.similarity_score !== undefined ? res.similarity_score.toFixed(4) : 'N/A')}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
                  <span style={{ fontSize: '0.7rem', background: 'rgba(139,92,246,0.15)', color: 'var(--accent-purple)', borderRadius: '4px', padding: '2px 8px', fontFamily: 'monospace' }}>
                    Chunk #{res.chunk_index + 1}
                  </span>
                  {res.section_name && (
                    <span style={{ fontSize: '0.7rem', background: 'rgba(59,130,246,0.1)', color: '#60a5fa', borderRadius: '4px', padding: '2px 8px' }}>
                      § {res.section_name}
                    </span>
                  )}
                  {res.subsection_name && (
                    <span style={{ fontSize: '0.7rem', background: 'rgba(167,139,250,0.1)', color: '#a78bfa', borderRadius: '4px', padding: '2px 8px' }}>
                      ↳ {res.subsection_name}
                    </span>
                  )}
                  {res.page_number != null && (
                    <span style={{ fontSize: '0.7rem', background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)', borderRadius: '4px', padding: '2px 8px' }}>
                      Page {res.page_number}
                    </span>
                  )}
                </div>

                <div style={{
                  background: '#0d1117',
                  padding: '16px',
                  borderRadius: '8px',
                  border: '1px solid rgba(255,255,255,0.05)'
                }}>
                  <p style={{
                    fontSize: '0.85rem', color: '#c9d1d9',
                    lineHeight: '1.6', margin: 0,
                    whiteSpace: 'pre-wrap', wordBreak: 'break-word'
                  }}>
                    {res.content}
                  </p>
                </div>
                
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
