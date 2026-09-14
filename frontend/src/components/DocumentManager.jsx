import React, { useState } from 'react';
import { 
  FileText, UploadCloud, Eye, Trash2, CheckCircle2, 
  AlertCircle, X, Layers, Calendar, ShieldCheck, Tag
} from 'lucide-react';
import { fetchDocumentDetail, fetchExtractedText, deleteDocument } from '../api';

export default function DocumentManager({ documents, onUploadDoc }) {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedDocDetail, setSelectedDocDetail] = useState(null);
  const [activeTextPreview, setActiveTextPreview] = useState(null);
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);

  // Upload Form State
  const [selectedFile, setSelectedFile] = useState(null);
  const [formData, setFormData] = useState({
    document_name: '',
    document_type: 'contract',
    jurisdiction: '',
    practice_area: '',
    client_reference: '',
    version_number: '1.0',
    effective_date: new Date().toISOString().split('T')[0],
    status_str: 'current',
    existing_document_id: ''
  });

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      // Auto fill document name if empty
      if (!formData.document_name) {
        setFormData(prev => ({ ...prev, document_name: file.name.replace(/\.[^/.]+$/, "") }));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setUploadMessage({ type: 'error', text: 'Please select a PDF, DOCX, or TXT file to upload.' });
      return;
    }

    setIsSubmitting(true);
    setUploadMessage(null);

    const data = new FormData();
    data.append('file', selectedFile);
    data.append('document_name', formData.document_name);
    data.append('document_type', formData.document_type);
    data.append('jurisdiction', formData.jurisdiction);
    data.append('practice_area', formData.practice_area);
    data.append('client_reference', formData.client_reference);
    data.append('version_number', formData.version_number);
    data.append('effective_date', formData.effective_date);
    data.append('status_str', formData.status_str);
    if (formData.existing_document_id) {
      data.append('existing_document_id', formData.existing_document_id);
    }

    const result = await onUploadDoc(data);
    setIsSubmitting(false);

    if (result && result.success) {
      setUploadMessage({
        type: 'success',
        text: `Success! ${result.data.message} (Doc ID: ${result.data.document_id}, Version: ${result.data.version_id}, Extracted Text Length: ${result.data.text_length} chars)`
      });
      // Reset form
      setSelectedFile(null);
      setFormData({
        document_name: '',
        document_type: 'contract',
        jurisdiction: '',
        practice_area: '',
        client_reference: '',
        version_number: '1.0',
        effective_date: new Date().toISOString().split('T')[0],
        status_str: 'current',
        existing_document_id: ''
      });
      setTimeout(() => setShowUploadModal(false), 2000);
    } else {
      setUploadMessage({
        type: 'error',
        text: result?.error || 'Document processing failed. Verify file format and content.'
      });
    }
  };

  const handleInspectDocument = async (docId) => {
    const detail = await fetchDocumentDetail(docId);
    if (detail) {
      setSelectedDocDetail(detail);
      setActiveTextPreview(null);
      setShowDetailModal(true);
    }
  };

  const handleFetchText = async (docId, versionId) => {
    const textData = await fetchExtractedText(docId, versionId);
    if (textData) {
      setActiveTextPreview(textData);
    }
  };

  const handleDelete = async (docId, e) => {
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to delete document '${docId}' and all its stored versions and files?`)) {
      await deleteDocument(docId);
      window.location.reload();
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 700 }}>
            LexTrace Document Vault
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            SQLite backed legal document storage with format text extraction (PDF, DOCX, TXT) and immutable version control.
          </p>
        </div>

        <button className="btn-primary" onClick={() => { setUploadMessage(null); setShowUploadModal(true); }}>
          <UploadCloud size={18} /> Upload Legal Document
        </button>
      </div>

      {/* Upload Zone banner */}
      <div className="glass-panel" style={{
        padding: '28px',
        border: '2px dashed var(--border-accent)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        gap: '12px',
        background: 'rgba(59, 130, 246, 0.03)',
        cursor: 'pointer'
      }} onClick={() => { setUploadMessage(null); setShowUploadModal(true); }}>
        <div style={{
          width: '52px',
          height: '52px',
          borderRadius: '50%',
          background: 'rgba(59, 130, 246, 0.12)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--accent-blue)'
        }}>
          <UploadCloud size={26} />
        </div>
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Click to Upload Contract, Precedent, or Regulation</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Supports PDF, DOCX, TXT up to 25 MB. Text extraction and metadata indexing will run automatically.
          </p>
        </div>
      </div>

      {/* Document Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
        {documents.map((doc) => {
          const docId = doc.document_id || doc.id;
          const docName = doc.document_name || doc.name;
          const docType = doc.document_type || doc.category || 'contract';
          const version = doc.current_version || '1.0';

          return (
            <div key={docId} className="glass-panel glass-panel-hover" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{
                    padding: '10px',
                    borderRadius: '10px',
                    background: 'rgba(139, 92, 246, 0.12)',
                    color: 'var(--accent-purple)'
                  }}>
                    <FileText size={22} />
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--accent-purple)', fontWeight: 600, fontFamily: 'monospace' }}>{docId}</span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{docType.replace('_', ' ')}</span>
                  </div>
                </div>

                <span className="badge badge-low" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                  v{version} ({doc.status || 'current'})
                </span>
              </div>

              <div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '6px', wordBreak: 'break-word' }}>
                  {docName}
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {doc.jurisdiction && <span>📍 {doc.jurisdiction}</span>}
                  {doc.practice_area && <span>⚖️ {doc.practice_area}</span>}
                  {doc.client_reference && <span>💼 {doc.client_reference}</span>}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px', marginTop: '4px' }}>
                <button 
                  className="btn-secondary" 
                  onClick={() => handleInspectDocument(docId)}
                  style={{ flex: 1, padding: '8px', fontSize: '0.8rem', justifyContent: 'center' }}
                >
                  <Eye size={14} /> Versions & Text
                </button>
                <button 
                  className="btn-secondary" 
                  onClick={(e) => handleDelete(docId, e)}
                  style={{ padding: '8px 12px', fontSize: '0.8rem', color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.3)' }}
                  title="Delete Document"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 200,
          padding: '20px'
        }}>
          <div className="glass-panel animate-fade-in" style={{ width: '560px', maxHeight: '90vh', overflowY: 'auto', padding: '28px', border: '1px solid var(--border-accent)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700 }}>
                Upload Legal Document & Metadata
              </h3>
              <button onClick={() => setShowUploadModal(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {uploadMessage && (
              <div style={{
                padding: '12px 16px',
                borderRadius: '8px',
                marginBottom: '16px',
                fontSize: '0.85rem',
                background: uploadMessage.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                color: uploadMessage.type === 'success' ? '#10b981' : '#ef4444',
                border: `1px solid ${uploadMessage.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
              }}>
                {uploadMessage.text}
              </div>
            )}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {/* File Selector */}
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Document File (PDF, DOCX, TXT) *</label>
                <input
                  type="file"
                  required
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileChange}
                  style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.85rem' }}
                />
              </div>

              {/* Existing Document selector if adding a version */}
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Upload Strategy</label>
                <select
                  value={formData.existing_document_id}
                  onChange={(e) => setFormData({ ...formData, existing_document_id: e.target.value })}
                  style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.85rem' }}
                >
                  <option value="">➕ Create New Document</option>
                  {documents.map(d => (
                    <option key={d.document_id || d.id} value={d.document_id || d.id}>
                      📌 Add new version to: {d.document_name || d.name} ({d.document_id || d.id})
                    </option>
                  ))}
                </select>
              </div>

              {/* Document Name */}
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Document Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Master Services Agreement 2026"
                  value={formData.document_name}
                  onChange={(e) => setFormData({ ...formData, document_name: e.target.value })}
                  style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.85rem', outline: 'none' }}
                />
              </div>

              {/* Row 1: Document Type & Version Number */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Document Type</label>
                  <select
                    value={formData.document_type}
                    onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
                    style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.85rem' }}
                  >
                    <option value="contract">Contract</option>
                    <option value="case_precedent">Case Precedent</option>
                    <option value="regulation">Regulation</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Version Number</label>
                  <input
                    type="text"
                    required
                    placeholder="1.0"
                    value={formData.version_number}
                    onChange={(e) => setFormData({ ...formData, version_number: e.target.value })}
                    style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.85rem' }}
                  />
                </div>
              </div>

              {/* Row 2: Jurisdiction & Practice Area */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Jurisdiction</label>
                  <input
                    type="text"
                    placeholder="e.g. England & Wales"
                    value={formData.jurisdiction}
                    onChange={(e) => setFormData({ ...formData, jurisdiction: e.target.value })}
                    style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.85rem' }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Practice Area</label>
                  <input
                    type="text"
                    placeholder="e.g. Intellectual Property"
                    value={formData.practice_area}
                    onChange={(e) => setFormData({ ...formData, practice_area: e.target.value })}
                    style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.85rem' }}
                  />
                </div>
              </div>

              {/* Row 3: Client Reference & Status */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Client Reference</label>
                  <input
                    type="text"
                    placeholder="e.g. REF-9012"
                    value={formData.client_reference}
                    onChange={(e) => setFormData({ ...formData, client_reference: e.target.value })}
                    style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.85rem' }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>Status</label>
                  <select
                    value={formData.status_str}
                    onChange={(e) => setFormData({ ...formData, status_str: e.target.value })}
                    style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px', color: '#fff', fontSize: '0.85rem' }}
                  >
                    <option value="current">Current</option>
                    <option value="superseded">Superseded</option>
                    <option value="draft">Draft</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '14px' }}>
                <button type="button" className="btn-secondary" onClick={() => setShowUploadModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={isSubmitting}>
                  {isSubmitting ? 'Extracting & Saving...' : 'Process & Upload File'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Document Detail & Extracted Text Modal */}
      {showDetailModal && selectedDocDetail && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 200,
          padding: '20px'
        }}>
          <div className="glass-panel animate-fade-in" style={{ width: '700px', maxHeight: '90vh', overflowY: 'auto', padding: '28px', border: '1px solid var(--border-accent)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-purple)', fontFamily: 'monospace' }}>{selectedDocDetail.document_id}</span>
                <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 700 }}>
                  {selectedDocDetail.document_name}
                </h3>
              </div>
              <button onClick={() => setShowDetailModal(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '0.8rem', padding: '12px 16px', background: 'var(--bg-surface)', borderRadius: '8px', marginBottom: '20px' }}>
              <div><strong>Type:</strong> {selectedDocDetail.document_type}</div>
              <div><strong>Jurisdiction:</strong> {selectedDocDetail.jurisdiction || 'N/A'}</div>
              <div><strong>Practice Area:</strong> {selectedDocDetail.practice_area || 'N/A'}</div>
              <div><strong>Client Ref:</strong> {selectedDocDetail.client_reference || 'N/A'}</div>
            </div>

            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '10px' }}>Document Versions ({selectedDocDetail.versions.length})</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
              {selectedDocDetail.versions.map((ver) => (
                <div key={ver.version_id} style={{ padding: '14px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>v{ver.version_number}</span>
                      <span className={`badge ${ver.status === 'current' ? 'badge-low' : 'badge-high'}`}>
                        {ver.status}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                      File: {ver.file_name} ({ver.file_type.toUpperCase()}, {(ver.file_size / 1024).toFixed(1)} KB) • Text Length: {ver.text_length} chars
                    </div>
                  </div>
                  <button 
                    className="btn-secondary" 
                    onClick={() => handleFetchText(selectedDocDetail.document_id, ver.version_id)}
                    style={{ fontSize: '0.75rem', padding: '6px 12px' }}
                  >
                    View Extracted Text
                  </button>
                </div>
              ))}
            </div>

            {activeTextPreview && (
              <div style={{ marginTop: '16px', borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
                <h5 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '8px' }}>
                  Extracted Text Preview for {activeTextPreview.version_id}:
                </h5>
                <pre style={{
                  background: '#0d1117',
                  padding: '14px',
                  borderRadius: '8px',
                  fontSize: '0.8rem',
                  maxHeight: '200px',
                  overflowY: 'auto',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  color: '#c9d1d9'
                }}>
                  {activeTextPreview.text}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
