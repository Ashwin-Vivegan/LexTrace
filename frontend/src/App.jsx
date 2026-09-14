import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import CaseTracker from './components/CaseTracker';
import TraceAuditLog from './components/TraceAuditLog';
import DocumentManager from './components/DocumentManager';
import RagAssistant from './components/RagAssistant';
import { 
  fetchHealth, 
  fetchCases, 
  createCase, 
  fetchTraceLogs, 
  addTraceLog, 
  fetchDocuments, 
  uploadDocument 
} from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('rag');
  const [searchTerm, setSearchTerm] = useState('');
  const [apiStatus, setApiStatus] = useState('offline');

  const [cases, setCases] = useState([]);
  const [traceLogs, setTraceLogs] = useState([]);
  const [documents, setDocuments] = useState([]);

  // Check health and load initial data
  useEffect(() => {
    async function loadData() {
      const health = await fetchHealth();
      setApiStatus(health.status || 'offline');

      const casesRes = await fetchCases();
      if (casesRes.success) setCases(casesRes.data);

      const traceRes = await fetchTraceLogs();
      if (traceRes.success) setTraceLogs(traceRes.data);

      const docsRes = await fetchDocuments();
      if (docsRes.success) setDocuments(docsRes.data);
    }

    loadData();
    const interval = setInterval(loadData, 8000);
    return () => clearInterval(interval);
  }, []);

  // Handlers for state updates with live backend sync
  const handleCreateCase = async (newCaseData) => {
    const res = await createCase(newCaseData);
    if (res.success) {
      setCases(prev => [res.data, ...prev]);
    }
  };

  const handleDeleteCase = async (id) => {
    setCases(prev => prev.filter(c => c.id !== id));
    try {
      await fetch(`http://localhost:5000/api/cases/${id}`, { method: 'DELETE' });
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddTraceLog = async (logData) => {
    const res = await addTraceLog(logData);
    if (res.success) {
      setTraceLogs(prev => [res.data, ...prev]);
    }
  };

  const handleUploadDocument = async (formData) => {
    const res = await uploadDocument(formData);
    if (res.success) {
      const docsRes = await fetchDocuments();
      if (docsRes.success) setDocuments(docsRes.data);
    }
    return res;
  };


  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Sidebar navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main content layout */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <Header searchTerm={searchTerm} setSearchTerm={setSearchTerm} apiStatus={apiStatus} />

        <main style={{ flex: 1, padding: '32px', maxWidth: '1400px', width: '100%', margin: '0 auto' }}>
          {activeTab === 'rag' && (
            <RagAssistant />
          )}

          {activeTab === 'dashboard' && (
            <Dashboard 
              cases={cases} 
              traceLogs={traceLogs} 
              documents={documents} 
              onNewCase={() => setActiveTab('cases')}
              onNewTrace={() => setActiveTab('trace')}
            />
          )}

          {activeTab === 'cases' && (
            <CaseTracker 
              cases={cases} 
              onCreateCase={handleCreateCase} 
              onDeleteCase={handleDeleteCase} 
            />
          )}

          {activeTab === 'trace' && (
            <TraceAuditLog 
              traceLogs={traceLogs} 
              cases={cases} 
              onAddLog={handleAddTraceLog} 
            />
          )}

          {activeTab === 'documents' && (
            <DocumentManager 
              documents={documents} 
              onUploadDoc={handleUploadDocument} 
            />
          )}
        </main>
      </div>
    </div>
  );
}
