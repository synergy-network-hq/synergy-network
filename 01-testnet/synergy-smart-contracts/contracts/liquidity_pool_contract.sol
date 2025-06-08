// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SynergyLiquidityPool is Ownable, ReentrancyGuard {
    IERC20 public token;
    mapping(address => uint256) public liquidity;
    uint256 public totalLiquidity;

    event LiquidityAdded(address indexed provider, uint256 amount);
    event LiquidityRemoved(address indexed provider, uint256 amount);
    event Swap(address indexed user, uint256 inputAmount, uint256 outputAmount);

    constructor(address _tokenAddress) {
        require(_tokenAddress != address(0), "Invalid token address");
        token = IERC20(_tokenAddress);
    }

    function addLiquidity(uint256 amount) external nonReentrant {
        require(amount > 0, "Amount must be greater than zero");
        token.transferFrom(msg.sender, address(this), amount);
        liquidity[msg.sender] += amount;
        totalLiquidity += amount;
        emit LiquidityAdded(msg.sender, amount);
    }

    function removeLiquidity(uint256 amount) external nonReentrant {
        require(amount > 0 && liquidity[msg.sender] >= amount, "Invalid amount");
        liquidity[msg.sender] -= amount;
        totalLiquidity -= amount;
        token.transfer(msg.sender, amount);
        emit LiquidityRemoved(msg.sender, amount);
    }

    function swap(uint256 inputAmount) external nonReentrant {
        require(inputAmount > 0, "Invalid input amount");
        require(totalLiquidity > 0, "No liquidity available");

        uint256 outputAmount = calculateSwapAmount(inputAmount);
        token.transferFrom(msg.sender, address(this), inputAmount);
        token.transfer(msg.sender, outputAmount);

        emit Swap(msg.sender, inputAmount, outputAmount);
    }

    function calculateSwapAmount(uint256 inputAmount) public view returns (uint256) {
        return (inputAmount * 95) / 100; // 5% fee retained in liquidity pool
    }
}
