import express from 'express';

const router = express.Router();

let traceLogs = [
  {
    id: 'TRC-9910',
    caseId: 'CASE-2026-0891',
    timestamp: '2026-08-29T13:40:12Z',
    actor: 'Elena Rostova',
    action: 'Decision Path Verification',
    details: 'Verified corporate officer resolution #410 with Delaware Secretary of State filing.',
    verificationStatus: 'Verified',
    riskFlag: 'Low',
    hash: '0x8f3b...9e12'
  },
  {
    id: 'TRC-9909',
    caseId: 'CASE-2026-0742',
    timestamp: '2026-08-29T11:22:05Z',
    actor: 'AI Audit Agent v3.4',
    action: 'EU AI Act Compliance Trace',
    details: 'Model training dataset sanitized; biometric feature vectors audited against Article 5 guidelines.',
    verificationStatus: 'Verified',
    riskFlag: 'Low',
    hash: '0xa41c...7d90'
  },
  {
    id: 'TRC-9908',
    caseId: 'CASE-2026-0618',
    timestamp: '2026-08-29T10:05:44Z',
    actor: 'Sarah Jenkins',
    action: 'Contract Ownership Trace',
    details: 'Detected ambiguous IP assignability clause in Schedule 4B of merger agreement.',
    verificationStatus: 'Flagged for Counsel',
    riskFlag: 'High',
    hash: '0xc112...3a88'
  },
  {
    id: 'TRC-9907',
    caseId: 'CASE-2026-0455',
    timestamp: '2026-08-28T16:15:30Z',
    actor: 'David K. Chen',
    action: 'Prior Art Lineage Analysis',
    details: 'Automated claim map generated against US Patent 9,841,204.',
    verificationStatus: 'In Review',
    riskFlag: 'Medium',
    hash: '0x5e98...11ef'
  }
];

// GET /api/trace
router.get('/', (req, res) => {
  const { caseId } = req.query;
  let results = [...traceLogs];

  if (caseId) {
    results = results.filter(t => t.caseId === caseId);
  }

  res.json({
    success: true,
    count: results.length,
    data: results
  });
});

// POST /api/trace/log
router.post('/log', (req, res) => {
  const { caseId, actor, action, details, riskFlag } = req.body;
  if (!action || !details) {
    return res.status(400).json({ success: false, message: 'Action and details are required' });
  }

  const newLog = {
    id: `TRC-${Math.floor(9000 + Math.random() * 1000)}`,
    caseId: caseId || 'CASE-2026-0891',
    timestamp: new Date().toISOString(),
    actor: actor || 'Legal Auditor',
    action,
    details,
    verificationStatus: riskFlag === 'High' ? 'Flagged for Counsel' : 'Verified',
    riskFlag: riskFlag || 'Low',
    hash: `0x${Math.random().toString(16).substring(2, 10)}...${Math.random().toString(16).substring(2, 6)}`
  };

  traceLogs.unshift(newLog);
  res.status(201).json({ success: true, data: newLog });
});

export default router;
