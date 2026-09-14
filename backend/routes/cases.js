import express from 'express';

const router = express.Router();

// Mock database store for legal cases
let cases = [
  {
    id: 'CASE-2026-0891',
    title: 'Apex Financial vs. Meridian Corp',
    client: 'Apex Financial Services',
    court: 'Delaware Chancery Court / High Court',
    type: 'Corporate Governance & Due Diligence',
    status: 'In Review',
    riskLevel: 'High',
    complianceScore: 84,
    leadCounsel: 'Elena Rostova, Esq.',
    lastUpdated: '2026-08-28T14:30:00Z',
    auditCount: 14,
    summary: 'Cross-border entity structure audit, contract ownership verification, and regulatory disclosure tracing.'
  },
  {
    id: 'CASE-2026-0742',
    title: 'EU AI Act Governance Certification',
    client: 'NeuralTech Dynamics',
    court: 'European AI Safety Board',
    type: 'AI Governance & Compliance',
    status: 'Compliant',
    riskLevel: 'Low',
    complianceScore: 97,
    leadCounsel: 'Marcus Vance, Esq.',
    lastUpdated: '2026-08-29T09:15:00Z',
    auditCount: 32,
    summary: 'Algorithmic impact assessment, training data lineage audit, and human-in-the-loop trace record.'
  },
  {
    id: 'CASE-2026-0618',
    title: 'Vanguard Holdings Acquisition Trace',
    client: 'Vanguard Capital',
    court: 'FTC Antitrust Division',
    type: 'M&A Due Diligence',
    status: 'Pending Evidence',
    riskLevel: 'Medium',
    complianceScore: 78,
    leadCounsel: 'Sarah Jenkins, Esq.',
    lastUpdated: '2026-08-27T18:45:00Z',
    auditCount: 21,
    summary: 'Data room structure analysis, key IP ownership verification, and regulatory reporting.'
  },
  {
    id: 'CASE-2026-0455',
    title: 'BioHealth IP Rights Litigation',
    client: 'BioHealth Innovations',
    court: 'U.S. Federal District Court',
    type: 'IP & Patent Rights',
    status: 'Active Discovery',
    riskLevel: 'High',
    complianceScore: 69,
    leadCounsel: 'David K. Chen',
    lastUpdated: '2026-08-29T11:00:00Z',
    auditCount: 18,
    summary: 'Patent claim trace, prior art search validation, and expert witness testimony tracking.'
  }
];

// GET /api/cases
router.get('/', (req, res) => {
  const { search, status, riskLevel } = req.query;
  let filtered = [...cases];

  if (search) {
    const q = search.toLowerCase();
    filtered = filtered.filter(c => 
      c.id.toLowerCase().includes(q) ||
      c.title.toLowerCase().includes(q) ||
      c.client.toLowerCase().includes(q) ||
      c.type.toLowerCase().includes(q)
    );
  }

  if (status && status !== 'All') {
    filtered = filtered.filter(c => c.status === status);
  }

  if (riskLevel && riskLevel !== 'All') {
    filtered = filtered.filter(c => c.riskLevel === riskLevel);
  }

  res.json({
    success: true,
    count: filtered.length,
    data: filtered
  });
});

// GET /api/cases/:id
router.get('/:id', (req, res) => {
  const item = cases.find(c => c.id === req.params.id);
  if (!item) {
    return res.status(404).json({ success: false, message: 'Case not found' });
  }
  res.json({ success: true, data: item });
});

// POST /api/cases
router.post('/', (req, res) => {
  const { title, client, court, type, riskLevel, leadCounsel, summary } = req.body;
  if (!title || !client) {
    return res.status(400).json({ success: false, message: 'Title and Client are required fields' });
  }

  const newCase = {
    id: `CASE-2026-${Math.floor(1000 + Math.random() * 9000)}`,
    title,
    client,
    court: court || 'Standard Jurisdiction',
    type: type || 'General Legal Trace',
    status: 'In Review',
    riskLevel: riskLevel || 'Medium',
    complianceScore: Math.floor(70 + Math.random() * 25),
    leadCounsel: leadCounsel || 'Unassigned',
    lastUpdated: new Date().toISOString(),
    auditCount: 1,
    summary: summary || 'Newly registered legal trace file.'
  };

  cases.unshift(newCase);
  res.status(201).json({ success: true, data: newCase });
});

// PATCH /api/cases/:id
router.patch('/:id', (req, res) => {
  const index = cases.findIndex(c => c.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ success: false, message: 'Case not found' });
  }

  cases[index] = {
    ...cases[index],
    ...req.body,
    lastUpdated: new Date().toISOString()
  };

  res.json({ success: true, data: cases[index] });
});

// DELETE /api/cases/:id
router.delete('/:id', (req, res) => {
  const index = cases.findIndex(c => c.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ success: false, message: 'Case not found' });
  }

  const deleted = cases.splice(index, 1)[0];
  res.json({ success: true, data: deleted, message: 'Case successfully archived/removed' });
});

export default router;
