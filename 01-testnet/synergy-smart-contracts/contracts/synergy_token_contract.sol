// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

contract SynergyToken is ERC20, ERC20Burnable, Ownable, ERC20Permit {
    uint256 public maxSupply;
    mapping(address => bool) public minters;

    event MinterAdded(address indexed minter);
    event MinterRemoved(address indexed minter);

    constructor(uint256 _maxSupply)
        ERC20("Synergy Token", "SYN")
        Ownable(msg.sender)  // Initialize owner explicitly
        ERC20Permit("Synergy Token")
    {
        maxSupply = _maxSupply * (10 ** decimals());
        _mint(msg.sender, maxSupply / 10); // Mint 10% of supply to contract owner
    }
    modifier onlyMinter() {
        require(minters[msg.sender] || owner() == msg.sender, "Not authorized to mint");
        _;
    }

    function addMinter(address _minter) external onlyOwner {
        minters[_minter] = true;
        emit MinterAdded(_minter);
    }

    function removeMinter(address _minter) external onlyOwner {
        minters[_minter] = false;
        emit MinterRemoved(_minter);
    }

    function mint(address to, uint256 amount) external onlyMinter {
        require(totalSupply() + amount <= maxSupply, "Exceeds max supply");
        _mint(to, amount);
    }

    function burn(uint256 amount) public override {
        super.burn(amount);
    }
}
