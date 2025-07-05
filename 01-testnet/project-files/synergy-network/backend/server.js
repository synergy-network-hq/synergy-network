const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Import routes
const blockchainRoutes = require('./api/routes/blockchain');
const walletRoutes = require('./api/routes/wallet');
const icoRoutes = require('./api/routes/ico');
const explorerRoutes = require('./api/routes/explorer');

// Initialize express app
const app = express();

// Set up middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS
app.use(express.json()); // Parse JSON bodies
app.use(morgan('dev')); // Logging

// Rate limiting
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
});

// Apply rate limiting to all routes
app.use(apiLimiter);

// Define routes
app.use('/api/blockchain', blockchainRoutes);
app.use('/api/wallet', walletRoutes);
app.use('/api/ico', icoRoutes);
app.use('/api/explorer', explorerRoutes);

// Root route
app.get('/', (req, res) => {
  res.json({
    message: 'Welcome to Synergy Network API',
    version: '0.1.0',
    documentation: '/api/docs'
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// Start server
const PORT = process.env.PORT || 6969;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app; // For testing
