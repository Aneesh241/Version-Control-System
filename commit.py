"""
Commit Class Implementation for Version Control System
======================================================

A Commit represents a node in the Directed Acyclic Graph (DAG) of version history.
Each commit contains:
- Unique SHA-256 hash identifier
- Merkle root hash for file integrity
- Metadata (author, timestamp, message)
- Parent commit references (supporting merge commits with multiple parents)

The DAG structure ensures:
- No cycles (prevents circular dependencies)
- Efficient traversal and history tracking
- Support for branching and merging

Time Complexity: O(1) for commit creation
Space Complexity: O(n) where n is number of files in commit
"""

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional
from merkle_tree import MerkleTree


class Commit:
    """
    Represents a single commit in the version control system.
    
    Each commit is a node in the DAG with:
    - Unique SHA-256 hash (computed from all commit data)
    - Merkle root for file integrity verification
    - Parent references (edges in DAG)
    - Metadata (message, author, timestamp)
    - Snapshot of files at this point in history
    
    Data Structure: DAG Node
    - Parents: List of parent commit hashes (edges in DAG)
    - Files: Dictionary mapping filenames to contents
    - Merkle Tree: Binary tree for integrity verification
    """
    
    def __init__(self, 
                 message: str,
                 files: Dict[str, str],
                 parents: List[str] = None,
                 author: str = "default",
                 timestamp: Optional[datetime] = None):
        """
        Initialize a new commit.
        
        Args:
            message: Commit message describing changes
            files: Dictionary mapping filename to file content
            parents: List of parent commit hashes (empty for initial commit)
            author: Name of commit author
            timestamp: Time of commit (defaults to current time)
            
        Algorithm:
        1. Store metadata and file snapshot
        2. Build Merkle Tree from files
        3. Compute unique commit hash from all data
        
        Time Complexity: O(n) where n is number of files
        """
        self.message = message
        self.files = files.copy()  # Create snapshot
        self.parents = parents if parents else []
        self.author = author
        self.timestamp = timestamp if timestamp else datetime.now()
        
        # Build Merkle Tree for file integrity
        # Converts dict to list of (filename, content) tuples
        file_data = [(filename, content) for filename, content in sorted(files.items())]
        self.merkle_tree = MerkleTree(file_data)
        self.merkle_root = self.merkle_tree.get_root_hash()
        
        # Compute unique commit hash
        self.hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """
        Compute SHA-256 hash uniquely identifying this commit.
        
        Hash is computed from:
        - All parent commit hashes (establishes DAG relationships)
        - Merkle root hash (represents file snapshot)
        - Message, author, timestamp (metadata)
        
        This ensures:
        - Any change to files changes the hash (via Merkle root)
        - Any change to history changes the hash (via parents)
        - Commits are tamper-proof
        
        Returns:
            SHA-256 hash as hexadecimal string
            
        Time Complexity: O(p) where p is number of parents
        """
        # Create deterministic string representation of commit
        commit_data = {
            'parents': sorted(self.parents),  # Sorted for determinism
            'merkle_root': self.merkle_root,
            'message': self.message,
            'author': self.author,
            'timestamp': self.timestamp.isoformat()
        }
        
        # Convert to JSON and hash
        commit_string = json.dumps(commit_data, sort_keys=True)
        return hashlib.sha256(commit_string.encode('utf-8')).hexdigest()
    
    def get_file(self, filename: str) -> Optional[str]:
        """
        Retrieve file content from this commit.
        
        Args:
            filename: Name of file to retrieve
            
        Returns:
            File content or None if file not in commit
            
        Time Complexity: O(1) - dictionary lookup
        """
        return self.files.get(filename)
    
    def get_all_files(self) -> Dict[str, str]:
        """
        Get all files in this commit.
        
        Returns:
            Dictionary mapping filenames to contents
            
        Time Complexity: O(1)
        """
        return self.files.copy()
    
    def verify_integrity(self) -> bool:
        """
        Verify commit integrity using Merkle root.
        
        Recomputes Merkle root from current files and compares
        with stored root. If they don't match, commit has been tampered.
        
        Returns:
            True if integrity verified, False if tampered
            
        Time Complexity: O(n) where n is number of files
        """
        # Rebuild Merkle Tree from current files
        file_data = [(filename, content) for filename, content in sorted(self.files.items())]
        new_tree = MerkleTree(file_data)
        new_root = new_tree.get_root_hash()
        
        # Compare with stored root
        return new_root == self.merkle_root
    
    def get_changed_files(self, parent_commit: Optional['Commit']) -> Dict[str, str]:
        """
        Get files that changed between this commit and parent.
        
        Args:
            parent_commit: Parent commit to compare against (None for initial)
            
        Returns:
            Dictionary of changed files {filename: status}
            status can be 'added', 'modified', or 'deleted'
            
        Time Complexity: O(n) where n is total number of unique files
        """
        if not parent_commit:
            # All files are new in initial commit
            return {filename: 'added' for filename in self.files}
        
        changes = {}
        parent_files = parent_commit.get_all_files()
        
        # Check for added or modified files
        for filename, content in self.files.items():
            if filename not in parent_files:
                changes[filename] = 'added'
            elif parent_files[filename] != content:
                changes[filename] = 'modified'
        
        # Check for deleted files
        for filename in parent_files:
            if filename not in self.files:
                changes[filename] = 'deleted'
        
        return changes
    
    def to_dict(self) -> Dict:
        """
        Convert commit to dictionary for serialization.
        
        Returns:
            Dictionary containing all commit data
            
        Time Complexity: O(n) where n is number of files
        """
        return {
            'hash': self.hash,
            'message': self.message,
            'author': self.author,
            'timestamp': self.timestamp.isoformat(),
            'parents': self.parents,
            'merkle_root': self.merkle_root,
            'files': self.files
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Commit':
        """
        Reconstruct commit from dictionary.
        
        Args:
            data: Dictionary containing commit data
            
        Returns:
            Reconstructed Commit object
            
        Time Complexity: O(n) where n is number of files
        """
        timestamp = datetime.fromisoformat(data['timestamp'])
        commit = cls(
            message=data['message'],
            files=data['files'],
            parents=data['parents'],
            author=data['author'],
            timestamp=timestamp
        )
        return commit
    
    def __str__(self) -> str:
        """Human-readable string representation of commit."""
        parent_info = f"Parents: {', '.join(p[:8] for p in self.parents)}" if self.parents else "Initial commit"
        return (f"Commit: {self.hash[:8]}\n"
                f"{parent_info}\n"
                f"Author: {self.author}\n"
                f"Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Merkle Root: {self.merkle_root[:8]}...\n"
                f"\n    {self.message}\n"
                f"\nFiles ({len(self.files)}): {', '.join(self.files.keys())}")
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Commit(hash={self.hash[:8]}, message='{self.message}', files={len(self.files)})"
    
    def __eq__(self, other) -> bool:
        """Check equality based on commit hash."""
        if not isinstance(other, Commit):
            return False
        return self.hash == other.hash
    
    def __hash__(self):
        """Make commits hashable for use in sets/dicts."""
        return hash(self.hash)
