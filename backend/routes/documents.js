import express from 'express';

const router = express.Router();

let documents = [
  {
    id: 'DOC-8801',
    name: 'Master_Services_Agreement_v4.2.pdf',
    category: 'Contract & License',
    size: '3.4 MB',
    uploadedBy: 'Elena Rostova',
    uploadDate: '2026-08-28T14:20:00Z',
    riskStatus: 'Low Risk',
    clausesExtracted: 48,
    complianceCheck: 'Passed 100%'
  },
  {
    id: 'DOC-8802',
    name: 'EU_AI_Act_Trust_Record_2026.docx',
    category: 'Regulatory Compliance',
    size: '1.8 MB',
    uploadedBy: 'Marcus Vance',
    uploadDate: '2026-08-29T08:50:00Z',
    riskStatus: 'Passed Compliance',
    clausesExtracted: 32,
    complianceCheck: 'Passed 100%'
  },
  {
    id: 'DOC-8803',
    name: 'IP_Transfer_Schedule_4B.pdf',
    category: 'M&A Due Diligence',
    size: '7.1 MB',
    uploadedBy: 'Sarah Jenkins',
    uploadDate: '2026-08-27T16:10:00Z',
    riskStatus: 'High Risk Flag',
    clausesExtracted: 19,
    complianceCheck: 'Review Required'
  }
];

// GET /api/documents
router.get('/', (req, res) => {
  res.json({
    success: true,
    count: documents.length,
    data: documents
  });
});

// POST /api/documents/upload
router.post('/upload', (req, res) => {
  const { name, category, uploadedBy } = req.body;
  if (!name) {
    return res.status(400).json({ success: false, message: 'Document name is required' });
  }

  const newDoc = {
    id: `DOC-${Math.floor(8000 + Math.random() * 1000)}`,
    name,
    category: category || 'General Legal',
    size: `${(Math.random() * 5 + 0.5).toFixed(1)} MB`,
    uploadedBy: uploadedBy || 'Current Counsel',
    uploadDate: new Date().toISOString(),
    riskStatus: Math.random() > 0.3 ? 'Low Risk' : 'Review Required',
    clausesExtracted: Math.floor(15 + Math.random() * 35),
    complianceCheck: 'Automated Scan Complete'
  };

  documents.unshift(newDoc);
  res.status(201).json({ success: true, data: newDoc });
});

export default router;
