import React from 'react';
import { Search, Bell, Activity, ShieldCheck, User } from 'lucide-react';

export default function Header({ searchTerm, setSearchTerm, apiStatus }) {
  return (
    <header style={{
      height: '70px',
      borderBottom: '1px solid var(--border-subtle)',
      background: 'rgba(11, 15, 25, 0.8)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 32px',
      position: 'sticky',
      top: 0,
      zIndex: 90
    }}>
      {/* Search Input */}
      <div style={{ position: 'relative', width: '380px' }}>
        <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
        <input
          type="text"
          placeholder="Search cases, document hashes, or audit entries..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: '100%',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '9px 16px 9px 42px',
            color: 'var(--text-primary)',
            fontSize: '0.85rem',
            outline: 'none',
            transition: 'var(--transition-fast)'
          }}
        />
      </div>

      {/* Right controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        {/* Backend Status indicator */}
        <div className="badge" style={{
          background: apiStatus === 'online' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
          border: `1px solid ${apiStatus === 'online' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
          color: apiStatus === 'online' ? 'var(--accent-emerald)' : 'var(--accent-rose)',
          padding: '6px 12px'
        }}>
          <span className="pulse-dot" style={{ backgroundColor: apiStatus === 'online' ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}></span>
          <span>API {apiStatus === 'online' ? 'Live (Port 5000)' : 'Connecting...'}</span>
        </div>

        {/* Notifications Icon */}
        <button style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '50%',
          width: '38px',
          height: '38px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          color: 'var(--text-secondary)',
          position: 'relative'
        }}>
          <Bell size={18} />
          <span style={{
            position: 'absolute',
            top: '8px',
            right: '8px',
            width: '7px',
            height: '7px',
            borderRadius: '50%',
            background: 'var(--accent-rose)'
          }}></span>
        </button>

        {/* User profile */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingLeft: '8px', borderLeft: '1px solid var(--border-subtle)' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff'
          }}>
            <User size={18} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Counsel Desk</span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Lead Compliance Admin</span>
          </div>
        </div>
      </div>
    </header>
  );
}
