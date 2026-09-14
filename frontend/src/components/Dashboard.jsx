import React from 'react';
import { Scale, ShieldCheck, AlertTriangle, FileCheck, ArrowUpRight, Plus, RefreshCw, Layers } from 'lucide-react';

export default function Dashboard({ cases, traceLogs, documents, onNewCase, onNewTrace }) {
  const activeCases = cases.length;
  const highRiskCount = cases.filter(c => c.riskLevel === 'High').length;
  const avgCompliance = cases.length > 0 
    ? Math.round(cases.reduce((sum, c) => sum + (c.complianceScore || 0), 0) / cases.length) 
    : 92;

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Top Banner */}
      <div className="glass-panel" style={{
        padding: '28px 32px',
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%)',
        border: '1px solid var(--border-accent)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ position: 'relative', zIndex: 2, maxWidth: '650px' }}>
          <span className="badge badge-blue" style={{ marginBottom: '12px' }}>Legal Trace & Governance Platform</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.8rem', fontWeight: 700, marginBottom: '8px' }}>
            Legal Risk & Compliance <span className="gradient-text">Audit Control</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6 }}>
            Track litigation lifecycles, reconstruct contract decision chains, and ensure EU AI Act & regulatory compliance with real-time hash verification.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
          <button className="btn-primary" onClick={onNewCase}>
            <Plus size={16} /> Register New Case Trace
          </button>
          <button className="btn-secondary" onClick={onNewTrace}>
            <RefreshCw size={16} /> Log Audit Trace Step
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '20px' }}>
        {/* Card 1 */}
        <div className="glass-panel glass-panel-hover" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Active Legal Cases</span>
            <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.12)', color: 'var(--accent-blue)' }}>
              <Scale size={20} />
            </div>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, fontFamily: 'var(--font-heading)' }}>{activeCases}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '6px' }}>
            <ArrowUpRight size={14} /> 2 cases added this week
          </div>
        </div>

        {/* Card 2 */}
        <div className="glass-panel glass-panel-hover" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>High Risk Audits</span>
            <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(244, 63, 94, 0.12)', color: 'var(--accent-rose)' }}>
              <AlertTriangle size={20} />
            </div>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, fontFamily: 'var(--font-heading)', color: highRiskCount > 0 ? 'var(--accent-rose)' : 'var(--text-primary)' }}>
            {highRiskCount}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>
            Requires lead counsel sign-off
          </div>
        </div>

        {/* Card 3 */}
        <div className="glass-panel glass-panel-hover" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>System Compliance Score</span>
            <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.12)', color: 'var(--accent-emerald)' }}>
              <ShieldCheck size={20} />
            </div>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, fontFamily: 'var(--font-heading)', color: 'var(--accent-emerald)' }}>
            {avgCompliance}%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', marginTop: '6px' }}>
            All cryptographic nodes operational
          </div>
        </div>

        {/* Card 4 */}
        <div className="glass-panel glass-panel-hover" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Document Vault Records</span>
            <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(139, 92, 246, 0.12)', color: 'var(--accent-purple)' }}>
              <FileCheck size={20} />
            </div>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, fontFamily: 'var(--font-heading)' }}>
            {documents.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>
            Automated clause extraction complete
          </div>
        </div>
      </div>

      {/* Main Grid: Recent Cases & Audit Feed */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Left: Active Cases Overview */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: 600 }}>
              Recent Legal Trace Files
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Showing top {cases.slice(0, 4).length} active</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {cases.slice(0, 4).map((item) => (
              <div key={item.id} style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '14px 18px',
                background: 'var(--bg-surface)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)'
              }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-blue)', fontFamily: 'monospace' }}>{item.id}</span>
                    <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>{item.title}</h4>
                  </div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Client: {item.client} • Counsel: {item.leadCounsel}</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <span className={`badge badge-${item.riskLevel.toLowerCase()}`}>
                    {item.riskLevel} Risk
                  </span>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-emerald)' }}>{item.complianceScore}%</span>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Score</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Live Audit Log Feed */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
            <Layers size={18} color="var(--accent-purple)" />
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: 600 }}>
              Live Trace Trail
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {traceLogs.slice(0, 4).map((log) => (
              <div key={log.id} style={{
                padding: '12px 14px',
                background: 'rgba(255, 255, 255, 0.02)',
                borderRadius: 'var(--radius-sm)',
                borderLeft: `3px solid ${log.riskFlag === 'High' ? 'var(--accent-rose)' : 'var(--accent-emerald)'}`
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>{log.action}</span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>{new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>{log.details}</p>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  <span>Actor: {log.actor}</span>
                  <span style={{ fontFamily: 'monospace' }}>{log.hash}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
