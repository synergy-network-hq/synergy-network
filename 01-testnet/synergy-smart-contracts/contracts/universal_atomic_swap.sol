// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract UniversalAtomicSwap is Ownable, ReentrancyGuard {
    using ECDSA for bytes32;

    struct Swap {
        address initiator;
        address participant;
        uint256 amount;
        bytes32 hashLock;
        uint256 expiration;
        bool completed;
    }

    mapping(bytes32 => Swap) public swaps;

    event SwapInitiated(bytes32 indexed swapId, address indexed initiator, address indexed participant, uint256 amount, bytes32 hashLock, uint256 expiration);
    event SwapCompleted(bytes32 indexed swapId, address indexed participant);
    event SwapRefunded(bytes32 indexed swapId, address indexed initiator);

    function initiateSwap(address _participant, uint256 _amount, bytes32 _hashLock, uint256 _expiration) external payable nonReentrant {
        require(msg.value == _amount, "Incorrect ETH amount sent");
        require(_expiration > block.timestamp, "Expiration must be in the future");

        bytes32 swapId = keccak256(abi.encodePacked(msg.sender, _participant, _amount, _hashLock, _expiration));
        require(swaps[swapId].initiator == address(0), "Swap already exists");

        swaps[swapId] = Swap(msg.sender, _participant, _amount, _hashLock, _expiration, false);
        emit SwapInitiated(swapId, msg.sender, _participant, _amount, _hashLock, _expiration);
    }

    function completeSwap(bytes32 swapId, string memory _secret) external nonReentrant {
        Swap storage swap = swaps[swapId];
        require(swap.participant == msg.sender, "Not the designated participant");
        require(!swap.completed, "Swap already completed");
        require(keccak256(abi.encodePacked(_secret)) == swap.hashLock, "Invalid secret");

        swap.completed = true;
        payable(msg.sender).transfer(swap.amount);
        emit SwapCompleted(swapId, msg.sender);
    }

    function refundSwap(bytes32 swapId) external nonReentrant {
        Swap storage swap = swaps[swapId];
        require(swap.initiator == msg.sender, "Not the swap initiator");
        require(!swap.completed, "Swap already completed");
        require(block.timestamp >= swap.expiration, "Swap has not expired yet");

        swap.completed = true;
        payable(swap.initiator).transfer(swap.amount);
        emit SwapRefunded(swapId, msg.sender);
    }
}
