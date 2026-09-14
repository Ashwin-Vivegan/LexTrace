import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import casesRouter from './routes/cases.js';
import traceRouter from './routes/trace.js';
import documentsRouter from './routes/documents.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Enable CORS and JSON parsing
app.use(cors());
app.use(express.json());

// Request logging middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.originalUrl}`);
  next();
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'online',
    service: 'Lextrace API Server',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    system: {
      platform: process.platform,
      nodeVersion: process.version
    }
  });
});

// Register API Routes
app.use('/api/cases', casesRouter);
app.use('/api/trace', traceRouter);
app.use('/api/documents', documentsRouter);

// Catch-all for undefined routes
app.use((req, res) => {
  res.status(404).json({ success: false, message: 'API Endpoint not found' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled Server Error:', err);
  res.status(500).json({ success: false, message: 'Internal Server Error', error: err.message });
});

app.listen(PORT, () => {
  console.log(`=======================================================`);
  console.log(`🚀 Lextrace Backend API is running on http://localhost:${PORT}`);
  console.log(`=======================================================`);
});
