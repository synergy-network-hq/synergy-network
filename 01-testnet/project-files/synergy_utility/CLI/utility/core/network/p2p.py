"""
P2P Network Module for Synergy Network

This module implements the peer-to-peer network communication layer
for the Synergy Network blockchain.
"""

import asyncio
import json
import time
import uuid
import socket
import hashlib
import random
from typing import Dict, List, Any, Optional, Set, Callable, Tuple
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("synergy.network")

# Add parent directory to path to import from other packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from implementation.cryptography.pqc.hash import HashFunctions
from implementation.cryptography.pqc.dilithium import DilithiumSigner

class MessageType:
    """Enumeration of message types in the Synergy Network P2P protocol."""
    HANDSHAKE = "handshake"
    HANDSHAKE_RESPONSE = "handshake_response"
    PING = "ping"
    PONG = "pong"
    GET_PEERS = "get_peers"
    PEERS = "peers"
    GET_BLOCKS = "get_blocks"
    BLOCKS = "blocks"
    GET_BLOCK = "get_block"
    BLOCK = "block"
    NEW_BLOCK = "new_block"
    GET_TRANSACTIONS = "get_transactions"
    TRANSACTIONS = "transactions"
    NEW_TRANSACTION = "new_transaction"
    GET_STATE = "get_state"
    STATE = "state"
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    CLUSTER_FORMATION = "cluster_formation"
    CLUSTER_UPDATE = "cluster_update"
    CONSENSUS_MESSAGE = "consensus_message"

class PeerInfo:
    """Class representing information about a peer in the network."""
    
    def __init__(
        self,
        node_id: str,
        address: str,
        port: int,
        is_validator: bool = False,
        last_seen: int = None,
        version: str = "1.0.0",
        capabilities: List[str] = None
    ):
        """
        Initialize a PeerInfo instance.
        
        Args:
            node_id: Unique identifier for the peer
            address: IP address or hostname
            port: Port number
            is_validator: Whether the peer is a validator
            last_seen: Timestamp of last communication
            version: Protocol version
            capabilities: List of supported capabilities
        """
        self.node_id = node_id
        self.address = address
        self.port = port
        self.is_validator = is_validator
        self.last_seen = last_seen or int(time.time())
        self.version = version
        self.capabilities = capabilities or []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert PeerInfo to dictionary.
        
        Returns:
            Dictionary representation of the peer info
        """
        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "is_validator": self.is_validator,
            "last_seen": self.last_seen,
            "version": self.version,
            "capabilities": self.capabilities
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PeerInfo':
        """
        Create PeerInfo from dictionary.
        
        Args:
            data: Dictionary representation of the peer info
        
        Returns:
            PeerInfo instance
        """
        return cls(
            node_id=data["node_id"],
            address=data["address"],
            port=data["port"],
            is_validator=data.get("is_validator", False),
            last_seen=data.get("last_seen"),
            version=data.get("version", "1.0.0"),
            capabilities=data.get("capabilities", [])
        )
    
    def get_endpoint(self) -> str:
        """
        Get the endpoint string for the peer.
        
        Returns:
            Endpoint string in format "address:port"
        """
        return f"{self.address}:{self.port}"
    
    def update_last_seen(self) -> None:
        """Update the last seen timestamp to current time."""
        self.last_seen = int(time.time())

class Message:
    """Class representing a message in the Synergy Network P2P protocol."""
    
    def __init__(
        self,
        msg_type: str,
        data: Dict[str, Any] = None,
        sender: str = None,
        timestamp: int = None,
        message_id: str = None,
        signature: bytes = None
    ):
        """
        Initialize a Message instance.
        
        Args:
            msg_type: Message type
            data: Message data
            sender: Sender node ID
            timestamp: Message creation timestamp
            message_id: Unique message identifier
            signature: Message signature
        """
        self.msg_type = msg_type
        self.data = data or {}
        self.sender = sender
        self.timestamp = timestamp or int(time.time())
        self.message_id = message_id or str(uuid.uuid4())
        self.signature = signature
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Message to dictionary.
        
        Returns:
            Dictionary representation of the message
        """
        return {
            "msg_type": self.msg_type,
            "data": self.data,
            "sender": self.sender,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "signature": self.signature.hex() if self.signature else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Create Message from dictionary.
        
        Args:
            data: Dictionary representation of the message
        
        Returns:
            Message instance
        """
        return cls(
            msg_type=data["msg_type"],
            data=data.get("data", {}),
            sender=data.get("sender"),
            timestamp=data.get("timestamp"),
            message_id=data.get("message_id"),
            signature=bytes.fromhex(data["signature"]) if data.get("signature") else None
        )
    
    def serialize(self) -> bytes:
        """
        Serialize the message to bytes.
        
        Returns:
            Serialized message
        """
        return json.dumps(self.to_dict()).encode('utf-8')
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'Message':
        """
        Deserialize bytes to a Message.
        
        Args:
            data: Serialized message
        
        Returns:
            Message instance
        """
        msg_dict = json.loads(data.decode('utf-8'))
        return cls.from_dict(msg_dict)
    
    def get_hash(self) -> bytes:
        """
        Compute the hash of the message.
        
        Returns:
            32-byte hash digest
        """
        # Create a dictionary representation without the signature
        msg_dict = self.to_dict()
        msg_dict.pop("signature", None)
        
        # Use the hash function from the cryptography package
        return HashFunctions.sha3_256(json.dumps(msg_dict, sort_keys=True).encode('utf-8'))
    
    def sign(self, private_key: bytes) -> bool:
        """
        Sign the message with the sender's private key.
        
        Args:
            private_key: Sender's private key
        
        Returns:
            True if message was signed, False otherwise
        """
        # Calculate message hash
        msg_hash = self.get_hash()
        
        # Sign the message hash
        self.signature = DilithiumSigner.sign(msg_hash, private_key)
        
        return True
    
    def verify_signature(self, public_key: bytes) -> bool:
        """
        Verify the message signature.
        
        Args:
            public_key: Sender's public key
        
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.signature:
            return False
        
        # Calculate message hash
        msg_hash = self.get_hash()
        
        # Verify the signature
        return DilithiumSigner.verify(msg_hash, self.signature, public_key)

class PeerConnection:
    """Class representing a connection to a peer in the network."""
    
    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        peer_info: PeerInfo = None,
        node: 'Node' = None
    ):
        """
        Initialize a PeerConnection instance.
        
        Args:
            reader: AsyncIO stream reader
            writer: AsyncIO stream writer
            peer_info: Information about the peer
            node: Reference to the parent node
        """
        self.reader = reader
        self.writer = writer
        self.peer_info = peer_info
        self.node = node
        self.is_active = True
        self.last_message_time = time.time()
        self.handshake_completed = False
    
    async def send_message(self, message: Message) -> bool:
        """
        Send a message to the peer.
        
        Args:
            message: Message to send
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_active:
            return False
        
        try:
            # Serialize message
            data = message.serialize()
            
            # Send message length as 4-byte header
            length = len(data)
            self.writer.write(length.to_bytes(4, byteorder='big'))
            
            # Send message data
            self.writer.write(data)
            await self.writer.drain()
            
            self.last_message_time = time.time()
            return True
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.is_active = False
            return False
    
    async def receive_message(self) -> Optional[Message]:
        """
        Receive a message from the peer.
        
        Returns:
            Received message or None if error
        """
        if not self.is_active:
            return None
        
        try:
            # Read message length (4-byte header)
            length_bytes = await self.reader.readexactly(4)
            length = int.from_bytes(length_bytes, byteorder='big')
            
            # Read message data
            data = await self.reader.readexactly(length)
            
            # Deserialize message
            message = Message.deserialize(data)
            
            self.last_message_time = time.time()
            return message
        
        except asyncio.IncompleteReadError:
            logger.info(f"Connection closed by peer: {self.peer_info.get_endpoint() if self.peer_info else 'unknown'}")
            self.is_active = False
            return None
        
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            self.is_active = False
            return None
    
    async def close(self) -> None:
        """Close the connection to the peer."""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        
        self.is_active = False

class Node:
    """Class representing a node in the Synergy Network."""
    
    def __init__(
        self,
        node_id: str = None,
        private_key: bytes = None,
        public_key: bytes = None,
        host: str = "0.0.0.0",
        port: int = 9090,
        is_validator: bool = False,
        bootstrap_nodes: List[Tuple[str, int]] = None
    ):
        """
        Initialize a Node instance.
        
        Args:
            node_id: Unique identifier for the node
            private_key: Node's private key
            public_key: Node's public key
            host: Host to bind to
            port: Port to listen on
            is_validator: Whether this node is a validator
            bootstrap_nodes: List of (host, port) tuples for bootstrap nodes
        """
        self.node_id = node_id or str(uuid.uuid4())
        self.private_key = private_key
        self.public_key = public_key
        self.host = host
        self.port = port
        self.is_validator = is_validator
        self.bootstrap_nodes = bootstrap_nodes or []
        
        # Node state
        self.peers: Dict[str, PeerInfo] = {}  # node_id -> PeerInfo
        self.connections: Dict[str, PeerConnection] = {}  # node_id -> PeerConnection
        self.message_handlers: Dict[str, List[Callable]] = {}  # msg_type -> [handler]
        self.server = None
        self.running = False
        
        # Message cache to prevent processing duplicates
        self.message_cache: Dict[str, int] = {}  # message_id -> timestamp
        self.message_cache_size = 1000
        
        # Validator-specific state
        self.validator_peers: Dict[str, PeerInfo] = {}  # node_id -> PeerInfo
        self.cluster_id = None
        self.cluster_members: Dict[str, PeerInfo] = {}  # node_id -> PeerInfo
    
    async def start(self) -> None:
        """Start the node's server and connect to bootstrap nodes."""
        if self.running:
            return
        
        self.running = True
        
        # Start server
        self.server = await asyncio.start_server(
            self._handle_connection,
            self.host,
            self.port
        )
        
        logger.info(f"Node {self.node_id} listening on {self.host}:{self.port}")
        
        # Connect to bootstrap nodes
        for host, port in self.bootstrap_nodes:
            asyncio.create_task(self.connect_to_peer(host, port))
        
        # Start maintenance tasks
        asyncio.create_task(self._maintenance_task())
        
        # Start server task
        asyncio.create_task(self._server_task())
    
    async def stop(self) -> None:
        """Stop the node's server and close all connections."""
        if not self.running:
            return
        
        self.running = False
        
        # Close all connections
        for connection in self.connections.values():
            await connection.close()
        
        self.connections = {}
        
        # Close server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        
        logger.info(f"Node {self.node_id} stopped")
    
    async def _server_task(self) -> None:
        """Task to keep the server running."""
        async with self.server:
            await self.server.serve_forever()
    
    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Handle a new incoming connection.
        
        Args:
            reader: AsyncIO stream reader
            writer: AsyncIO stream writer
        """
        # Create connection object
        connection = PeerConnection(reader, writer, node=self)
        
        # Perform handshake
        handshake_successful = await self._perform_handshake(connection, is_initiator=False)
        
        if not handshake_successful:
            await connection.close()
            return
        
        # Add to connections
        self.connections[connection.peer_info.node_id] = connection
        
        # Process messages
        await self._process_messages(connection)
    
    async def connect_to_peer(self, host: str, port: int) -> bool:
        """
        Connect to a peer.
        
        Args:
            host: Peer's hostname or IP address
            port: Peer's port
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Connect to peer
            reader, writer = await asyncio.open_connection(host, port)
            
            # Create connection object
            connection = PeerConnection(reader, writer, node=self)
            
            # Perform handshake
            handshake_successful = await self._perform_handshake(connection, is_initiator=True)
            
            if not handshake_successful:
                await connection.close()
                return False
            
            # Add to connections
            self.connections[connection.peer_info.node_id] = connection
            
            # Process messages
            asyncio.create_task(self._process_messages(connection))
            
            return True
        
        except Exception as e:
            logger.error(f"Error connecting to peer {host}:{port}: {e}")
            return False
    
    async def _perform_handshake(self, connection: PeerConnection, is_initiator: bool) -> bool:
        """
        Perform handshake with a peer.
        
        Args:
            connection: Connection to the peer
            is_initiator: Whether this node initiated the connection
        
        Returns:
            True if handshake successful, False otherwise
        """
        try:
            if is_initiator:
                # Send handshake message
                handshake_msg = Message(
                    msg_type=MessageType.HANDSHAKE,
                    data={
                        "node_id": self.node_id,
                        "address": self.host,
                        "port": self.port,
                        "is_validator": self.is_validator,
                        "version": "1.0.0",
                        "capabilities": ["blocks", "transactions", "state"]
                    },
                    sender=self.node_id
                )
                
                if self.private_key:
                    handshake_msg.sign(self.private_key)
                
                await connection.send_message(handshake_msg)
                
                # Receive handshake response
                response = await connection.receive_message()
                
                if not response or response.msg_type != MessageType.HANDSHAKE_RESPONSE:
                    logger.error("Invalid handshake response")
                    return False
                
                # Create peer info
                peer_info = PeerInfo(
                    node_id=response.data["node_id"],
                    address=response.data["address"],
                    port=response.data["port"],
                    is_validator=response.data.get("is_validator", False),
                    version=response.data.get("version", "1.0.0"),
                    capabilities=response.data.get("capabilities", [])
                )
            
            else:
                # Receive handshake message
                handshake = await connection.receive_message()
                
                if not handshake or handshake.msg_type != MessageType.HANDSHAKE:
                    logger.error("Invalid handshake message")
                    return False
                
                # Create peer info
                peer_info = PeerInfo(
                    node_id=handshake.data["node_id"],
                    address=handshake.data["address"],
                    port=handshake.data["port"],
                    is_validator=handshake.data.get("is_validator", False),
                    version=handshake.data.get("version", "1.0.0"),
                    capabilities=handshake.data.get("capabilities", [])
                )
                
                # Send handshake response
                response_msg = Message(
                    msg_type=MessageType.HANDSHAKE_RESPONSE,
                    data={
                        "node_id": self.node_id,
                        "address": self.host,
                        "port": self.port,
                        "is_validator": self.is_validator,
                        "version": "1.0.0",
                        "capabilities": ["blocks", "transactions", "state"]
                    },
                    sender=self.node_id
                )
                
                if self.private_key:
                    response_msg.sign(self.private_key)
                
                await connection.send_message(response_msg)
            
            # Store peer info
            connection.peer_info = peer_info
            self.peers[peer_info.node_id] = peer_info
            
            if peer_info.is_validator:
                self.validator_peers[peer_info.node_id] = peer_info
            
            connection.handshake_completed = True
            logger.info(f"Handshake completed with peer {peer_info.get_endpoint()}")
            
            # Request peers from the new peer
            await self._request_peers(connection)
            
            return True
        
        except Exception as e:
            logger.error(f"Error during handshake: {e}")
            return False
    
    async def _process_messages(self, connection: PeerConnection) -> None:
        """
        Process messages from a peer.
        
        Args:
            connection: Connection to the peer
        """
        while connection.is_active and self.running:
            message = await connection.receive_message()
            
            if not message:
                break
            
            # Update peer's last seen time
            if connection.peer_info:
                connection.peer_info.update_last_seen()
            
            # Process message
            await self._handle_message(message, connection)
        
        # Connection closed
        if connection.peer_info and connection.peer_info.node_id in self.connections:
            del self.connections[connection.peer_info.node_id]
        
        await connection.close()
    
    async def _handle_message(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a received message.
        
        Args:
            message: Received message
            connection: Connection the message was received on
        """
        # Check if message is in cache (to prevent duplicate processing)
        if message.message_id in self.message_cache:
            return
        
        # Add to cache
        self.message_cache[message.message_id] = message.timestamp
        
        # Trim cache if needed
        if len(self.message_cache) > self.message_cache_size:
            # Remove oldest entries
            oldest = sorted(self.message_cache.items(), key=lambda x: x[1])[:100]
            for msg_id, _ in oldest:
                del self.message_cache[msg_id]
        
        # Handle based on message type
        if message.msg_type == MessageType.PING:
            await self._handle_ping(message, connection)
        
        elif message.msg_type == MessageType.PONG:
            # Nothing to do for pong
            pass
        
        elif message.msg_type == MessageType.GET_PEERS:
            await self._handle_get_peers(message, connection)
        
        elif message.msg_type == MessageType.PEERS:
            await self._handle_peers(message, connection)
        
        elif message.msg_type == MessageType.GET_BLOCKS:
            await self._handle_get_blocks(message, connection)
        
        elif message.msg_type == MessageType.BLOCKS:
            await self._handle_blocks(message, connection)
        
        elif message.msg_type == MessageType.GET_BLOCK:
            await self._handle_get_block(message, connection)
        
        elif message.msg_type == MessageType.BLOCK:
            await self._handle_block(message, connection)
        
        elif message.msg_type == MessageType.NEW_BLOCK:
            await self._handle_new_block(message, connection)
        
        elif message.msg_type == MessageType.GET_TRANSACTIONS:
            await self._handle_get_transactions(message, connection)
        
        elif message.msg_type == MessageType.TRANSACTIONS:
            await self._handle_transactions(message, connection)
        
        elif message.msg_type == MessageType.NEW_TRANSACTION:
            await self._handle_new_transaction(message, connection)
        
        elif message.msg_type == MessageType.GET_STATE:
            await self._handle_get_state(message, connection)
        
        elif message.msg_type == MessageType.STATE:
            await self._handle_state(message, connection)
        
        elif message.msg_type == MessageType.TASK_REQUEST:
            await self._handle_task_request(message, connection)
        
        elif message.msg_type == MessageType.TASK_RESPONSE:
            await self._handle_task_response(message, connection)
        
        elif message.msg_type == MessageType.CLUSTER_FORMATION:
            await self._handle_cluster_formation(message, connection)
        
        elif message.msg_type == MessageType.CLUSTER_UPDATE:
            await self._handle_cluster_update(message, connection)
        
        elif message.msg_type == MessageType.CONSENSUS_MESSAGE:
            await self._handle_consensus_message(message, connection)
        
        # Call registered message handlers
        if message.msg_type in self.message_handlers:
            for handler in self.message_handlers[message.msg_type]:
                try:
                    await handler(message, connection)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")
    
    async def _handle_ping(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a ping message.
        
        Args:
            message: Ping message
            connection: Connection the message was received on
        """
        # Send pong response
        pong_msg = Message(
            msg_type=MessageType.PONG,
            data={"ping_id": message.message_id},
            sender=self.node_id
        )
        
        if self.private_key:
            pong_msg.sign(self.private_key)
        
        await connection.send_message(pong_msg)
    
    async def _handle_get_peers(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a get_peers message.
        
        Args:
            message: Get_peers message
            connection: Connection the message was received on
        """
        # Send peers response with a subset of known peers
        peer_limit = message.data.get("limit", 20)
        peer_sample = random.sample(list(self.peers.values()), min(peer_limit, len(self.peers)))
        
        peers_msg = Message(
            msg_type=MessageType.PEERS,
            data={"peers": [peer.to_dict() for peer in peer_sample]},
            sender=self.node_id
        )
        
        if self.private_key:
            peers_msg.sign(self.private_key)
        
        await connection.send_message(peers_msg)
    
    async def _handle_peers(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a peers message.
        
        Args:
            message: Peers message
            connection: Connection the message was received on
        """
        # Process received peers
        for peer_data in message.data.get("peers", []):
            peer_info = PeerInfo.from_dict(peer_data)
            
            # Skip self
            if peer_info.node_id == self.node_id:
                continue
            
            # Skip already connected peers
            if peer_info.node_id in self.connections:
                continue
            
            # Add to known peers
            self.peers[peer_info.node_id] = peer_info
            
            if peer_info.is_validator:
                self.validator_peers[peer_info.node_id] = peer_info
            
            # Try to connect to new peer (with some probability to avoid connection storms)
            if random.random() < 0.3:  # 30% chance
                asyncio.create_task(self.connect_to_peer(peer_info.address, peer_info.port))
    
    async def _request_peers(self, connection: PeerConnection) -> None:
        """
        Request peers from a connection.
        
        Args:
            connection: Connection to request peers from
        """
        get_peers_msg = Message(
            msg_type=MessageType.GET_PEERS,
            data={"limit": 20},
            sender=self.node_id
        )
        
        if self.private_key:
            get_peers_msg.sign(self.private_key)
        
        await connection.send_message(get_peers_msg)
    
    async def _handle_get_blocks(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a get_blocks message.
        
        Args:
            message: Get_blocks message
            connection: Connection the message was received on
        """
        # This would be implemented with the blockchain module
        # For now, just send an empty response
        blocks_msg = Message(
            msg_type=MessageType.BLOCKS,
            data={"blocks": []},
            sender=self.node_id
        )
        
        if self.private_key:
            blocks_msg.sign(self.private_key)
        
        await connection.send_message(blocks_msg)
    
    async def _handle_blocks(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a blocks message.
        
        Args:
            message: Blocks message
            connection: Connection the message was received on
        """
        # This would be implemented with the blockchain module
        # For now, just log the number of blocks received
        blocks = message.data.get("blocks", [])
        logger.info(f"Received {len(blocks)} blocks from {connection.peer_info.node_id}")
    
    async def _handle_get_block(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a get_block message.
        
        Args:
            message: Get_block message
            connection: Connection the message was received on
        """
        # This would be implemented with the blockchain module
        # For now, just send an empty response
        block_msg = Message(
            msg_type=MessageType.BLOCK,
            data={"block": None},
            sender=self.node_id
        )
        
        if self.private_key:
            block_msg.sign(self.private_key)
        
        await connection.send_message(block_msg)
    
    async def _handle_block(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a block message.
        
        Args:
            message: Block message
            connection: Connection the message was received on
        """
        # This would be implemented with the blockchain module
        # For now, just log that a block was received
        block = message.data.get("block")
        if block:
            logger.info(f"Received block from {connection.peer_info.node_id}")
    
    async def _handle_new_block(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a new_block message.
        
        Args:
            message: New_block message
            connection: Connection the message was received on
        """
        # This would be implemented with the blockchain module
        # For now, just log that a new block was received and relay to peers
        block = message.data.get("block")
        if block:
            logger.info(f"Received new block from {connection.peer_info.node_id}")
            
            # Relay to other peers
            await self.broadcast_message(message, exclude=[connection.peer_info.node_id])
    
    async def _handle_get_transactions(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a get_transactions message.
        
        Args:
            message: Get_transactions message
            connection: Connection the message was received on
        """
        # This would be implemented with the transaction pool module
        # For now, just send an empty response
        txs_msg = Message(
            msg_type=MessageType.TRANSACTIONS,
            data={"transactions": []},
            sender=self.node_id
        )
        
        if self.private_key:
            txs_msg.sign(self.private_key)
        
        await connection.send_message(txs_msg)
    
    async def _handle_transactions(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a transactions message.
        
        Args:
            message: Transactions message
            connection: Connection the message was received on
        """
        # This would be implemented with the transaction pool module
        # For now, just log the number of transactions received
        txs = message.data.get("transactions", [])
        logger.info(f"Received {len(txs)} transactions from {connection.peer_info.node_id}")
    
    async def _handle_new_transaction(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a new_transaction message.
        
        Args:
            message: New_transaction message
            connection: Connection the message was received on
        """
        # This would be implemented with the transaction pool module
        # For now, just log that a new transaction was received and relay to peers
        tx = message.data.get("transaction")
        if tx:
            logger.info(f"Received new transaction from {connection.peer_info.node_id}")
            
            # Relay to other peers
            await self.broadcast_message(message, exclude=[connection.peer_info.node_id])
    
    async def _handle_get_state(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a get_state message.
        
        Args:
            message: Get_state message
            connection: Connection the message was received on
        """
        # This would be implemented with the state module
        # For now, just send an empty response
        state_msg = Message(
            msg_type=MessageType.STATE,
            data={"state": {}},
            sender=self.node_id
        )
        
        if self.private_key:
            state_msg.sign(self.private_key)
        
        await connection.send_message(state_msg)
    
    async def _handle_state(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a state message.
        
        Args:
            message: State message
            connection: Connection the message was received on
        """
        # This would be implemented with the state module
        # For now, just log that state was received
        state = message.data.get("state")
        if state:
            logger.info(f"Received state from {connection.peer_info.node_id}")
    
    async def _handle_task_request(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a task_request message.
        
        Args:
            message: Task_request message
            connection: Connection the message was received on
        """
        # This would be implemented with the task pool module
        # For now, just log that a task request was received
        task = message.data.get("task")
        if task:
            logger.info(f"Received task request from {connection.peer_info.node_id}")
            
            # Send a dummy response
            response_msg = Message(
                msg_type=MessageType.TASK_RESPONSE,
                data={
                    "task_id": message.data.get("task_id"),
                    "status": "rejected",
                    "reason": "Not implemented"
                },
                sender=self.node_id
            )
            
            if self.private_key:
                response_msg.sign(self.private_key)
            
            await connection.send_message(response_msg)
    
    async def _handle_task_response(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a task_response message.
        
        Args:
            message: Task_response message
            connection: Connection the message was received on
        """
        # This would be implemented with the task pool module
        # For now, just log that a task response was received
        task_id = message.data.get("task_id")
        status = message.data.get("status")
        if task_id and status:
            logger.info(f"Received task response from {connection.peer_info.node_id}: {status}")
    
    async def _handle_cluster_formation(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a cluster_formation message.
        
        Args:
            message: Cluster_formation message
            connection: Connection the message was received on
        """
        # This would be implemented with the consensus module
        # For now, just log that a cluster formation message was received
        cluster_id = message.data.get("cluster_id")
        members = message.data.get("members", [])
        if cluster_id and members:
            logger.info(f"Received cluster formation from {connection.peer_info.node_id}: {cluster_id} with {len(members)} members")
            
            # If this node is a member, update cluster info
            if self.node_id in members:
                self.cluster_id = cluster_id
                self.cluster_members = {}
                
                for member_id in members:
                    if member_id in self.peers:
                        self.cluster_members[member_id] = self.peers[member_id]
    
    async def _handle_cluster_update(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a cluster_update message.
        
        Args:
            message: Cluster_update message
            connection: Connection the message was received on
        """
        # This would be implemented with the consensus module
        # For now, just log that a cluster update message was received
        cluster_id = message.data.get("cluster_id")
        updates = message.data.get("updates", {})
        if cluster_id and updates:
            logger.info(f"Received cluster update from {connection.peer_info.node_id}: {cluster_id}")
            
            # If this node is in the cluster, apply updates
            if self.cluster_id == cluster_id:
                # Handle added members
                for member_id in updates.get("added", []):
                    if member_id in self.peers:
                        self.cluster_members[member_id] = self.peers[member_id]
                
                # Handle removed members
                for member_id in updates.get("removed", []):
                    if member_id in self.cluster_members:
                        del self.cluster_members[member_id]
    
    async def _handle_consensus_message(self, message: Message, connection: PeerConnection) -> None:
        """
        Handle a consensus_message message.
        
        Args:
            message: Consensus_message message
            connection: Connection the message was received on
        """
        # This would be implemented with the consensus module
        # For now, just log that a consensus message was received
        consensus_type = message.data.get("consensus_type")
        if consensus_type:
            logger.info(f"Received consensus message from {connection.peer_info.node_id}: {consensus_type}")
    
    async def broadcast_message(self, message: Message, exclude: List[str] = None) -> None:
        """
        Broadcast a message to all connected peers.
        
        Args:
            message: Message to broadcast
            exclude: List of node IDs to exclude from broadcast
        """
        exclude = exclude or []
        
        for node_id, connection in self.connections.items():
            if node_id not in exclude and connection.is_active and connection.handshake_completed:
                await connection.send_message(message)
    
    async def broadcast_to_cluster(self, message: Message, exclude: List[str] = None) -> None:
        """
        Broadcast a message to all peers in the same cluster.
        
        Args:
            message: Message to broadcast
            exclude: List of node IDs to exclude from broadcast
        """
        if not self.cluster_id:
            return
        
        exclude = exclude or []
        
        for node_id in self.cluster_members:
            if node_id not in exclude and node_id in self.connections:
                connection = self.connections[node_id]
                if connection.is_active and connection.handshake_completed:
                    await connection.send_message(message)
    
    async def send_message_to_peer(self, peer_id: str, message: Message) -> bool:
        """
        Send a message to a specific peer.
        
        Args:
            peer_id: ID of the peer to send to
            message: Message to send
        
        Returns:
            True if successful, False otherwise
        """
        if peer_id not in self.connections:
            return False
        
        connection = self.connections[peer_id]
        
        if not connection.is_active or not connection.handshake_completed:
            return False
        
        return await connection.send_message(message)
    
    async def _maintenance_task(self) -> None:
        """Periodic maintenance task for the node."""
        while self.running:
            try:
                # Send ping to all connections
                for connection in list(self.connections.values()):
                    if connection.is_active and connection.handshake_completed:
                        ping_msg = Message(
                            msg_type=MessageType.PING,
                            data={"timestamp": int(time.time())},
                            sender=self.node_id
                        )
                        
                        if self.private_key:
                            ping_msg.sign(self.private_key)
                        
                        await connection.send_message(ping_msg)
                
                # Clean up inactive connections
                current_time = time.time()
                for node_id, connection in list(self.connections.items()):
                    if not connection.is_active:
                        del self.connections[node_id]
                    elif current_time - connection.last_message_time > 300:  # 5 minutes
                        logger.info(f"Connection to {node_id} timed out")
                        await connection.close()
                        del self.connections[node_id]
                
                # Connect to more peers if needed
                if len(self.connections) < 10:
                    # Find disconnected peers
                    disconnected_peers = [
                        peer for peer_id, peer in self.peers.items()
                        if peer_id not in self.connections
                    ]
                    
                    # Try to connect to some random disconnected peers
                    if disconnected_peers:
                        peers_to_connect = random.sample(
                            disconnected_peers,
                            min(3, len(disconnected_peers))
                        )
                        
                        for peer in peers_to_connect:
                            asyncio.create_task(self.connect_to_peer(peer.address, peer.port))
            
            except Exception as e:
                logger.error(f"Error in maintenance task: {e}")
            
            # Wait before next maintenance cycle
            await asyncio.sleep(60)  # 1 minute
    
    def register_message_handler(self, msg_type: str, handler: Callable) -> None:
        """
        Register a handler for a specific message type.
        
        Args:
            msg_type: Message type to handle
            handler: Handler function
        """
        if msg_type not in self.message_handlers:
            self.message_handlers[msg_type] = []
        
        self.message_handlers[msg_type].append(handler)
    
    def unregister_message_handler(self, msg_type: str, handler: Callable) -> bool:
        """
        Unregister a handler for a specific message type.
        
        Args:
            msg_type: Message type
            handler: Handler function
        
        Returns:
            True if handler was removed, False otherwise
        """
        if msg_type not in self.message_handlers:
            return False
        
        if handler in self.message_handlers[msg_type]:
            self.message_handlers[msg_type].remove(handler)
            return True
        
        return False
    
    async def get_network_info(self) -> Dict[str, Any]:
        """
        Get information about the node's network status.
        
        Returns:
            Dictionary with network information
        """
        return {
            "node_id": self.node_id,
            "address": self.host,
            "port": self.port,
            "is_validator": self.is_validator,
            "peers": len(self.peers),
            "connections": len(self.connections),
            "validator_peers": len(self.validator_peers),
            "cluster_id": self.cluster_id,
            "cluster_members": len(self.cluster_members) if self.cluster_id else 0
        }

# Example usage
async def main():
    # Create a node
    node = Node(
        host="127.0.0.1",
        port=9090,
        is_validator=False,
        bootstrap_nodes=[("127.0.0.1", 9091)]
    )
    
    # Register message handlers
    node.register_message_handler(MessageType.NEW_BLOCK, lambda msg, conn: print(f"New block received: {msg.data}"))
    
    # Start the node
    await node.start()
    
    try:
        # Keep the node running
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        # Stop the node
        await node.stop()

if __name__ == "__main__":
    asyncio.run(main())
