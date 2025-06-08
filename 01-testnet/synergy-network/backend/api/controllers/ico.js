const icoService = require('../../services/ico');

// Controller for ICO-related endpoints

/**
 * Get ICO details
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getIcoDetails = async (req, res, next) => {
  try {
    const details = await icoService.getIcoDetails();
    res.json(details);
  } catch (error) {
    next(error);
  }
};

/**
 * Get ICO statistics
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getIcoStats = async (req, res, next) => {
  try {
    const stats = await icoService.getIcoStats();
    res.json(stats);
  } catch (error) {
    next(error);
  }
};

/**
 * Get price tiers
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getPriceTiers = async (req, res, next) => {
  try {
    const tiers = await icoService.getPriceTiers();
    res.json(tiers);
  } catch (error) {
    next(error);
  }
};

/**
 * Get user's ICO participation
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getUserParticipation = async (req, res, next) => {
  try {
    const { address } = req.params;
    const participation = await icoService.getUserParticipation(address);
    
    if (!participation) {
      return res.status(404).json({ error: 'No participation found for this address' });
    }
    
    res.json(participation);
  } catch (error) {
    next(error);
  }
};

/**
 * Participate in ICO
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.participateInIco = async (req, res, next) => {
  try {
    const { address, amount, paymentMethod, signature } = req.body;
    
    if (!address || !amount || !paymentMethod || !signature) {
      return res.status(400).json({ error: 'Missing required parameters' });
    }
    
    const result = await icoService.participateInIco(address, amount, paymentMethod, signature);
    res.status(201).json(result);
  } catch (error) {
    if (error.message.includes('minimum purchase')) {
      return res.status(400).json({ error: error.message });
    }
    if (error.message.includes('maximum purchase')) {
      return res.status(400).json({ error: error.message });
    }
    next(error);
  }
};

/**
 * Get token distribution schedule
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getDistributionSchedule = async (req, res, next) => {
  try {
    const schedule = await icoService.getDistributionSchedule();
    res.json(schedule);
  } catch (error) {
    next(error);
  }
};

/**
 * Get KYC requirements
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getKycRequirements = async (req, res, next) => {
  try {
    const requirements = await icoService.getKycRequirements();
    res.json(requirements);
  } catch (error) {
    next(error);
  }
};

/**
 * Submit KYC information
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.submitKyc = async (req, res, next) => {
  try {
    const { address, fullName, dateOfBirth, nationality, idType, idNumber, documentImages } = req.body;
    
    if (!address || !fullName || !dateOfBirth || !nationality || !idType || !idNumber || !documentImages) {
      return res.status(400).json({ error: 'Missing required KYC information' });
    }
    
    const result = await icoService.submitKyc(
      address, 
      fullName, 
      dateOfBirth, 
      nationality, 
      idType, 
      idNumber, 
      documentImages
    );
    
    res.status(201).json(result);
  } catch (error) {
    next(error);
  }
};

/**
 * Get KYC status
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getKycStatus = async (req, res, next) => {
  try {
    const { address } = req.params;
    const status = await icoService.getKycStatus(address);
    
    if (!status) {
      return res.status(404).json({ error: 'No KYC submission found for this address' });
    }
    
    res.json(status);
  } catch (error) {
    next(error);
  }
};
