import React, { useState, useEffect } from 'react';
import { Sparkles, Database, Search, FileText, CheckCircle2, AlertTriangle, Layers, BookOpen, Clock, ShieldCheck } from 'lucide-react';
import { askRag, fetchSearchIndexStatus, rebuildSearchIndex } from '../api';

export default function RagAssistant() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [ragResult, setRagResult] = useState(null);
  const [status, setStatus] = useState(null);
  const [reindexing, setReindexing] = useState(false);

  const samplePrompts = [
    "What are the termination conditions due to regulatory changes?",
    "What data protection technical measures are required under GDPR?",
    "What is the governing law and jurisdiction of the agreement?",
    "What are the indemnification obligations for third-party claims?",
    "What is the policy regarding nuclear submarine space propulsion?" // Sample prompt for insufficient evidence test
  ];

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    const res = await fetchSearchIndexStatus();
    if (res) setStatus(res);
  };

  const handleAsk = async (textToQuery) => {
    const q = textToQuery !== undefined ? textToQuery : query;
    if (!q.trim()) return;

    setLoading(true);
    setRagResult(null);

    const res = await askRag(q, topK);
    setLoading(false);
    if (res) {
      setRagResult(res);
    }
    loadStats();
  };

  const handleReindex = async () => {
    if (!window.confirm('Rebuild search indices (FAISS + FTS5)?')) return;
    setReindexing(true);
    await rebuildSearchIndex();
    await loadStats();
    setReindexing(false);
  };

  const isInsufficient = ragResult?.answer === "Insufficient evidence in the retrieved documents.";

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header Banner */}
      <div className="glass-panel" style={{ padding: '24px', background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ padding: '8px', borderRadius: '10px', background: 'rgba(139, 92, 246, 0.2)', color: '#c084fc' }}>
                <Sparkles size={22} />
              </div>
              <div>
                <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>
                  Evidence-Grounded Legal Research Assistant
                </h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '4px', margin: 0 }}>
                  RAG pipeline combining M4 Hybrid Search (FAISS + FTS5), Groq LLM generation, and database source citations.
                </p>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {status && (
              <div className="badge badge-low" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '6px 12px', borderRadius: '6px' }}>
                <Database size={14} style={{ marginRight: '6px' }} />
                FAISS: {status.vector_count} | FTS5: {status.fts5_count}
              </div>
            )}
            <button
              onClick={handleReindex}
              disabled={reindexing}
              className="btn-secondary"
              style={{ padding: '8px 14px', fontSize: '0.8rem' }}
            >
              <span>🔄</span> {reindexing ? 'Re-indexing...' : 'Re-index Space'}
            </button>
          </div>
        </div>
      </div>

      {/* Query Search Input Section */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, position: 'relative', minWidth: '280px' }}>
            <Search size={18} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
              placeholder="Ask a question grounded in legal agreements..."
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
              onChange={(e) => setTopK(Number(e.target.value))}
              style={{ background: '#0d1117', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '10px', color: '#fff', outline: 'none' }}
            >
              <option value={3}>3</option>
              <option value={5}>5</option>
              <option value={10}>10</option>
            </select>
          </div>

          <button
            onClick={() => handleAsk()}
            disabled={loading || !query.trim()}
            className="btn-primary"
            style={{ padding: '14px 28px', fontSize: '0.95rem' }}
          >
            {loading ? 'Synthesizing Answer...' : 'Ask LexTrace AI ⚡'}
          </button>
        </div>

        {/* Suggested Queries */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            SAMPLE RESEARCH QUESTIONS:
          </span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {samplePrompts.map((promptText, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuery(promptText);
                  handleAsk(promptText);
                }}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-subtle)',
                  color: idx === 4 ? '#fde047' : '#93c5fd',
                  borderRadius: '16px',
                  padding: '6px 12px',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                {idx === 4 ? `⚠️ ${promptText}` : promptText}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* RAG Results & Citations Display */}
      {ragResult && (
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Metadata Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '14px', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{
                background: isInsufficient ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                color: isInsufficient ? '#ef4444' : '#10b981',
                border: `1px solid ${isInsufficient ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '0.8rem',
                fontWeight: 600
              }}>
                {isInsufficient ? 'Refusal: Insufficient Evidence' : 'Evidence Grounded'}
              </span>

              {ragResult.metadata && (
                <>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={14} /> Latency: <strong>{ragResult.metadata.latency_ms} ms</strong>
                  </span>

                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <BookOpen size={14} /> Chunks Retrieved: <strong>{ragResult.metadata.chunks_retrieved}</strong>
                  </span>
                </>
              )}
            </div>

            {ragResult.metadata && (
              <span style={{ fontSize: '0.75rem', background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)', padding: '4px 10px', borderRadius: '4px' }}>
                LLM Model: {ragResult.metadata.model}
              </span>
            )}
          </div>

          {/* AI Answer Text */}
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={18} style={{ color: 'var(--accent-blue)' }} /> Synthesized Answer
            </h3>
            
            <div style={{
              background: isInsufficient ? 'rgba(239, 68, 68, 0.08)' : '#0d1117',
              border: `1px solid ${isInsufficient ? 'rgba(239, 68, 68, 0.3)' : 'rgba(255, 255, 255, 0.08)'}`,
              padding: '20px',
              borderRadius: '8px',
              color: isInsufficient ? '#fca5a5' : '#e2e8f0',
              lineHeight: '1.6',
              fontSize: '0.95rem',
              whiteSpace: 'pre-wrap'
            }}>
              {isInsufficient ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <AlertTriangle size={20} style={{ color: '#ef4444' }} />
                  <span><strong>Insufficient evidence in the retrieved documents.</strong> The legal corpus does not contain supporting facts for this question.</span>
                </div>
              ) : (
                ragResult.answer
              )}
            </div>
          </div>

          {/* Source Citations Section */}
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '12px', color: 'var(--text-primary)' }}>
              Database Source Citations ({ragResult.citations ? ragResult.citations.length : 0})
            </h4>

            {!ragResult.citations || ragResult.citations.length === 0 ? (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                {isInsufficient ? 'No citations created because retrieved evidence was insufficient.' : 'No citations returned.'}
              </p>
            ) : (
              <div style={{ display: 'grid', gap: '12px' }}>
                {ragResult.citations.map((citation, idx) => (
                  <div key={citation.chunk_id || idx} style={{
                    background: '#0d1117',
                    borderRadius: '8px',
                    padding: '16px',
                    border: '1px solid rgba(255,255,255,0.08)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>
                          📄 {citation.document_name}
                        </span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          v{citation.version_number} | {citation.document_type}
                        </span>
                      </div>

                      <span style={{ fontSize: '0.7rem', background: 'rgba(139,92,246,0.15)', color: 'var(--accent-purple)', borderRadius: '4px', padding: '2px 8px', fontFamily: 'monospace' }}>
                        Chunk ID: {citation.chunk_id}
                      </span>
                    </div>

                    <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                      {citation.section_name && (
                        <span style={{ fontSize: '0.7rem', background: 'rgba(59,130,246,0.1)', color: '#60a5fa', borderRadius: '4px', padding: '2px 8px' }}>
                          § {citation.section_name}
                        </span>
                      )}
                      {citation.page_number != null && (
                        <span style={{ fontSize: '0.7rem', background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)', borderRadius: '4px', padding: '2px 8px' }}>
                          Page {citation.page_number}
                        </span>
                      )}
                    </div>

                    <p style={{
                      fontSize: '0.85rem',
                      color: '#c9d1d9',
                      margin: 0,
                      lineHeight: '1.5',
                      whiteSpace: 'pre-wrap',
                      background: 'rgba(255, 255, 255, 0.02)',
                      padding: '10px 12px',
                      borderRadius: '6px',
                      borderLeft: '3px solid var(--accent-blue)'
                    }}>
                      "{citation.content}"
                    </p>
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
