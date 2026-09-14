import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

class DataStore:
    def __init__(self):
        self.cases: List[Dict[str, Any]] = [
            {
                "id": "CASE-2026-0891",
                "title": "Apex Financial vs. Meridian Corp",
                "client": "Apex Financial Services",
                "court": "Delaware Chancery Court / High Court",
                "type": "Corporate Governance & Due Diligence",
                "status": "In Review",
                "riskLevel": "High",
                "complianceScore": 84,
                "leadCounsel": "Elena Rostova, Esq.",
                "lastUpdated": "2026-08-28T14:30:00Z",
                "auditCount": 14,
                "summary": "Cross-border entity structure audit, contract ownership verification, and regulatory disclosure tracing."
            },
            {
                "id": "CASE-2026-0742",
                "title": "EU AI Act Governance Certification",
                "client": "NeuralTech Dynamics",
                "court": "European AI Safety Board",
                "type": "AI Governance & Compliance",
                "status": "Compliant",
                "riskLevel": "Low",
                "complianceScore": 97,
                "leadCounsel": "Marcus Vance, Esq.",
                "lastUpdated": "2026-08-29T09:15:00Z",
                "auditCount": 32,
                "summary": "Algorithmic impact assessment, training data lineage audit, and human-in-the-loop trace record."
            },
            {
                "id": "CASE-2026-0618",
                "title": "Vanguard Holdings Acquisition Trace",
                "client": "Vanguard Capital",
                "court": "FTC Antitrust Division",
                "type": "M&A Due Diligence",
                "status": "Pending Evidence",
                "riskLevel": "Medium",
                "complianceScore": 78,
                "leadCounsel": "Sarah Jenkins, Esq.",
                "lastUpdated": "2026-08-27T18:45:00Z",
                "auditCount": 21,
                "summary": "Data room structure analysis, key IP ownership verification, and regulatory reporting."
            },
            {
                "id": "CASE-2026-0455",
                "title": "BioHealth IP Rights Litigation",
                "client": "BioHealth Innovations",
                "court": "U.S. Federal District Court",
                "type": "IP & Patent Rights",
                "status": "Active Discovery",
                "riskLevel": "High",
                "complianceScore": 69,
                "leadCounsel": "David K. Chen",
                "lastUpdated": "2026-08-29T11:00:00Z",
                "auditCount": 18,
                "summary": "Patent claim trace, prior art search validation, and expert witness testimony tracking."
            }
        ]

        self.trace_logs: List[Dict[str, Any]] = [
            {
                "id": "TRC-9901",
                "timestamp": "2026-08-29T10:42:15Z",
                "action": "DOCUMENT_HASH_VERIFIED",
                "caseId": "CASE-2026-0891",
                "caseTitle": "Apex Financial vs. Meridian Corp",
                "actor": "Elena Rostova (Lead Counsel)",
                "details": "Verified SHA-256 integrity hash for Shareholder Agreement v4.2. Zero discrepancies detected.",
                "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "status": "VERIFIED"
            },
            {
                "id": "TRC-9900",
                "timestamp": "2026-08-29T09:18:02Z",
                "action": "RAG_VECTOR_SEARCH_EXECUTED",
                "caseId": "CASE-2026-0742",
                "caseTitle": "EU AI Act Governance Certification",
                "actor": "System RAG Engine v2.4",
                "details": "Queried 142 training data lineage logs. Top similarity score: 0.941. High confidence score.",
                "hash": "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
                "status": "VERIFIED"
            },
            {
                "id": "TRC-9899",
                "timestamp": "2026-08-28T16:05:40Z",
                "action": "ANOMALY_DETECTED",
                "caseId": "CASE-2026-0455",
                "caseTitle": "BioHealth IP Rights Litigation",
                "actor": "Automated Legal Audit Worker",
                "details": "Detected date mismatch in Patent Assignment Ex. 4B vs SEC filing disclosure.",
                "hash": "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
                "status": "FLAGGED"
            },
            {
                "id": "TRC-9898",
                "timestamp": "2026-08-28T11:22:10Z",
                "action": "DATA_ROOM_SYNC",
                "caseId": "CASE-2026-0618",
                "caseTitle": "Vanguard Holdings Acquisition Trace",
                "actor": "Sarah Jenkins (Lead Counsel)",
                "details": "Ingested 18 financial audit reports from Virtual Data Room. RAG vector embeddings updated.",
                "hash": "d41d8cd98f00b204e9800998ecf8427e0a7863118c7c975a59a9307736195726",
                "status": "VERIFIED"
            }
        ]

        self.documents: List[Dict[str, Any]] = [
            {
                "id": "DOC-101",
                "name": "Master_Shareholder_Agreement_v4.pdf",
                "caseId": "CASE-2026-0891",
                "caseTitle": "Apex Financial vs. Meridian Corp",
                "category": "Corporate Agreement",
                "fileSize": "1.8 MB",
                "uploadDate": "2026-08-28T14:00:00Z",
                "indexedChunks": 24,
                "ragStatus": "Indexed",
                "hash": "a4f89d31b2e1904c552084",
                "content": """SECTION 4.1: CORPORATE GOVERNANCE AND VOTING RIGHTS.
Each shareholder of Meridian Corp holding Class A Voting Shares shall have full entitlement to vote on key corporate actions including cross-border mergers, asset liquidations, and board appointment.
SECTION 4.2: RESTRICTIONS ON TRANSFER & FIRST REFUSAL.
No shareholder may assign, pledge, or transfer shares to a non-affiliated third party without first offering Meridian Corp a 30-day right of first refusal at fair market value determined by an independent auditor.
SECTION 4.3: INDEMNIFICATION AND LIABILITY EXCLUSION.
Apex Financial Services shall be indemnified against all regulatory penalties arising from legacy material non-disclosures incurred prior to the closing date of August 15, 2025."""
            },
            {
                "id": "DOC-102",
                "name": "EU_AI_Act_Algorithmic_Audit_Report.pdf",
                "caseId": "CASE-2026-0742",
                "caseTitle": "EU AI Act Governance Certification",
                "category": "Compliance Audit",
                "fileSize": "3.4 MB",
                "uploadDate": "2026-08-29T08:30:00Z",
                "indexedChunks": 42,
                "ragStatus": "Indexed",
                "hash": "8c21bf90e4412ad890117b",
                "content": """ARTICLE 14: HUMAN OVERSIGHT AND ALGORITHMIC LINEAGE TRACE.
NeuralTech Dynamics' high-risk AI models implement continuous logging of model outputs, confidence scores, and feature importance.
Human-in-the-loop overrides must be stored in tamper-proof audit logs for a minimum retention period of 10 years.
ARTICLE 15: ACCURACY, ROBUSTNESS AND CYBERSECURITY.
All training datasets have undergone rigorous bias mitigation filtering, synthetic data validation, and adversarial robustness testing according to EU AI Act Annex IV standards."""
            },
            {
                "id": "DOC-103",
                "name": "Vanguard_Financial_Disclosures_Q2.pdf",
                "caseId": "CASE-2026-0618",
                "caseTitle": "Vanguard Holdings Acquisition Trace",
                "category": "Financial Disclosure",
                "fileSize": "2.1 MB",
                "uploadDate": "2026-08-27T17:10:00Z",
                "indexedChunks": 18,
                "ragStatus": "Indexed",
                "hash": "7731aaef902b1c88219901",
                "content": """EXHIBIT B: MATERIAL CONTRACTS AND IP INTANGIBLE ASSETS.
Vanguard Capital retains full legal title to key patent portfolios and proprietary trading algorithms.
Pending antitrust disclosures with the FTC indicate total cross-market share post-acquisition will not exceed 18.4% in primary jurisdictions."""
            },
            {
                "id": "DOC-104",
                "name": "BioHealth_Patent_Claim_Assignment.pdf",
                "caseId": "CASE-2026-0455",
                "caseTitle": "BioHealth IP Rights Litigation",
                "category": "IP Patent Assignment",
                "fileSize": "950 KB",
                "uploadDate": "2026-08-29T10:15:00Z",
                "indexedChunks": 12,
                "ragStatus": "Indexed",
                "hash": "3310ff982ca0194e883210",
                "content": """CLAIM 1: RECOMBINANT DNA SYNTHESIS TECHNIQUE.
The assignee BioHealth Innovations holds exclusive worldwide rights for US Patent No. 9,842,119 covering genetic sequence assembly method.
Prior art analysis confirms priority filing date of March 12, 2021, pre-dating respondent's contested filing by 14 months."""
            }
        ]

# Global singleton instance
db = DataStore()
