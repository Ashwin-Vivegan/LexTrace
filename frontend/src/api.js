const API_BASE = 'http://localhost:5000/api';

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return await res.json();
  } catch (err) {
    console.error('API health error:', err);
    return { status: 'offline' };
  }
}

export async function fetchCases(search = '', status = '', riskLevel = '') {
  try {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (status) params.append('status', status);
    if (riskLevel) params.append('riskLevel', riskLevel);

    const res = await fetch(`${API_BASE}/cases?${params.toString()}`);
    return await res.json();
  } catch (err) {
    console.error('Fetch cases error:', err);
    return { success: false, data: [] };
  }
}

export async function createCase(caseData) {
  try {
    const res = await fetch(`${API_BASE}/cases`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(caseData)
    });
    return await res.json();
  } catch (err) {
    console.error('Create case error:', err);
    return { success: false };
  }
}

export async function fetchTraceLogs(caseId = '') {
  try {
    const params = caseId ? `?caseId=${encodeURIComponent(caseId)}` : '';
    const res = await fetch(`${API_BASE}/trace${params}`);
    return await res.json();
  } catch (err) {
    console.error('Fetch trace logs error:', err);
    return { success: false, data: [] };
  }
}

export async function addTraceLog(logData) {
  try {
    const res = await fetch(`${API_BASE}/trace/log`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(logData)
    });
    return await res.json();
  } catch (err) {
    console.error('Add trace log error:', err);
    return { success: false };
  }
}

// LexTrace Document Management APIs (Milestone 1)
export async function fetchDocuments() {
  try {
    const res = await fetch(`${API_BASE}/documents`);
    const data = await res.json();
    if (Array.isArray(data)) {
      return { success: true, data };
    }
    return data;
  } catch (err) {
    console.error('Fetch documents error:', err);
    return { success: false, data: [] };
  }
}

export async function uploadDocument(formData) {
  try {
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      // Note: Do NOT set Content-Type header when uploading FormData so browser auto-sets boundary
      body: formData
    });
    const data = await res.json();
    if (res.ok) {
      return { success: true, data };
    } else {
      return { success: false, error: data.detail || 'Upload failed' };
    }
  } catch (err) {
    console.error('Upload document error:', err);
    return { success: false, error: err.message };
  }
}

export async function fetchDocumentDetail(documentId) {
  try {
    const res = await fetch(`${API_BASE}/documents/${encodeURIComponent(documentId)}`);
    return await res.json();
  } catch (err) {
    console.error('Fetch document detail error:', err);
    return null;
  }
}

export async function fetchExtractedText(documentId, versionId) {
  try {
    const res = await fetch(`${API_BASE}/documents/${encodeURIComponent(documentId)}/versions/${encodeURIComponent(versionId)}/text`);
    return await res.json();
  } catch (err) {
    console.error('Fetch extracted text error:', err);
    return null;
  }
}

export async function fetchVersionChunks(documentId, versionId, page = 1, limit = 50) {
  try {
    const params = new URLSearchParams({ page, limit });
    const res = await fetch(
      `${API_BASE}/documents/${encodeURIComponent(documentId)}/versions/${encodeURIComponent(versionId)}/chunks?${params}`
    );
    return await res.json();
  } catch (err) {
    console.error('Fetch version chunks error:', err);
    return null;
  }
}

export async function deleteDocument(documentId) {
  try {
    const res = await fetch(`${API_BASE}/documents/${encodeURIComponent(documentId)}`, {
      method: 'DELETE'
    });
    return await res.json();
  } catch (err) {
    console.error('Delete document error:', err);
    return { success: false, message: err.message };
  }
}



// RAG AI Engine Endpoints
export async function askRag(query, caseId = '', topK = 3) {
  try {
    const res = await fetch(`${API_BASE}/rag/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, caseId: caseId || null, topK })
    });
    return await res.json();
  } catch (err) {
    console.error('RAG query error:', err);
    return { success: false, answer: 'Error connecting to Python FastAPI RAG AI engine.' };
  }
}

export async function fetchRagStats() {
  try {
    const res = await fetch(`${API_BASE}/rag/stats`);
    return await res.json();
  } catch (err) {
    console.error('Fetch RAG stats error:', err);
    return { success: false };
  }
}

export async function semanticSearch(query, caseId = '') {
  try {
    const res = await fetch(`${API_BASE}/rag/semantic-search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, caseId: caseId || null, topK: 5 })
    });
    return await res.json();
  } catch (err) {
    console.error('Semantic search error:', err);
    return { success: false, results: [] };
  }
}

export async function reindexRag() {
  try {
    const res = await fetch(`${API_BASE}/rag/ingest`, { method: 'POST' });
    return await res.json();
  } catch (err) {
    console.error('Reindex RAG error:', err);
    return { success: false };
  }
}
