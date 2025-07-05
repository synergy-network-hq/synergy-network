"""
Address Module for Synergy Network

This module implements the address generation and validation functionality
for the Synergy Network, using Bech32m encoding for quantum-resistant addresses.
"""

import hashlib
import random
import re
from typing import List, Optional, Tuple, Union

class Bech32m:
    """Implementation of the Bech32m encoding scheme."""
    
    # Bech32m character set (excluding ambiguous characters)
    CHARSET = "023456789acdefghjklmnpqrstuvwxyz"
    
    # Bech32m constant for checksum calculation
    BECH32M_CONST = 0x2bc830a3
    
    @staticmethod
    def polymod(values: List[int]) -> int:
        """
        Calculate the Bech32m checksum.
        
        Args:
            values: List of 5-bit values to calculate checksum for
        
        Returns:
            Checksum value
        """
        generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
        chk = 1
        for value in values:
            top = chk >> 25
            chk = (chk & 0x1ffffff) << 5 ^ value
            for i in range(5):
                chk ^= generator[i] if ((top >> i) & 1) else 0
        return chk
    
    @staticmethod
    def hrp_expand(hrp: str) -> List[int]:
        """
        Expand the human-readable part for checksum calculation.
        
        Args:
            hrp: Human-readable part
        
        Returns:
            Expanded values
        """
        return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]
    
    @staticmethod
    def create_checksum(hrp: str, data: List[int]) -> List[int]:
        """
        Create a Bech32m checksum.
        
        Args:
            hrp: Human-readable part
            data: Data values
        
        Returns:
            Checksum values
        """
        values = Bech32m.hrp_expand(hrp) + data
        polymod = Bech32m.polymod(values + [0, 0, 0, 0, 0, 0]) ^ Bech32m.BECH32M_CONST
        return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]
    
    @staticmethod
    def verify_checksum(hrp: str, data: List[int]) -> bool:
        """
        Verify a Bech32m checksum.
        
        Args:
            hrp: Human-readable part
            data: Data values including checksum
        
        Returns:
            True if the checksum is valid, False otherwise
        """
        return Bech32m.polymod(Bech32m.hrp_expand(hrp) + data) == Bech32m.BECH32M_CONST
    
    @staticmethod
    def encode(hrp: str, data: List[int]) -> str:
        """
        Encode data using Bech32m.
        
        Args:
            hrp: Human-readable part
            data: Data values
        
        Returns:
            Bech32m encoded string
        """
        combined = data + Bech32m.create_checksum(hrp, data)
        return hrp + "1" + "".join([Bech32m.CHARSET[d] for d in combined])
    
    @staticmethod
    def decode(bech_str: str) -> Tuple[Optional[str], Optional[List[int]]]:
        """
        Decode a Bech32m encoded string.
        
        Args:
            bech_str: Bech32m encoded string
        
        Returns:
            Tuple of (hrp, data) or (None, None) if invalid
        """
        if not all(x in Bech32m.CHARSET for x in bech_str.lower().rsplit("1", 1)[1]):
            return None, None
        
        bech_str = bech_str.lower()
        pos = bech_str.rfind("1")
        if pos < 1 or pos + 7 > len(bech_str) or len(bech_str) > 90:
            return None, None
        
        hrp = bech_str[:pos]
        data = [Bech32m.CHARSET.find(x) for x in bech_str[pos+1:]]
        
        if not Bech32m.verify_checksum(hrp, data):
            return None, None
        
        return hrp, data[:-6]
    
    @staticmethod
    def convert_bits(data: List[int], from_bits: int, to_bits: int, pad: bool = True) -> Optional[List[int]]:
        """
        Convert between bit sizes.
        
        Args:
            data: Input data
            from_bits: Source bit size
            to_bits: Target bit size
            pad: Whether to pad the output
        
        Returns:
            Converted data or None if invalid
        """
        acc = 0
        bits = 0
        ret = []
        maxv = (1 << to_bits) - 1
        max_acc = (1 << (from_bits + to_bits - 1)) - 1
        
        for value in data:
            if value < 0 or (value >> from_bits):
                return None
            acc = ((acc << from_bits) | value) & max_acc
            bits += from_bits
            while bits >= to_bits:
                bits -= to_bits
                ret.append((acc >> bits) & maxv)
        
        if pad:
            if bits:
                ret.append((acc << (to_bits - bits)) & maxv)
        elif bits >= from_bits or ((acc << (to_bits - bits)) & maxv):
            return None
        
        return ret

class AddressGenerator:
    """Class for generating and validating Synergy Network addresses."""
    
    # Synergy Network address prefixes
    PREFIXES = ["sYnQ", "sYnU"]
    
    # Human-readable part for Bech32m encoding
    HRP = "syn"
    
    @staticmethod
    def generate_address(public_key: Union[bytes, str], prefix: Optional[str] = None) -> str:
        """
        Generate a Synergy Network address from a public key.
        
        Args:
            public_key: Public key (bytes or hex string)
            prefix: Optional address prefix ('sYnQ' or 'sYnU')
        
        Returns:
            Synergy Network address
        """
        # Convert hex string to bytes if needed
        if isinstance(public_key, str):
            public_key = bytes.fromhex(public_key)
        
        # Hash the public key with SHA3-256
        hash_bytes = hashlib.sha3_256(public_key).digest()
        
        # Convert 8-bit bytes to 5-bit values for Bech32m
        data = Bech32m.convert_bits(list(hash_bytes), 8, 5)
        
        # Encode with Bech32m
        bech32m_encoded = Bech32m.encode(AddressGenerator.HRP, data)
        
        # Select a prefix
        if prefix is not None:
            if prefix not in AddressGenerator.PREFIXES:
                raise ValueError(f"Invalid prefix: {prefix}. Must be one of {AddressGenerator.PREFIXES}")
            selected_prefix = prefix
        else:
            selected_prefix = random.choice(AddressGenerator.PREFIXES)
        
        # Combine prefix and encoded hash
        return selected_prefix + bech32m_encoded
    
    @staticmethod
    def validate_address(address: str) -> bool:
        """
        Validate a Synergy Network address.
        
        Args:
            address: Address to validate
        
        Returns:
            True if the address is valid, False otherwise
        """
        # Check prefix
        if not any(address.startswith(prefix) for prefix in AddressGenerator.PREFIXES):
            return False
        
        # Extract Bech32m part
        for prefix in AddressGenerator.PREFIXES:
            if address.startswith(prefix):
                bech32m_part = address[len(prefix):]
                break
        
        # Decode Bech32m
        hrp, data = Bech32m.decode(bech32m_part)
        
        # Check if decoding was successful and HRP matches
        if hrp is None or data is None or hrp != AddressGenerator.HRP:
            return False
        
        return True
    
    @staticmethod
    def get_address_type(address: str) -> Optional[str]:
        """
        Get the type of a Synergy Network address.
        
        Args:
            address: Address to check
        
        Returns:
            Address type ('quantum' or 'universal') or None if invalid
        """
        if not AddressGenerator.validate_address(address):
            return None
        
        if address.startswith("sYnQ"):
            return "quantum"
        elif address.startswith("sYnU"):
            return "universal"
        
        return None
    
    @staticmethod
    def extract_hash_from_address(address: str) -> Optional[bytes]:
        """
        Extract the hash from a Synergy Network address.
        
        Args:
            address: Address to extract hash from
        
        Returns:
            Hash bytes or None if invalid
        """
        if not AddressGenerator.validate_address(address):
            return None
        
        # Extract Bech32m part
        for prefix in AddressGenerator.PREFIXES:
            if address.startswith(prefix):
                bech32m_part = address[len(prefix):]
                break
        
        # Decode Bech32m
        hrp, data = Bech32m.decode(bech32m_part)
        
        if hrp is None or data is None:
            return None
        
        # Convert 5-bit values back to 8-bit bytes
        hash_bytes = bytes(Bech32m.convert_bits(data, 5, 8, False))
        
        return hash_bytes

# Example usage
if __name__ == "__main__":
    # Generate a random public key for testing
    public_key = bytes([random.randint(0, 255) for _ in range(32)])
    
    # Generate addresses with both prefixes
    address_q = AddressGenerator.generate_address(public_key, "sYnQ")
    address_u = AddressGenerator.generate_address(public_key, "sYnU")
    
    print(f"Public key: {public_key.hex()}")
    print(f"Quantum address: {address_q}")
    print(f"Universal address: {address_u}")
    
    # Validate addresses
    print(f"\nValidating quantum address: {AddressGenerator.validate_address(address_q)}")
    print(f"Validating universal address: {AddressGenerator.validate_address(address_u)}")
    
    # Get address types
    print(f"\nQuantum address type: {AddressGenerator.get_address_type(address_q)}")
    print(f"Universal address type: {AddressGenerator.get_address_type(address_u)}")
    
    # Extract hash from addresses
    hash_q = AddressGenerator.extract_hash_from_address(address_q)
    hash_u = AddressGenerator.extract_hash_from_address(address_u)
    
    print(f"\nHash from quantum address: {hash_q.hex() if hash_q else None}")
    print(f"Hash from universal address: {hash_u.hex() if hash_u else None}")
    
    # Test with invalid address
    invalid_address = "sYnXsyn1abcdef"
    print(f"\nValidating invalid address: {AddressGenerator.validate_address(invalid_address)}")
    print(f"Invalid address type: {AddressGenerator.get_address_type(invalid_address)}")
