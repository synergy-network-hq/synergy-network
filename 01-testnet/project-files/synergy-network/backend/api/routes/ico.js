const express = require('express');
const router = express.Router();
const icoController = require('../controllers/ico');

// GET ICO details (start/end dates, price tiers, etc.)
router.get('/details', icoController.getIcoDetails);

// GET ICO statistics (raised amount, participants, etc.)
router.get('/stats', icoController.getIcoStats);

// GET price tiers
router.get('/price-tiers', icoController.getPriceTiers);

// GET user's ICO participation
router.get('/participation/:address', icoController.getUserParticipation);

// POST participate in ICO
router.post('/participate', icoController.participateInIco);

// GET token distribution schedule
router.get('/distribution-schedule', icoController.getDistributionSchedule);

// GET KYC requirements
router.get('/kyc-requirements', icoController.getKycRequirements);

// POST submit KYC information
router.post('/submit-kyc', icoController.submitKyc);

// GET KYC status
router.get('/kyc-status/:address', icoController.getKycStatus);

module.exports = router;
