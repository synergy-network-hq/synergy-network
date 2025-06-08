const {ethers} = require("hardhat");

async function deployContracts() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with account:", deployer.address);

    // Deploy Synergy Token
    const SynergyToken = await ethers.getContractFactory("SynergyToken");
    const synergyToken = await SynergyToken.deploy(ethers.utils.parseEther("1000000000"));
    await synergyToken.deployed();
    console.log("Synergy Token deployed at:", synergyToken.address);

    // Deploy Liquidity Pool
    const LiquidityPool = await ethers.getContractFactory("SynergyLiquidityPool");
    const liquidityPool = await LiquidityPool.deploy(synergyToken.address);
    await liquidityPool.deployed();
    console.log("Liquidity Pool deployed at:", liquidityPool.address);

    // Deploy Governance Contract
    const Governance = await ethers.getContractFactory("SynergyGovernance");
    const governance = await Governance.deploy(synergyToken.address);
    await governance.deployed();
    console.log("Governance Contract deployed at:", governance.address);

    // Deploy Staking Contract
    const Staking = await ethers.getContractFactory("SynergyStaking");
    const staking = await Staking.deploy(synergyToken.address, ethers.utils.parseEther("0.05"));
    await staking.deployed();
    console.log("Staking Contract deployed at:", staking.address);
}

deployContracts().catch((error) => {
    console.error("Deployment failed:", error);
    process.exit(1);
});
