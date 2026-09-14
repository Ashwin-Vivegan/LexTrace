import React, { useState, useEffect } from 'react';
import { askRag, fetchRagStats, fetchCases, reindexRag } from '../api';

export default function RagAssistant() {
  const [query, setQuery] = useState('');
  const [selectedCase, setSelectedCase] = useState('');
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [ragResult, setRagResult] = useState(null);
  const [stats, setStats] = useState(null);
  const [reindexing, setReindexing] = useState(false);

  const samplePrompts = [
    "What are the shareholder voting rights & right of first refusal restrictions?",
    "EU AI Act retention requirements for human oversight audit logs?",
    "Antitrust market share thresholds post-acquisition?",
    "BioHealth recombinant DNA patent priority date analysis?"
  ];

  useEffect(() => {
    loadCases();
    loadStats();
  }, []);

  const loadCases = async () => {
    const res = await fetchCases();
    if (res.success) setCases(res.data);
  };

  const loadStats = async () => {
    const res = await fetchRagStats();
    if (res.success) setStats(res);
  };

  const handleAsk = async (textToQuery) => {
    const q = textToQuery !== undefined ? textToQuery : query;
    if (!q.trim()) return;

    setLoading(true);
    setRagResult(null);

    const res = await askRag(q, selectedCase);
    if (res.success) {
      setRagResult(res);
    }
    setLoading(false);
    loadStats(); // refresh stats
  };

  const handleReindex = async () => {
    setReindexing(true);
    await reindexRag();
    await loadStats();
    setReindexing(false);
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', color: '#f8fafc' }}>
      
      {/* Header Banner */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid #334155',
        boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.3)',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '24px' }}>⚡</span>
              <h2 style={{ margin: 0, fontSize: '22px', fontWeight: '700', color: '#60a5fa' }}>
                Python FastAPI RAG AI Assistant
              </h2>
              <span style={{
                background: stats?.indexStatus === 'READY' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(234, 179, 8, 0.2)',
                color: stats?.indexStatus === 'READY' ? '#4ade80' : '#facc15',
                border: `1px solid ${stats?.indexStatus === 'READY' ? '#22c55e' : '#eab308'}`,
                padding: '2px 10px',
                borderRadius: '12px',
                fontSize: '12px',
                fontWeight: '600'
              }}>
                {stats?.indexStatus || 'RAG ONLINE'}
              </span>
            </div>
            <p style={{ margin: '6px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
              Retrieval-Augmented Generation engine for instant legal document synthesis & vector chunk search.
            </p>
          </div>

          <button
            onClick={handleReindex}
            disabled={reindexing}
            style={{
              background: '#334155',
              color: '#e2e8f0',
              border: '1px solid #475569',
              borderRadius: '8px',
              padding: '10px 16px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span>🔄</span> {reindexing ? 'Re-indexing...' : 'Re-index Vector Space'}
          </button>
        </div>

        {/* Vector Stats Bar */}
        {stats && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '12px',
            marginTop: '20px',
            paddingTop: '16px',
            borderTop: '1px solid rgba(255,255,255,0.08)'
          }}>
            <div style={{ background: '#0f172a', padding: '12px 16px', borderRadius: '10px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Indexed Vector Chunks</div>
              <div style={{ fontSize: '20px', fontWeight: '700', color: '#38bdf8', marginTop: '2px' }}>{stats.totalIndexedChunks}</div>
            </div>
            <div style={{ background: '#0f172a', padding: '12px 16px', borderRadius: '10px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Vector Space Dimension</div>
              <div style={{ fontSize: '20px', fontWeight: '700', color: '#a78bfa', marginTop: '2px' }}>{stats.vectorSpaceDimensions}</div>
            </div>
            <div style={{ background: '#0f172a', padding: '12px 16px', borderRadius: '10px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Target Legal Docs</div>
              <div style={{ fontSize: '20px', fontWeight: '700', color: '#34d399', marginTop: '2px' }}>{stats.totalDocuments}</div>
            </div>
            <div style={{ background: '#0f172a', padding: '12px 16px', borderRadius: '10px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Embedding Engine</div>
              <div style={{ fontSize: '12px', fontWeight: '600', color: '#cbd5e1', marginTop: '6px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>TF-IDF + Cosine Vector Space</div>
            </div>
          </div>
        )}
      </div>

      {/* Query Search Section */}
      <div style={{
        background: '#1e293b',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid #334155',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '280px' }}>
            <label style={{ display: 'block', fontSize: '13px', color: '#94a3b8', marginBottom: '6px', fontWeight: '600' }}>
              RAG Legal Search Query
            </label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
              placeholder="Ask a legal question or search across contract terms..."
              style={{
                width: '100%',
                padding: '12px 16px',
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '15px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div style={{ width: '240px' }}>
            <label style={{ display: 'block', fontSize: '13px', color: '#94a3b8', marginBottom: '6px', fontWeight: '600' }}>
              Case Context Filter
            </label>
            <select
              value={selectedCase}
              onChange={(e) => setSelectedCase(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 16px',
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '14px',
                outline: 'none'
              }}
            >
              <option value="">All Cases (Global Search)</option>
              {cases.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.id} - {c.title.length > 25 ? c.title.substring(0, 25) + '...' : c.title}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button
              onClick={() => handleAsk()}
              disabled={loading || !query.trim()}
              style={{
                padding: '12px 24px',
                background: loading ? '#475569' : 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '700',
                fontSize: '15px',
                cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
                boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)'
              }}
            >
              {loading ? 'Synthesizing RAG...' : 'Ask RAG Engine 🤖'}
            </button>
          </div>
        </div>

        {/* Quick Sample Prompts */}
        <div style={{ marginTop: '16px' }}>
          <span style={{ fontSize: '12px', color: '#64748b', fontWeight: '600', marginRight: '8px' }}>
            SUGGESTED RAG QUERIES:
          </span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
            {samplePrompts.map((promptText, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuery(promptText);
                  handleAsk(promptText);
                }}
                style={{
                  background: 'rgba(51, 65, 85, 0.5)',
                  border: '1px solid #334155',
                  color: '#93c5fd',
                  borderRadius: '20px',
                  padding: '6px 14px',
                  fontSize: '12px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                {promptText}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* RAG Results Display */}
      {ragResult && (
        <div style={{
          background: '#1e293b',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.3)'
        }}>
          {/* Metadata Badges */}
          <div style={{
            display: 'flex',
            justify: 'space-between',
            alignItems: 'center',
            paddingBottom: '16px',
            marginBottom: '16px',
            borderBottom: '1px solid #334155',
            flexWrap: 'wrap',
            gap: '12px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{
                background: 'rgba(59, 130, 246, 0.2)',
                color: '#60a5fa',
                padding: '4px 12px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: '700',
                border: '1px solid rgba(59, 130, 246, 0.4)'
              }}>
                RAG Confidence: {ragResult.confidenceScore}%
              </span>

              <span style={{ fontSize: '13px', color: '#94a3b8' }}>
                ⏱️ Latency: <strong>{ragResult.processingTimeMs} ms</strong>
              </span>

              <span style={{ fontSize: '13px', color: '#94a3b8' }}>
                📚 Retrieved Chunks: <strong>{ragResult.retrievedCount}</strong>
              </span>
            </div>

            {ragResult.usedCaseFilter && (
              <span style={{ fontSize: '12px', background: '#334155', color: '#cbd5e1', padding: '4px 10px', borderRadius: '4px' }}>
                Filter: {ragResult.usedCaseFilter}
              </span>
            )}
          </div>

          {/* AI Response Text */}
          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '16px', margin: '0 0 12px 0', color: '#f1f5f9', fontWeight: '700' }}>
              Synthesized AI Answer
            </h3>
            <div style={{
              background: '#0f172a',
              padding: '16px 20px',
              borderRadius: '10px',
              border: '1px solid #334155',
              color: '#e2e8f0',
              lineHeight: '1.6',
              fontSize: '15px',
              whiteSpace: 'pre-line'
            }}>
              {ragResult.answer}
            </div>
          </div>

          {/* Source Citations & Chunk Viewer */}
          <div>
            <h4 style={{ fontSize: '15px', margin: '0 0 14px 0', color: '#cbd5e1', fontWeight: '700' }}>
              Retrieved Document Source Citations ({ragResult.citations.length})
            </h4>

            {ragResult.citations.length === 0 ? (
              <p style={{ color: '#64748b', fontSize: '14px' }}>No vector document chunks matched the search criteria.</p>
            ) : (
              <div style={{ display: 'grid', gap: '12px' }}>
                {ragResult.citations.map((citation, idx) => (
                  <div key={idx} style={{
                    background: '#0f172a',
                    borderRadius: '10px',
                    padding: '16px',
                    border: '1px solid #334155'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ background: '#1e293b', color: '#38bdf8', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: '600' }}>
                          📄 {citation.documentName}
                        </span>
                        <span style={{ color: '#94a3b8', fontSize: '12px' }}>
                          ({citation.category} | {citation.caseId})
                        </span>
                      </div>

                      <span style={{
                        background: 'rgba(34, 197, 94, 0.15)',
                        color: '#4ade80',
                        border: '1px solid rgba(34, 197, 94, 0.3)',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: '700'
                      }}>
                        Similarity Match: {citation.similarityScore}%
                      </span>
                    </div>

                    <div style={{
                      background: 'rgba(30, 41, 59, 0.6)',
                      padding: '10px 14px',
                      borderRadius: '6px',
                      fontFamily: 'monospace',
                      fontSize: '13px',
                      color: '#cbd5e1',
                      borderLeft: '3px solid #3b82f6',
                      marginTop: '8px'
                    }}>
                      "{citation.snippet}"
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      )}

    </div>
  );
}
