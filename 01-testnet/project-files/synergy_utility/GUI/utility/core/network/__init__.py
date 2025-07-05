"""
Network Module for Synergy Network

This package contains the peer-to-peer network implementation for the Synergy Network,
including message handling, peer discovery, and data synchronization.
"""

from .p2p import Node, PeerInfo, Message, MessageType, PeerConnection

__all__ = ['Node', 'PeerInfo', 'Message', 'MessageType', 'PeerConnection']
