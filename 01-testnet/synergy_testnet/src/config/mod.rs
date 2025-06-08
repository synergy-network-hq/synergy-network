use std::env;
use std::fs;
use std::path::Path;
use std::error::Error;
use serde::Deserialize;
use toml;

#[derive(Debug, Deserialize, Clone)]
pub struct NodeConfig {
    pub network: NetworkConfig,
    pub consensus: ConsensusConfig,
    pub logging: LoggingConfig,
    pub rpc: RPCConfig,
}

#[derive(Debug, Deserialize, Clone)]
pub struct NetworkConfig {
    pub node_name: String,
    pub listen_address: String,
    pub public_address: String,
    pub bootnodes: Vec<String>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ConsensusConfig {
    pub algorithm: String,
    pub block_time_secs: u64,
    pub max_validators: usize,
    pub synergetic_mode: bool,
}

#[derive(Debug, Deserialize, Clone)]
pub struct LoggingConfig {
    pub log_level: String,
    pub log_file: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct RPCConfig {
    pub http_port: u16,
    pub ws_port: u16,
    pub enable_cors: bool,
}

/// Fallback configuration values in the absence of a config file
impl Default for NodeConfig {
    fn default() -> Self {
        NodeConfig {
            network: NetworkConfig {
                node_name: "synergy-default-node".to_string(),
                listen_address: "0.0.0.0:30303".to_string(),
                public_address: "127.0.0.1:30303".to_string(),
                bootnodes: vec![],
            },
            consensus: ConsensusConfig {
                algorithm: "PoSy".to_string(),
                block_time_secs: 6,
                max_validators: 21,
                synergetic_mode: true,
            },
            logging: LoggingConfig {
                log_level: "info".to_string(),
                log_file: "logs/synergy-node.log".to_string(),
            },
            rpc: RPCConfig {
                http_port: 8545,
                ws_port: 8546,
                enable_cors: true,
            },
        }
    }
}

/// Loads the configuration from TOML file or returns an error with helpful diagnostics
pub fn load_node_config(path: Option<&str>) -> Result<NodeConfig, Box<dyn Error>> {
    let config_path = match path {
        Some(p) => p.to_string(),
        None => env::var("SYNERGY_CONFIG_PATH").unwrap_or_else(|_| "config/node_config.toml".to_string()),
    };

    if !Path::new(&config_path).exists() {
        return Err(format!("❌ Configuration file not found: {}", config_path).into());
    }

    let content = fs::read_to_string(&config_path)?;
    let config: NodeConfig = toml::from_str(&content)?;

    // Optional: Display loaded config summary
    println!("✅ Loaded configuration from {}", config_path);
    println!("Node ID: {}", config.network.node_name);
    println!("Public Address: {}", config.network.public_address);
    println!("Consensus Algorithm: {}", config.consensus.algorithm);
    println!("Logging Output: {}", config.logging.log_file);

    Ok(config)
}
