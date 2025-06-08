// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract SynergyGovernance is Ownable {
    struct Proposal {
        string description;
        uint256 voteCount;
        bool executed;
        mapping(address => bool) voted;
    }

    IERC20 public governanceToken;
    Proposal[] public proposals;
    mapping(address => uint256) public votingPower;

    event ProposalCreated(uint256 indexed proposalId, string description);
    event Voted(uint256 indexed proposalId, address indexed voter);
    event ProposalExecuted(uint256 indexed proposalId);

    constructor(address _tokenAddress) {
        require(_tokenAddress != address(0), "Invalid token address");
        governanceToken = IERC20(_tokenAddress);
    }

    function createProposal(string calldata _description) external onlyOwner {
        proposals.push();
        Proposal storage newProposal = proposals[proposals.length - 1];
        newProposal.description = _description;

        emit ProposalCreated(proposals.length - 1, _description);
    }

    function vote(uint256 proposalId) external {
        require(proposalId < proposals.length, "Invalid proposal");
        Proposal storage proposal = proposals[proposalId];
        require(!proposal.voted[msg.sender], "Already voted");

        uint256 voterPower = governanceToken.balanceOf(msg.sender);
        require(voterPower > 0, "No voting power");

        proposal.voteCount += voterPower;
        proposal.voted[msg.sender] = true;

        emit Voted(proposalId, msg.sender);
    }

    function executeProposal(uint256 proposalId) external onlyOwner {
        require(proposalId < proposals.length, "Invalid proposal");
        Proposal storage proposal = proposals[proposalId];
        require(!proposal.executed, "Already executed");

        proposal.executed = true;
        emit ProposalExecuted(proposalId);
    }
}


