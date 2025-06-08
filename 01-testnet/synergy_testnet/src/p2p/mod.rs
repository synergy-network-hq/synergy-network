use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

pub async fn start_p2p_network(addr: &str) -> Result<(), Box<dyn std::error::Error>> {
    let listener = TcpListener::bind(addr).await?;
    println!("P2P listening on {}", addr);

    loop {
        let (mut socket, peer_addr) = listener.accept().await?;
        println!("New peer connected: {}", peer_addr);

        tokio::spawn(async move {
            let mut buf = [0u8; 1024];
            loop {
                match socket.read(&mut buf).await {
                    Ok(0) => {
                        println!("Peer {} disconnected", peer_addr);
                        break;
                    }
                    Ok(n) => {
                        println!("Received from {}: {:?}", peer_addr, &buf[..n]);
                        if socket.write_all(&buf[..n]).await.is_err() {
                            println!("Write failed to {}", peer_addr);
                            break;
                        }
                    }
                    Err(e) => {
                        println!("Read error from {}: {:?}", peer_addr, e);
                        break;
                    }
                }
            }
        });
    }
}
