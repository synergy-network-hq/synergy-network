// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Locked Synergy Token (Ethereum Claim Ticket)
 * @dev Non-transferable ERC20, only owner can mint, and transfers are locked
 *      except to a migration/burn contract when set.
 */
contract LockedSynergyToken is ERC20, Ownable {
    // Address of the migration contract, settable by owner
    address public migrationContract;

    constructor() ERC20("Locked Synergy Token", "LockedSYN") {}

    /**
     * @dev Mint tokens to an address (onlyOwner)
     */
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }

    /**
     * @dev Set the migration contract address (onlyOwner, one-time set)
     */
    function setMigrationContract(address _migrationContract) external onlyOwner {
        require(migrationContract == address(0), "Migration contract already set");
        require(_migrationContract != address(0), "Zero address");
        migrationContract = _migrationContract;
    }

    /**
     * @dev Override transfer logic: allow only to migration contract if set
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override {
        // Allow minting (from == 0) and burning (to == 0)
        if (from == address(0) || to == address(0)) {
            super._beforeTokenTransfer(from, to, amount);
            return;
        }
        // Transfers only allowed to migration contract, if set
        require(migrationContract != address(0), "Migration contract not set");
        require(to == migrationContract, "Transfers only allowed to migration contract");
        super._beforeTokenTransfer(from, to, amount);
    }
}
