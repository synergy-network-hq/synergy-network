"""
PBFT Consensus Module for Synergy Network

This module implements the PBFT (Practical Byzantine Fault Tolerance) consensus
algorithm used within validator clusters in the Proof of Synergy mechanism.
"""

import enum
import time
import hashlib
import json
from typing import Dict, List, Any, Optional, Set, Tuple

class MessageType(enum.Enum):
    """Types of messages in the PBFT protocol."""
    PRE_PREPARE = 1
    PREPARE = 2
    COMMIT = 3
    VIEW_CHANGE = 4
    NEW_VIEW = 5

class ConsensusState(enum.Enum):
    """States of the PBFT consensus process."""
    IDLE = 1
    PRE_PREPARED = 2
    PREPARED = 3
    COMMITTED = 4
    VIEW_CHANGING = 5

class PBFTMessage:
    """Class representing a message in the PBFT protocol."""
    
    def __init__(
        self,
        msg_type: MessageType,
        view_number: int,
        sequence_number: int,
        sender_id: str,
        content: Any,
        timestamp: int = None,
        signature: bytes = None
    ):
        self.msg_type = msg_type
        self.view_number = view_number
        self.sequence_number = sequence_number
        self.sender_id = sender_id
        self.content = content
        self.timestamp = timestamp or int(time.time())
        self.signature = signature
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PBFTMessage to dictionary."""
        return {
            "msg_type": self.msg_type.name,
            "view_number": self.view_number,
            "sequence_number": self.sequence_number,
            "sender_id": self.sender_id,
            "content": self.content,
            "timestamp": self.timestamp,
            "signature": self.signature.hex() if self.signature else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PBFTMessage':
        """Create PBFTMessage from dictionary."""
        return cls(
            msg_type=MessageType[data["msg_type"]],
            view_number=data["view_number"],
            sequence_number=data["sequence_number"],
            sender_id=data["sender_id"],
            content=data["content"],
            timestamp=data["timestamp"],
            signature=bytes.fromhex(data["signature"]) if data.get("signature") else None
        )
    
    def get_digest(self) -> str:
        """Get a digest of the message content."""
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.sha256(
            f"{self.view_number}:{self.sequence_number}:{content_str}".encode()
        ).hexdigest()

class PBFTConsensus:
    """
    Implementation of PBFT consensus algorithm for validator clusters.
    
    This implementation follows the original PBFT paper with modifications
    for the Synergy Network's validator cluster model.
    """
    
    def __init__(
        self,
        node_id: str,
        validators: List[str],
        primary_id: str = None,
        view_number: int = 0,
        sequence_number: int = 0,
        f: int = None  # Maximum number of faulty nodes tolerated
    ):
        self.node_id = node_id
        self.validators = validators
        self.primary_id = primary_id or validators[0]
        self.view_number = view_number
        self.sequence_number = sequence_number
        
        # Calculate f based on n = 3f + 1
        self.f = f if f is not None else (len(validators) - 1) // 3
        
        # Consensus state
        self.state = ConsensusState.IDLE
        
        # Message logs
        self.pre_prepare_log: Dict[int, Dict[str, PBFTMessage]] = {}  # seq_num -> digest -> message
        self.prepare_log: Dict[int, Dict[str, Dict[str, PBFTMessage]]] = {}  # seq_num -> digest -> sender_id -> message
        self.commit_log: Dict[int, Dict[str, Dict[str, PBFTMessage]]] = {}  # seq_num -> digest -> sender_id -> message
        
        # Results log
        self.results: Dict[int, Any] = {}  # seq_num -> result
        
        # View change related
        self.view_change_log: Dict[int, Dict[str, PBFTMessage]] = {}  # view_num -> sender_id -> message
        self.new_view_log: Dict[int, PBFTMessage] = {}  # view_num -> message
        
        # Timers
        self.request_timer: Dict[int, int] = {}  # seq_num -> expiration time
        self.view_change_timer: int = 0  # expiration time for view change
    
    def is_primary(self) -> bool:
        """Check if this node is the primary."""
        return self.node_id == self.primary_id
    
    def get_primary_for_view(self, view_number: int) -> str:
        """Get the primary node for a specific view."""
        return self.validators[view_number % len(self.validators)]
    
    def start_consensus(self, task_result: Any) -> Optional[int]:
        """
        Start consensus process for a task result.
        
        Args:
            task_result: Result of the task execution
        
        Returns:
            Sequence number if consensus started, None otherwise
        """
        if not self.is_primary():
            return None
        
        # Increment sequence number
        self.sequence_number += 1
        seq_num = self.sequence_number
        
        # Create pre-prepare message
        message = PBFTMessage(
            msg_type=MessageType.PRE_PREPARE,
            view_number=self.view_number,
            sequence_number=seq_num,
            sender_id=self.node_id,
            content=task_result
        )
        
        # Process the pre-prepare message locally
        self._process_pre_prepare(message)
        
        # Set request timer
        self.request_timer[seq_num] = int(time.time()) + 30  # 30 seconds timeout
        
        return seq_num
    
    def receive_message(self, message_dict: Dict[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Process a received PBFT message.
        
        Args:
            message_dict: Dictionary representation of the message
        
        Returns:
            Tuple of (success, result)
            - success: True if message was processed successfully
            - result: Task result if consensus was reached, None otherwise
        """
        message = PBFTMessage.from_dict(message_dict)
        
        # Verify message is from a known validator
        if message.sender_id not in self.validators:
            return False, None
        
        # Process based on message type
        if message.msg_type == MessageType.PRE_PREPARE:
            return self._process_pre_prepare(message), None
        
        elif message.msg_type == MessageType.PREPARE:
            success = self._process_prepare(message)
            result = self._check_prepared(message.sequence_number, message.get_digest())
            return success, result
        
        elif message.msg_type == MessageType.COMMIT:
            success = self._process_commit(message)
            result = self._check_committed(message.sequence_number, message.get_digest())
            return success, result
        
        elif message.msg_type == MessageType.VIEW_CHANGE:
            return self._process_view_change(message), None
        
        elif message.msg_type == MessageType.NEW_VIEW:
            return self._process_new_view(message), None
        
        return False, None
    
    def _process_pre_prepare(self, message: PBFTMessage) -> bool:
        """
        Process a pre-prepare message.
        
        Args:
            message: The pre-prepare message
        
        Returns:
            True if message was processed successfully
        """
        # Verify view number
        if message.view_number != self.view_number:
            return False
        
        # Verify sender is the primary for this view
        if message.sender_id != self.get_primary_for_view(self.view_number):
            return False
        
        # Verify we haven't already processed this sequence number
        if message.sequence_number in self.results:
            return False
        
        # Get message digest
        digest = message.get_digest()
        
        # Store in log
        if message.sequence_number not in self.pre_prepare_log:
            self.pre_prepare_log[message.sequence_number] = {}
        self.pre_prepare_log[message.sequence_number][digest] = message
        
        # Update state
        self.state = ConsensusState.PRE_PREPARED
        
        # If not primary, send prepare message
        if not self.is_primary():
            prepare_message = PBFTMessage(
                msg_type=MessageType.PREPARE,
                view_number=self.view_number,
                sequence_number=message.sequence_number,
                sender_id=self.node_id,
                content=digest
            )
            
            # Process prepare message locally
            self._process_prepare(prepare_message)
            
            # Return prepare message for broadcasting
            return True
        
        return True
    
    def _process_prepare(self, message: PBFTMessage) -> bool:
        """
        Process a prepare message.
        
        Args:
            message: The prepare message
        
        Returns:
            True if message was processed successfully
        """
        # Verify view number
        if message.view_number != self.view_number:
            return False
        
        # Verify we have received a pre-prepare for this sequence number
        if message.sequence_number not in self.pre_prepare_log:
            return False
        
        # Get digest
        digest = message.content
        
        # Verify we have a matching pre-prepare
        if digest not in self.pre_prepare_log[message.sequence_number]:
            return False
        
        # Store in log
        if message.sequence_number not in self.prepare_log:
            self.prepare_log[message.sequence_number] = {}
        if digest not in self.prepare_log[message.sequence_number]:
            self.prepare_log[message.sequence_number][digest] = {}
        self.prepare_log[message.sequence_number][digest][message.sender_id] = message
        
        return True
    
    def _check_prepared(self, sequence_number: int, digest: str) -> Optional[Any]:
        """
        Check if we have reached the prepared state for a request.
        
        Args:
            sequence_number: Sequence number of the request
            digest: Digest of the request
        
        Returns:
            None if not prepared, otherwise sends commit message
        """
        # Verify we have logs for this sequence number and digest
        if (sequence_number not in self.prepare_log or
            digest not in self.prepare_log[sequence_number]):
            return None
        
        # Count prepare messages
        prepare_count = len(self.prepare_log[sequence_number][digest])
        
        # We need 2f prepare messages to move to prepared state
        if prepare_count >= 2 * self.f:
            # Update state
            self.state = ConsensusState.PREPARED
            
            # Send commit message
            commit_message = PBFTMessage(
                msg_type=MessageType.COMMIT,
                view_number=self.view_number,
                sequence_number=sequence_number,
                sender_id=self.node_id,
                content=digest
            )
            
            # Process commit message locally
            self._process_commit(commit_message)
            
            # Return commit message for broadcasting
            return commit_message
        
        return None
    
    def _process_commit(self, message: PBFTMessage) -> bool:
        """
        Process a commit message.
        
        Args:
            message: The commit message
        
        Returns:
            True if message was processed successfully
        """
        # Verify view number
        if message.view_number != self.view_number:
            return False
        
        # Get digest
        digest = message.content
        
        # Store in log
        if message.sequence_number not in self.commit_log:
            self.commit_log[message.sequence_number] = {}
        if digest not in self.commit_log[message.sequence_number]:
            self.commit_log[message.sequence_number][digest] = {}
        self.commit_log[message.sequence_number][digest][message.sender_id] = message
        
        return True
    
    def _check_committed(self, sequence_number: int, digest: str) -> Optional[Any]:
        """
        Check if we have reached the committed state for a request.
        
        Args:
            sequence_number: Sequence number of the request
            digest: Digest of the request
        
        Returns:
            Result if committed, None otherwise
        """
        # Verify we have logs for this sequence number and digest
        if (sequence_number not in self.commit_log or
            digest not in self.commit_log[sequence_number]):
            return None
        
        # Count commit messages
        commit_count = len(self.commit_log[sequence_number][digest])
        
        # We need 2f+1 commit messages to move to committed state
        if commit_count >= 2 * self.f + 1:
            # Update state
            self.state = ConsensusState.COMMITTED
            
            # Get the result from pre-prepare message
            result = self.pre_prepare_log[sequence_number][digest].content
            
            # Store result
            self.results[sequence_number] = result
            
            # Clear request timer
            if sequence_number in self.request_timer:
                del self.request_timer[sequence_number]
            
            return result
        
        return None
    
    def check_timers(self) -> Optional[PBFTMessage]:
        """
        Check timers and trigger view change if needed.
        
        Returns:
            View change message if view change triggered, None otherwise
        """
        current_time = int(time.time())
        
        # Check request timers
        for seq_num, expiration in list(self.request_timer.items()):
            if current_time > expiration:
                # Request timed out, trigger view change
                return self.start_view_change()
        
        # Check view change timer
        if self.view_change_timer > 0 and current_time > self.view_change_timer:
            # View change timed out, increment view and try again
            self.view_number += 1
            return self.start_view_change()
        
        return None
    
    def start_view_change(self) -> PBFTMessage:
        """
        Start a view change.
        
        Returns:
            View change message
        """
        # Increment view number
        self.view_number += 1
        
        # Update state
        self.state = ConsensusState.VIEW_CHANGING
        
        # Set view change timer
        self.view_change_timer = int(time.time()) + 30  # 30 seconds timeout
        
        # Create view change message
        message = PBFTMessage(
            msg_type=MessageType.VIEW_CHANGE,
            view_number=self.view_number,
            sequence_number=self.sequence_number,
            sender_id=self.node_id,
            content={
                "last_sequence": self.sequence_number,
                "prepared_messages": self._get_prepared_messages()
            }
        )
        
        # Process view change message locally
        self._process_view_change(message)
        
        return message
    
    def _get_prepared_messages(self) -> Dict[str, Any]:
        """
        Get all prepared messages for view change.
        
        Returns:
            Dictionary of prepared messages
        """
        prepared = {}
        
        for seq_num in self.prepare_log:
            for digest in self.prepare_log[seq_num]:
                prepare_count = len(self.prepare_log[seq_num][digest])
                
                if prepare_count >= 2 * self.f:
                    # This request was prepared
                    pre_prepare = self.pre_prepare_log[seq_num][digest].to_dict()
                    prepares = [m.to_dict() for m in self.prepare_log[seq_num][digest].values()]
                    
                    prepared[str(seq_num)] = {
                        "pre_prepare": pre_prepare,
                        "prepares": prepares
                    }
        
        return prepared
    
    def _process_view_change(self, message: PBFTMessage) -> bool:
        """
        Process a view change message.
        
        Args:
            message: The view change message
        
        Returns:
            True if message was processed successfully
        """
        # Verify view number is greater than current
        if message.view_number < self.view_number:
            return False
        
        # If view number is higher, update our view
        if message.view_number > self.view_number:
            self.view_number = message.view_number
            self.state = ConsensusState.VIEW_CHANGING
            self.view_change_timer = int(time.time()) + 30  # 30 seconds timeout
        
        # Store in log
        if message.view_number not in self.view_change_log:
            self.view_change_log[message.view_number] = {}
        self.view_change_log[message.view_number][message.sender_id] = message
        
        # Check if we have enough view change messages
        if len(self.view_change_log[message.view_number]) >= 2 * self.f + 1:
            # We have enough messages to complete view change
            
            # If I am the primary for the new view, send new view message
            if self.get_primary_for_view(message.view_number) == self.node_id:
                new_view_message = self._create_new_view_message(message.view_number)
                
                # Process new view message locally
                self._process_new_view(new_view_message)
                
                return True
        
        return True
    
    def _create_new_view_message(self, view_number: int) -> PBFTMessage:
        """
        Create a new view message.
        
        Args:
            view_number: The new view number
        
        Returns:
            New view message
        """
        # Get all view change messages for this view
        view_change_messages = list(self.view_change_log[view_number].values())
        
        # Select 2f+1 messages
        selected_messages = view_change_messages[:2 * self.f + 1]
        
        # Extract prepared messages from view change messages
        prepared_messages = {}
        for vc_msg in selected_messages:
            content = vc_msg.content
            for seq_num, data in content.get("prepared_messages", {}).items():
                if seq_num not in prepared_messages:
                    prepared_messages[seq_num] = data
        
        # Create new view message
        message = PBFTMessage(
            msg_type=MessageType.NEW_VIEW,
            view_number=view_number,
            sequence_number=self.sequence_number,
            sender_id=self.node_id,
            content={
                "view_change_messages": [m.to_dict() for m in selected_messages],
                "prepared_messages": prepared_messages
            }
        )
        
        return message
    
    def _process_new_view(self, message: PBFTMessage) -> bool:
        """
        Process a new view message.
        
        Args:
            message: The new view message
        
        Returns:
            True if message was processed successfully
        """
        # Verify sender is the primary for the new view
        if message.sender_id != self.get_primary_for_view(message.view_number):
            return False
        
        # Verify view number
        if message.view_number < self.view_number:
            return False
        
        # Store in log
        self.new_view_log[message.view_number] = message
        
        # Update view number
        self.view_number = message.view_number
        
        # Update primary
        self.primary_id = self.get_primary_for_view(self.view_number)
        
        # Reset view change timer
        self.view_change_timer = 0
        
        # Update state
        self.state = ConsensusState.IDLE
        
        # Process prepared messages
        content = message.content
        for seq_num_str, data in content.get("prepared_messages", {}).items():
            seq_num = int(seq_num_str)
            
            # Skip if we already have a result for this sequence number
            if seq_num in self.results:
                continue
            
            # Process pre-prepare message
            pre_prepare = PBFTMessage.from_dict(data["pre_prepare"])
            self._process_pre_prepare(pre_prepare)
            
            # Process prepare messages
            for prepare_dict in data["prepares"]:
                prepare = PBFTMessage.from_dict(prepare_dict)
                self._process_prepare(prepare)
            
            # Check if prepared
            digest = pre_prepare.get_digest()
            self._check_prepared(seq_num, digest)
        
        return True
    
    def get_state_info(self) -> Dict[str, Any]:
        """
        Get information about the current consensus state.
        
        Returns:
            Dictionary with state information
        """
        return {
            "node_id": self.node_id,
            "view_number": self.view_number,
            "sequence_number": self.sequence_number,
            "primary_id": self.primary_id,
            "is_primary": self.is_primary(),
            "state": self.state.name,
            "validators_count": len(self.validators),
            "f_value": self.f,
            "results_count": len(self.results)
        }
    
    def save_to_file(self, filename: str) -> None:
        """
        Save consensus state to a file.
        
        Args:
            filename: Path to save the file
        """
        data = {
            "node_id": self.node_id,
            "validators": self.validators,
            "primary_id": self.primary_id,
            "view_number": self.view_number,
            "sequence_number": self.sequence_number,
            "f": self.f,
            "state": self.state.name,
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'PBFTConsensus':
        """
        Load consensus state from a file.
        
        Args:
            filename: Path to the file
        
        Returns:
            Loaded PBFTConsensus instance
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
                consensus = cls(
                    node_id=data["node_id"],
                    validators=data["validators"],
                    primary_id=data["primary_id"],
                    view_number=data["view_number"],
                    sequence_number=data["sequence_number"],
                    f=data["f"]
                )
                
                consensus.state = ConsensusState[data["state"]]
                consensus.results = data["results"]
                
                return consensus
        
        except (FileNotFoundError, json.JSONDecodeError):
            # Return None if file doesn't exist or is invalid
            return None


# Example usage
if __name__ == "__main__":
    # Create a PBFT consensus instance
    validators = ["node_1", "node_2", "node_3", "node_4"]
    consensus = PBFTConsensus(node_id="node_1", validators=validators)
    
    print("Initial state:")
    print(consensus.get_state_info())
    
    # Start consensus for a task result
    task_result = {"task_id": "task_123", "result": "Task completed successfully"}
    seq_num = consensus.start_consensus(task_result)
    
    if seq_num:
        print(f"\nStarted consensus for sequence number: {seq_num}")
    
    # Simulate receiving prepare messages from other validators
    for validator_id in ["node_2", "node_3", "node_4"]:
        prepare_message = {
            "msg_type": "PREPARE",
            "view_number": consensus.view_number,
            "sequence_number": seq_num,
            "sender_id": validator_id,
            "content": consensus.pre_prepare_log[seq_num][list(consensus.pre_prepare_log[seq_num].keys())[0]].get_digest(),
            "timestamp": int(time.time()),
            "signature": None
        }
        
        success, result = consensus.receive_message(prepare_message)
        print(f"Received prepare from {validator_id}: {success}")
    
    # Simulate receiving commit messages from all validators
    for validator_id in validators:
        commit_message = {
            "msg_type": "COMMIT",
            "view_number": consensus.view_number,
            "sequence_number": seq_num,
            "sender_id": validator_id,
            "content": consensus.pre_prepare_log[seq_num][list(consensus.pre_prepare_log[seq_num].keys())[0]].get_digest(),
            "timestamp": int(time.time()),
            "signature": None
        }
        
        success, result = consensus.receive_message(commit_message)
        print(f"Received commit from {validator_id}: {success}")
        
        if result:
            print(f"\nConsensus reached for sequence number {seq_num}!")
            print(f"Result: {result}")
    
    # Check final state
    print("\nFinal state:")
    print(consensus.get_state_info())
    
    # Save to file
    consensus.save_to_file("pbft_state.json")
    print("\nSaved consensus state to pbft_state.json")
