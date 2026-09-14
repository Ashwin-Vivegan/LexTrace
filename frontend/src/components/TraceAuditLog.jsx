import React, { useState } from 'react';
import { GitCommit, ShieldCheck, AlertCircle, Plus, Hash, CheckCircle2, UserCheck, X } from 'lucide-react';

export default function TraceAuditLog({ traceLogs, cases, onAddLog }) {
  const [showModal, setShowModal] = useState(false);
  const [selectedCase, setSelectedCase] = useState('');
  
  const [formData, setFormData] = useState({
    caseId: cases.length > 0 ? cases[0].id : 'CASE-2026-0891',
    actor: 'Lead Counsel',
    action: 'Document Lineage Verification',
    details: '',
    riskFlag: 'Low'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.action || !formData.details) return;
    onAddLog(formData);
    setFormData({
      caseId: cases.length > 0 ? cases[0].id : 'CASE-2026-0891',
      actor: 'Lead Counsel',
      action: 'Document Lineage Verification',
      details: '',
      riskFlag: 'Low'
    });
    setShowModal(false);
  };

  const filteredLogs = selectedCase 
    ? traceLogs.filter(log => log.caseId === selectedCase)
    : traceLogs;

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 700 }}>
            Cryptographic Audit Trace Lineage
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Immutable trace log of legal decision paths, compliance checks, and evidence hashes.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={18} /> Append Audit Log Entry
          </button>
        </div>
      </div>

      {/* Case filter pills */}
      <div className="glass-panel" style={{ padding: '14px 20px', display: 'flex', gap: '10px', alignItems: 'center', overflowX: 'auto' }}>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>Filter Case:</span>
        <button
          onClick={() => setSelectedCase('')}
          style={{
            padding: '6px 14px',
            borderRadius: '20px',
            background: selectedCase === '' ? 'var(--accent-blue)' : 'var(--bg-surface)',
            color: selectedCase === '' ? '#fff' : 'var(--text-secondary)',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.8rem',
            cursor: 'pointer',
            fontWeight: 500,
            whiteSpace: 'nowrap'
          }}
        >
          All Cases ({traceLogs.length})
        </button>
        {cases.map(c => (
          <button
            key={c.id}
            onClick={() => setSelectedCase(c.id)}
            style={{
              padding: '6px 14px',
              borderRadius: '20px',
              background: selectedCase === c.id ? 'var(--accent-blue)' : 'var(--bg-surface)',
              color: selectedCase === c.id ? '#fff' : 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.8rem',
              cursor: 'pointer',
              fontWeight: 500,
              whiteSpace: 'nowrap'
            }}
          >
            {c.id}
          </button>
        ))}
      </div>

      {/* Timeline view */}
      <div className="glass-panel" style={{ padding: '28px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', position: 'relative' }}>
          {/* Vertical line behind timeline nodes */}
          <div style={{
            position: 'absolute',
            left: '23px',
            top: '20px',
            bottom: '20px',
            width: '2px',
            background: 'linear-gradient(180deg, var(--accent-blue) 0%, var(--accent-purple) 50%, var(--border-subtle) 100%)',
            zIndex: 1
          }} />

          {filteredLogs.map((log) => (
            <div key={log.id} style={{ display: 'flex', gap: '20px', zIndex: 2 }}>
              {/* Timeline Icon Node */}
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                background: log.riskFlag === 'High' ? 'rgba(244, 63, 94, 0.15)' : 'rgba(59, 130, 246, 0.15)',
                border: `2px solid ${log.riskFlag === 'High' ? 'var(--accent-rose)' : 'var(--accent-blue)'}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                <GitCommit size={20} color={log.riskFlag === 'High' ? 'var(--accent-rose)' : 'var(--accent-blue)'} />
              </div>

              {/* Log Details Box */}
              <div style={{
                flex: 1,
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '18px 22px',
                display: 'flex',
                flexDirection: 'column',
                gap: '10px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                      <span className="badge badge-blue" style={{ fontFamily: 'monospace' }}>{log.caseId}</span>
                      <h4 style={{ fontSize: '1rem', fontWeight: 600 }}>{log.action}</h4>
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Timestamp: {new Date(log.timestamp).toLocaleString()}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span className={`badge badge-${log.riskFlag.toLowerCase()}`}>
                      {log.riskFlag} Risk
                    </span>
                    <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-emerald)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                      <CheckCircle2 size={12} /> {log.verificationStatus}
                    </span>
                  </div>
                </div>

                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {log.details}
                </p>

                <div style={{
                  display: 'flex',
                  justify: 'space-between',
                  alignItems: 'center',
                  paddingTop: '10px',
                  borderTop: '1px dashed var(--border-subtle)',
                  fontSize: '0.75rem',
                  color: 'var(--text-muted)'
                }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <UserCheck size={14} color="var(--accent-cyan)" /> Verified Actor: <strong>{log.actor}</strong>
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontFamily: 'monospace' }}>
                    <Hash size={14} color="var(--accent-purple)" /> Hash: {log.hash}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal for Appending Trace Log */}
      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 200
        }}>
          <div className="glass-panel animate-fade-in" style={{ width: '500px', padding: '28px', border: '1px solid var(--border-accent)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700 }}>
                Log Audit Trace Action
              </h3>
              <button onClick={() => setShowModal(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Target Case File *</label>
                <select
                  value={formData.caseId}
                  onChange={(e) => setFormData({ ...formData, caseId: e.target.value })}
                  style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.9rem', outline: 'none' }}
                >
                  {cases.map(c => (
                    <option key={c.id} value={c.id}>{c.id} - {c.title}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Action Type *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. EU AI Act Assessment / Ownership Audit"
                  value={formData.action}
                  onChange={(e) => setFormData({ ...formData, action: e.target.value })}
                  style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.9rem', outline: 'none' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Actor Name</label>
                  <input
                    type="text"
                    value={formData.actor}
                    onChange={(e) => setFormData({ ...formData, actor: e.target.value })}
                    style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.9rem', outline: 'none' }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Risk Assessment</label>
                  <select
                    value={formData.riskFlag}
                    onChange={(e) => setFormData({ ...formData, riskFlag: e.target.value })}
                    style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.9rem', outline: 'none' }}
                  >
                    <option value="Low">Low Risk</option>
                    <option value="Medium">Medium Risk</option>
                    <option value="High">High Risk Flag</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Trace Findings / Decision Log *</label>
                <textarea
                  rows="3"
                  required
                  placeholder="Record findings, extracted clause numbers, or evidence link..."
                  value={formData.details}
                  onChange={(e) => setFormData({ ...formData, details: e.target.value })}
                  style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.9rem', outline: 'none', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '12px' }}>
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Append to Hash Chain</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
