// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract SynergyPresale is Ownable, ReentrancyGuard {
    IERC20 public synergyToken;
    uint256 public tokenPrice; // Price in wei per SYN token
    uint256 public totalTokensForSale;
    uint256 public tokensSold;
    bool public presaleActive;

    mapping(address => uint256) public purchasedTokens;

    event TokensPurchased(address indexed buyer, uint256 amount);
    event PresaleStarted(uint256 totalTokens, uint256 price);
    event PresaleEnded();

    constructor(address _tokenAddress, uint256 _tokenPrice, uint256 _totalTokensForSale) {
        require(_tokenAddress != address(0), "Invalid token address");
        synergyToken = IERC20(_tokenAddress);
        tokenPrice = _tokenPrice;
        totalTokensForSale = _totalTokensForSale;
    }

    modifier onlyWhenActive() {
        require(presaleActive, "Presale is not active");
        _;
    }

    function startPresale() external onlyOwner {
        require(!presaleActive, "Presale already active");
        presaleActive = true;
        emit PresaleStarted(totalTokensForSale, tokenPrice);
    }

    function endPresale() external onlyOwner {
        require(presaleActive, "Presale is not active");
        presaleActive = false;
        emit PresaleEnded();
    }

    function buyTokens() external payable onlyWhenActive nonReentrant {
        require(msg.value > 0, "Must send ETH to purchase tokens");
        uint256 tokensToBuy = msg.value / tokenPrice;
        require(tokensSold + tokensToBuy <= totalTokensForSale, "Not enough tokens left");

        tokensSold += tokensToBuy;
        purchasedTokens[msg.sender] += tokensToBuy;
        synergyToken.transfer(msg.sender, tokensToBuy);

        emit TokensPurchased(msg.sender, tokensToBuy);
    }

    function withdrawFunds() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}
