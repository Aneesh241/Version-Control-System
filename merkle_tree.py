"""
Merkle Tree Implementation for Version Control System
=====================================================

A Merkle Tree is a binary tree where:
- Leaf nodes contain hashes of file contents
- Internal nodes contain hashes of their children's concatenated hashes
- The root hash represents the entire snapshot of files

This ensures data integrity: any change in any file will propagate up
and change the root hash, making tampering detectable.

Time Complexity: O(n) for construction, O(log n) for verification
Space Complexity: O(n) where n is the number of files
"""

import hashlib
from typing import List, Optional, Tuple


class MerkleNode:
    """
    Represents a node in the Merkle Tree.
    
    Attributes:
        hash: SHA-256 hash value of this node
        left: Reference to left child (for internal nodes)
        right: Reference to right child (for internal nodes)
        data: Original data (for leaf nodes only)
    """
    
    def __init__(self, hash_value: str, left=None, right=None, data: Optional[str] = None):
        self.hash = hash_value
        self.left = left
        self.right = right
        self.data = data  # Only set for leaf nodes
    
    def is_leaf(self) -> bool:
        """Check if this node is a leaf node."""
        return self.left is None and self.right is None


class MerkleTree:
    """
    Merkle Tree implementation for file integrity verification.
    
    Uses SHA-256 hashing and binary tree structure to create a tamper-proof
    snapshot of all files in a commit.
    
    Data Structure: Binary Tree
    - Each leaf represents a file hash
    - Each internal node is hash of concatenated children
    - Root hash represents entire commit state
    """
    
    def __init__(self, file_data: List[Tuple[str, str]]):
        """
        Initialize Merkle Tree from file data.
        
        Args:
            file_data: List of (filename, content) tuples
            
        Algorithm:
        1. Create leaf nodes for each file (O(n))
        2. Build tree bottom-up by pairing nodes (O(n))
        3. If odd number of nodes, duplicate last node
        """
        self.file_data = file_data
        self.root = self._build_tree()
    
    @staticmethod
    def compute_hash(data: str) -> str:
        """
        Compute SHA-256 hash of data.
        
        Args:
            data: String data to hash
            
        Returns:
            Hexadecimal string representation of SHA-256 hash
            
        Time Complexity: O(m) where m is length of data
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _build_tree(self) -> Optional[MerkleNode]:
        """
        Build Merkle Tree from file data using bottom-up approach.
        
        Returns:
            Root node of the Merkle Tree
            
        Algorithm:
        1. Create leaf nodes for each file
        2. While more than one node exists:
           a. Pair consecutive nodes
           b. Create parent with hash of concatenated children
           c. If odd number, duplicate last node
        3. Return final root node
        
        Time Complexity: O(n) - each node processed once
        Space Complexity: O(n) - stores all nodes
        """
        if not self.file_data:
            # Empty tree - return node with hash of empty string
            return MerkleNode(self.compute_hash(""))
        
        # Step 1: Create leaf nodes for each file
        # Each leaf contains hash of file content
        nodes = []
        for filename, content in self.file_data:
            file_hash = self.compute_hash(f"{filename}:{content}")
            nodes.append(MerkleNode(file_hash, data=filename))
        
        # Step 2: Build tree bottom-up
        while len(nodes) > 1:
            temp_nodes = []
            
            # Process nodes in pairs
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                
                # If odd number of nodes, duplicate the last one
                if i + 1 < len(nodes):
                    right = nodes[i + 1]
                else:
                    right = nodes[i]  # Duplicate last node
                
                # Create parent node with combined hash
                combined_hash = self.compute_hash(left.hash + right.hash)
                parent = MerkleNode(combined_hash, left=left, right=right)
                temp_nodes.append(parent)
            
            nodes = temp_nodes
        
        return nodes[0] if nodes else None
    
    def get_root_hash(self) -> str:
        """
        Get the root hash of the Merkle Tree.
        
        Returns:
            SHA-256 hash of the root (represents entire commit state)
            
        Time Complexity: O(1)
        """
        return self.root.hash if self.root else ""
    
    def get_proof(self, filename: str) -> List[Tuple[str, str]]:
        """
        Generate Merkle proof for a specific file.
        
        A Merkle proof is a path from leaf to root with sibling hashes,
        allowing verification that a file is part of the commit.
        
        Args:
            filename: Name of file to generate proof for
            
        Returns:
            List of (position, hash) tuples representing the proof path
            position is 'left' or 'right' indicating sibling position
            
        Time Complexity: O(n) - worst case traverse entire tree
        """
        proof = []
        self._find_proof(self.root, filename, proof)
        return proof
    
    def _find_proof(self, node: Optional[MerkleNode], filename: str, 
                    proof: List[Tuple[str, str]]) -> bool:
        """
        Recursively find proof path for a file.
        
        Args:
            node: Current node in traversal
            filename: Target filename
            proof: List to accumulate proof path
            
        Returns:
            True if file found in this subtree, False otherwise
        """
        if not node:
            return False
        
        # If leaf node, check if it's our target
        if node.is_leaf():
            return node.data == filename
        
        # Search left subtree
        if self._find_proof(node.left, filename, proof):
            # Add right sibling to proof
            if node.right:
                proof.append(('right', node.right.hash))
            return True
        
        # Search right subtree
        if self._find_proof(node.right, filename, proof):
            # Add left sibling to proof
            if node.left:
                proof.append(('left', node.left.hash))
            return True
        
        return False
    
    def verify_proof(self, filename: str, content: str, 
                     proof: List[Tuple[str, str]], root_hash: str) -> bool:
        """
        Verify that a file is part of the commit using Merkle proof.
        
        Args:
            filename: Name of file to verify
            content: Content of file
            proof: Merkle proof (path to root)
            root_hash: Expected root hash
            
        Returns:
            True if proof is valid, False otherwise
            
        Algorithm:
        1. Compute hash of file
        2. For each sibling in proof:
           - Combine current hash with sibling
           - Compute new hash
        3. Compare final hash with root_hash
        
        Time Complexity: O(log n) - follows path to root
        """
        # Compute hash of the file
        current_hash = self.compute_hash(f"{filename}:{content}")
        
        # Traverse proof path, combining with siblings
        for position, sibling_hash in proof:
            if position == 'left':
                current_hash = self.compute_hash(sibling_hash + current_hash)
            else:  # position == 'right'
                current_hash = self.compute_hash(current_hash + sibling_hash)
        
        return current_hash == root_hash
    
    def __str__(self) -> str:
        """String representation showing tree structure."""
        if not self.root:
            return "Empty Merkle Tree"
        
        lines = []
        self._print_tree(self.root, "", True, lines)
        return "\n".join(lines)
    
    def _print_tree(self, node: Optional[MerkleNode], prefix: str, 
                    is_tail: bool, lines: List[str]):
        """Recursively build tree visualization."""
        if not node:
            return
        
        # Format node information
        if node.is_leaf():
            node_info = f"{node.hash[:8]}... (file: {node.data})"
        else:
            node_info = f"{node.hash[:8]}... (internal)"
        
        lines.append(prefix + ("└── " if is_tail else "├── ") + node_info)
        
        # Recursively print children
        if not node.is_leaf():
            children = [child for child in [node.left, node.right] if child]
            for i, child in enumerate(children):
                is_last = i == len(children) - 1
                extension = "    " if is_tail else "│   "
                self._print_tree(child, prefix + extension, is_last, lines)
