"""
Repository Class Implementation for Version Control System
=========================================================

The Repository is the core of the VCS, managing:
- DAG of commits (using hash map for O(1) lookup)
- Adjacency list for parent-child relationships
- Branch management
- Staging area for pending changes
- Stack for rollback operations

Data Structures Used:
1. Hash Map (dict): commits storage - O(1) access by hash
2. Adjacency List (dict): commit relationships - O(1) edge lookup
3. Stack (list): rollback history - O(1) push/pop
4. Staging Area (dict): files pending commit

Time Complexities:
- Add file to staging: O(1)
- Create commit: O(n) where n = staged files
- Retrieve commit: O(1)
- Rollback: O(1) stack pop + O(n) file restoration
"""

import os
import json
import pickle
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from commit import Commit
from pathlib import Path


class Repository:
    """
    Main repository class managing version control operations.
    
    Data Structures:
    - commits: Hash map {commit_hash: Commit} for O(1) commit access
    - commit_graph: Adjacency list {commit_hash: [child_hashes]} for DAG
    - branches: Hash map {branch_name: commit_hash} for branch heads
    - staging_area: Hash map {filename: content} for pending changes
    - rollback_stack: Stack of commit hashes for undo operations
    - current_branch: String tracking active branch
    - head: String pointing to current commit hash
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize repository data structures.
        
        Args:
            repo_path: Path to repository root directory
            
        Data Structure Initialization:
        - commits: HashMap for O(1) commit retrieval
        - commit_graph: Adjacency list for DAG traversal
        - branches: HashMap for branch management
        - staging_area: HashMap for file staging
        - rollback_stack: Stack for undo functionality
        """
        self.repo_path = Path(repo_path)
        self.vcs_dir = self.repo_path / '.vcs'
        
        # Hash Map: commit_hash -> Commit object
        # Time Complexity: O(1) for lookup, insertion
        self.commits: Dict[str, Commit] = {}
        
        # Adjacency List: commit_hash -> [child_commit_hashes]
        # Represents edges in DAG (parent -> children)
        # Time Complexity: O(1) for lookup, O(k) to get children where k = #children
        self.commit_graph: Dict[str, List[str]] = {}
        
        # Hash Map: branch_name -> commit_hash
        # Tracks head commit of each branch
        self.branches: Dict[str, str] = {}
        
        # Hash Map: filename -> content
        # Staging area for files pending commit
        self.staging_area: Dict[str, str] = {}
        
        # Stack: List of commit hashes
        # Used for rollback/undo operations (LIFO)
        # Push: O(1), Pop: O(1)
        self.rollback_stack: List[str] = []
        
        # Current state
        self.current_branch: str = 'main'
        self.head: Optional[str] = None  # Hash of current commit
        
        # Audit trail
        self.audit_log: List[Dict] = []
    
    def init(self) -> str:
        """
        Initialize a new repository.
        
        Creates .vcs directory structure:
        - .vcs/commits/: Serialized commit objects
        - .vcs/objects/: File storage
        - .vcs/refs/: Branch references
        - .vcs/config: Repository configuration
        
        Returns:
            Success message
            
        Time Complexity: O(1)
        """
        if self.vcs_dir.exists():
            return "Repository already initialized"
        
        # Create directory structure
        self.vcs_dir.mkdir(parents=True)
        (self.vcs_dir / 'commits').mkdir()
        (self.vcs_dir / 'objects').mkdir()
        (self.vcs_dir / 'refs').mkdir()
        
        # Initialize main branch
        self.branches['main'] = None
        self.current_branch = 'main'
        
        # Save initial state
        self._save_repo_state()
        
        # Audit log
        self._log_action('init', 'Repository initialized')
        
        return f"Initialized empty VCS repository in {self.vcs_dir}"
    
    def add(self, filepath: str) -> str:
        """
        Add file to staging area.
        
        Args:
            filepath: Path to file (relative to repo root)
            
        Returns:
            Success message
            
        Algorithm:
        1. Read file content from working directory
        2. Add to staging_area hash map
        
        Time Complexity: O(m) where m = file size
        Space Complexity: O(m) - stores file in staging area
        """
        full_path = self.repo_path / filepath
        
        if not full_path.exists():
            return f"Error: File '{filepath}' not found"
        
        if not full_path.is_file():
            return f"Error: '{filepath}' is not a file"
        
        # Read file content with robust encoding handling.
        # Try common text encodings first, then fall back to binary stored as base64.
        content = None
        try_encodings = ['utf-8', 'utf-8-sig', 'latin-1']
        for enc in try_encodings:
            try:
                with open(full_path, 'r', encoding=enc) as f:
                    content = f.read()
                # If read succeeded, break out
                break
            except UnicodeDecodeError:
                # Try next encoding
                continue
            except Exception as e:
                return f"Error reading file: {e}"

        if content is None:
            # Could not decode as text; read as binary and store base64 string
            try:
                import base64
                with open(full_path, 'rb') as f:
                    raw = f.read()
                b64 = base64.b64encode(raw).decode('ascii')
                # Prefix to indicate binary data stored as base64
                content = f"__binary_base64__:{b64}"
            except Exception as e:
                return f"Error reading file in binary mode: {e}"
        
        # Add to staging area (Hash Map insertion: O(1))
        self.staging_area[filepath] = content
        
        self._log_action('add', f'Added {filepath} to staging area')
        # Persist state so CLI runs in separate processes see the staged file
        try:
            self._save_repo_state()
        except Exception:
            # Don't fail add if saving state fails; we already staged in memory
            pass
        
        return f"Added '{filepath}' to staging area"
    
    def commit(self, message: str, author: str = "default") -> str:
        """
        Create a new commit from staged files.
        
        Args:
            message: Commit message
            author: Commit author name
            
        Returns:
            Success message with commit hash
            
        Algorithm:
        1. Check if staging area has files
        2. Get current commit's files (if exists)
        3. Merge current files with staged changes
        4. Create new Commit object (builds Merkle tree)
        5. Add to commits hash map
        6. Update commit_graph adjacency list
        7. Update branch pointer and HEAD
        8. Push to rollback stack
        9. Clear staging area
        
        Time Complexity: O(n) where n = total files in commit
        Space Complexity: O(n) - stores full file snapshot
        """
        if not self.staging_area:
            return "Nothing to commit (staging area empty)"
        
        # Get parent commit's files
        parent_files = {}
        parents = []
        
        if self.head:
            parent_commit = self.commits[self.head]
            parent_files = parent_commit.get_all_files()
            parents = [self.head]
        
        # Merge parent files with staged changes
        new_files = parent_files.copy()
        new_files.update(self.staging_area)
        
        # Create new commit (O(n) - builds Merkle tree)
        new_commit = Commit(
            message=message,
            files=new_files,
            parents=parents,
            author=author
        )
        
        # Add to commits hash map (O(1))
        self.commits[new_commit.hash] = new_commit
        
        # Update commit_graph adjacency list (O(1))
        if self.head:
            if self.head not in self.commit_graph:
                self.commit_graph[self.head] = []
            self.commit_graph[self.head].append(new_commit.hash)
        
        # Initialize graph entry for new commit
        self.commit_graph[new_commit.hash] = []
        
        # Update branch pointer (O(1))
        self.branches[self.current_branch] = new_commit.hash
        
        # Update HEAD
        old_head = self.head
        self.head = new_commit.hash
        
        # Push to rollback stack (O(1))
        if old_head:
            self.rollback_stack.append(old_head)
        
        # Clear staging area
        staged_files = list(self.staging_area.keys())
        self.staging_area.clear()
        
        # Save state
        self._save_repo_state()
        self._save_commit(new_commit)
        
        # Audit log
        self._log_action('commit', f'Created commit {new_commit.hash[:8]} with message: {message}')
        
        return (f"[{self.current_branch} {new_commit.hash[:8]}] {message}\n"
                f" {len(staged_files)} file(s) changed")
    
    def status(self) -> str:
        """
        Show repository status.
        
        Returns:
            String showing current branch, staged files, and commit info
            
        Time Complexity: O(n) where n = staged files
        """
        status_lines = [f"On branch {self.current_branch}"]
        
        if self.head:
            commit = self.commits[self.head]
            status_lines.append(f"HEAD at {self.head[:8]}: {commit.message}")
        else:
            status_lines.append("No commits yet")
        
        if self.staging_area:
            status_lines.append(f"\nStaged files ({len(self.staging_area)}):")
            for filename in sorted(self.staging_area.keys()):
                status_lines.append(f"  + {filename}")
        else:
            status_lines.append("\nNo files staged for commit")
        
        return "\n".join(status_lines)
    
    def log(self, limit: Optional[int] = None) -> str:
        """
        Display commit history from HEAD.
        
        Args:
            limit: Maximum number of commits to show
            
        Returns:
            Formatted commit history
            
        Algorithm:
        1. Start from HEAD
        2. Follow parent pointers (traversing DAG backwards)
        3. Collect commits until no more parents or limit reached
        
        Time Complexity: O(c) where c = number of commits to show
        """
        if not self.head:
            return "No commits yet"
        
        log_lines = []
        current = self.head
        count = 0
        visited = set()  # Prevent infinite loops in case of data corruption
        
        # Traverse DAG backwards from HEAD
        while current and (limit is None or count < limit):
            if current in visited:
                break
            visited.add(current)
            
            commit = self.commits[current]
            log_lines.append(str(commit))
            log_lines.append("-" * 60)
            
            # Move to parent (following DAG edge backwards)
            if commit.parents:
                current = commit.parents[0]  # Follow first parent
            else:
                break
            
            count += 1
        
        return "\n".join(log_lines)
    
    def rollback(self, steps: int = 1) -> str:
        """
        Rollback to previous commit using stack.
        
        Args:
            steps: Number of commits to roll back
            
        Returns:
            Success message
            
        Algorithm:
        1. Pop commit hashes from rollback_stack
        2. Update HEAD to popped commit
        3. Update branch pointer
        4. Restore files from commit snapshot
        
        Time Complexity: O(steps + n) where n = files in commit
        Space Complexity: O(1) - stack pop is in-place
        """
        if not self.rollback_stack:
            return "Cannot rollback: no previous commits"
        
        if steps > len(self.rollback_stack):
            steps = len(self.rollback_stack)
        
        # Pop from stack (O(1) per pop)
        target_hash = None
        for _ in range(steps):
            target_hash = self.rollback_stack.pop()
        
        if not target_hash:
            return "Rollback failed"
        
        # Update HEAD and branch
        self.head = target_hash
        self.branches[self.current_branch] = target_hash
        
        # Clear staging area
        self.staging_area.clear()
        
        # Save state
        self._save_repo_state()
        
        commit = self.commits[target_hash]
        self._log_action('rollback', f'Rolled back {steps} commit(s) to {target_hash[:8]}')
        
        return (f"Rolled back {steps} commit(s)\n"
                f"HEAD is now at {target_hash[:8]}: {commit.message}")
    
    def create_branch(self, branch_name: str) -> str:
        """
        Create a new branch from current HEAD.
        
        Args:
            branch_name: Name for new branch
            
        Returns:
            Success message
            
        Time Complexity: O(1) - hash map insertion
        """
        if branch_name in self.branches:
            return f"Branch '{branch_name}' already exists"
        
        # Create branch pointing to current HEAD
        self.branches[branch_name] = self.head
        
        self._save_repo_state()
        self._log_action('branch', f'Created branch {branch_name}')
        
        return f"Created branch '{branch_name}'"
    
    def switch_branch(self, branch_name: str) -> str:
        """
        Switch to a different branch.
        
        Args:
            branch_name: Name of branch to switch to
            
        Returns:
            Success message
            
        Algorithm:
        1. Check if staging area is clean
        2. Update current_branch pointer
        3. Update HEAD to branch's commit
        4. Restore files from commit
        
        Time Complexity: O(n) where n = files in commit
        """
        if branch_name not in self.branches:
            return f"Branch '{branch_name}' does not exist"
        
        if self.staging_area:
            return "Cannot switch branch with staged changes. Commit or discard them first."
        
        old_branch = self.current_branch
        self.current_branch = branch_name
        self.head = self.branches[branch_name]
        
        self._save_repo_state()
        self._log_action('checkout', f'Switched from {old_branch} to {branch_name}')
        
        if self.head:
            commit = self.commits[self.head]
            return f"Switched to branch '{branch_name}'\nHEAD at {self.head[:8]}: {commit.message}"
        else:
            return f"Switched to branch '{branch_name}'\nNo commits yet"
    
    def list_branches(self) -> str:
        """
        List all branches.
        
        Returns:
            Formatted list of branches
            
        Time Complexity: O(b) where b = number of branches
        """
        lines = ["Branches:"]
        for branch_name in sorted(self.branches.keys()):
            prefix = "* " if branch_name == self.current_branch else "  "
            commit_hash = self.branches[branch_name]
            if commit_hash:
                lines.append(f"{prefix}{branch_name} -> {commit_hash[:8]}")
            else:
                lines.append(f"{prefix}{branch_name} (no commits)")
        return "\n".join(lines)
    
    def merge(self, source_branch: str) -> str:
        """
        Merge source branch into current branch.
        
        Args:
            source_branch: Branch to merge from
            
        Returns:
            Success message or conflict report
            
        Algorithm:
        1. Find common ancestor (LCA in DAG)
        2. Get file changes from both branches
        3. Detect conflicts (same file modified differently)
        4. If no conflicts, create merge commit with 2 parents
        5. If conflicts, return conflict report
        
        Time Complexity: O(V + E) for LCA + O(n) for file comparison
        where V = vertices (commits), E = edges, n = files
        """
        if source_branch not in self.branches:
            return f"Branch '{source_branch}' does not exist"
        
        if source_branch == self.current_branch:
            return "Cannot merge branch into itself"
        
        if self.staging_area:
            return "Cannot merge with staged changes. Commit or discard them first."
        
        source_hash = self.branches[source_branch]
        target_hash = self.head
        
        if not source_hash:
            return f"Branch '{source_branch}' has no commits"
        
        if not target_hash:
            return "Current branch has no commits"
        
        # Check if already merged (source is ancestor of target)
        if self._is_ancestor(source_hash, target_hash):
            return f"Already up to date. {source_branch} is ancestor of {self.current_branch}"
        
        # Fast-forward merge if target is ancestor of source
        if self._is_ancestor(target_hash, source_hash):
            self.head = source_hash
            self.branches[self.current_branch] = source_hash
            self._save_repo_state()
            self._log_action('merge', f'Fast-forward merge of {source_branch} into {self.current_branch}')
            return f"Fast-forward merge: {self.current_branch} -> {source_hash[:8]}"
        
        # Find common ancestor (LCA)
        common_ancestor = self._find_common_ancestor(target_hash, source_hash)
        
        # Get commits
        target_commit = self.commits[target_hash]
        source_commit = self.commits[source_hash]
        
        # Detect conflicts
        conflicts = self._detect_conflicts(target_commit, source_commit, common_ancestor)
        
        if conflicts:
            conflict_report = [f"Merge conflict detected in {len(conflicts)} file(s):"]
            for filename in conflicts:
                conflict_report.append(f"  ! {filename}")
            conflict_report.append("\nResolve conflicts manually and commit")
            return "\n".join(conflict_report)
        
        # No conflicts - create merge commit
        merged_files = target_commit.get_all_files().copy()
        source_files = source_commit.get_all_files()
        
        # Apply changes from source
        for filename, content in source_files.items():
            merged_files[filename] = content
        
        # Create merge commit with 2 parents
        merge_commit = Commit(
            message=f"Merge branch '{source_branch}' into {self.current_branch}",
            files=merged_files,
            parents=[target_hash, source_hash],  # Two parents for merge
            author="system"
        )
        
        # Add to repository
        self.commits[merge_commit.hash] = merge_commit
        
        # Update graph (both parents point to merge commit)
        self.commit_graph[target_hash].append(merge_commit.hash)
        self.commit_graph[source_hash].append(merge_commit.hash)
        self.commit_graph[merge_commit.hash] = []
        
        # Update HEAD and branch
        old_head = self.head
        self.head = merge_commit.hash
        self.branches[self.current_branch] = merge_commit.hash
        self.rollback_stack.append(old_head)
        
        self._save_repo_state()
        self._save_commit(merge_commit)
        self._log_action('merge', f'Merged {source_branch} into {self.current_branch}')
        
        return f"Merged '{source_branch}' into '{self.current_branch}'\nMerge commit: {merge_commit.hash[:8]}"
    
    def _is_ancestor(self, ancestor_hash: str, descendant_hash: str) -> bool:
        """
        Check if ancestor_hash is ancestor of descendant_hash in DAG.
        
        Uses BFS to traverse DAG backwards from descendant.
        
        Time Complexity: O(V + E) where V = commits, E = edges
        """
        if ancestor_hash == descendant_hash:
            return True
        
        visited = set()
        queue = [descendant_hash]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            if current == ancestor_hash:
                return True
            
            commit = self.commits[current]
            queue.extend(commit.parents)
        
        return False
    
    def _find_common_ancestor(self, hash1: str, hash2: str) -> Optional[str]:
        """
        Find Lowest Common Ancestor (LCA) of two commits in DAG.
        
        Algorithm:
        1. Traverse ancestors of hash1, mark all as visited
        2. Traverse ancestors of hash2 until we find one that's visited
        3. That's the LCA (first common ancestor found)
        
        Time Complexity: O(V + E)
        """
        # Get all ancestors of hash1
        ancestors1 = set()
        queue = [hash1]
        
        while queue:
            current = queue.pop(0)
            if current in ancestors1:
                continue
            ancestors1.add(current)
            
            commit = self.commits[current]
            queue.extend(commit.parents)
        
        # Find first common ancestor from hash2
        queue = [hash2]
        visited = set()
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            if current in ancestors1:
                return current
            
            commit = self.commits[current]
            queue.extend(commit.parents)
        
        return None
    
    def _detect_conflicts(self, commit1: Commit, commit2: Commit, 
                         ancestor_hash: Optional[str]) -> List[str]:
        """
        Detect merge conflicts between two commits.
        
        A conflict occurs when:
        - Same file modified differently in both branches
        - File deleted in one branch but modified in other
        
        Returns:
            List of conflicting filenames
            
        Time Complexity: O(n) where n = total unique files
        """
        conflicts = []
        
        files1 = commit1.get_all_files()
        files2 = commit2.get_all_files()
        
        # Get ancestor files if exists
        ancestor_files = {}
        if ancestor_hash:
            ancestor_commit = self.commits.get(ancestor_hash)
            if ancestor_commit:
                ancestor_files = ancestor_commit.get_all_files()
        
        # Check all files in both commits
        all_files = set(files1.keys()) | set(files2.keys())
        
        for filename in all_files:
            in_1 = filename in files1
            in_2 = filename in files2
            in_ancestor = filename in ancestor_files
            
            # Both branches modified the file
            if in_1 and in_2:
                if files1[filename] != files2[filename]:
                    # Check if both actually changed from ancestor
                    if in_ancestor:
                        changed_1 = files1[filename] != ancestor_files[filename]
                        changed_2 = files2[filename] != ancestor_files[filename]
                        if changed_1 and changed_2:
                            conflicts.append(filename)
                    else:
                        # New file in both branches with different content
                        conflicts.append(filename)
            
            # File deleted in one branch, modified in other
            elif in_ancestor:
                if (in_1 and not in_2) or (in_2 and not in_1):
                    # Check if it was actually modified
                    if in_1 and files1[filename] != ancestor_files[filename]:
                        conflicts.append(filename)
                    elif in_2 and files2[filename] != ancestor_files[filename]:
                        conflicts.append(filename)
        
        return conflicts
    
    def get_commit_graph_dot(self) -> str:
        """
        Generate DOT format representation of commit DAG.
        
        Returns:
            DOT format string for visualization
            
        Time Complexity: O(V + E)
        """
        lines = ['digraph CommitGraph {']
        lines.append('  rankdir=BT;')  # Bottom to top (oldest to newest)
        lines.append('  node [shape=box];')
        
        # Add nodes (commits)
        for commit_hash, commit in self.commits.items():
            label = f"{commit_hash[:8]}\\n{commit.message[:20]}"
            lines.append(f'  "{commit_hash[:8]}" [label="{label}"];')
        
        # Add edges (parent-child relationships)
        for parent_hash, children in self.commit_graph.items():
            for child_hash in children:
                lines.append(f'  "{parent_hash[:8]}" -> "{child_hash[:8]}";')
        
        # Highlight branches
        for branch_name, commit_hash in self.branches.items():
            if commit_hash:
                color = "red" if branch_name == self.current_branch else "blue"
                lines.append(f'  "{commit_hash[:8]}" [color={color}, penwidth=2];')
        
        lines.append('}')
        return '\n'.join(lines)
    
    def _log_action(self, action: str, details: str):
        """Add entry to audit log."""
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details
        })
    
    def get_audit_log(self) -> str:
        """Get formatted audit log."""
        if not self.audit_log:
            return "No actions recorded"
        
        lines = ["Audit Log:", "=" * 60]
        for entry in self.audit_log:
            lines.append(f"[{entry['timestamp']}] {entry['action']}: {entry['details']}")
        return "\n".join(lines)
    
    def _save_repo_state(self):
        """Save repository state to disk."""
        state = {
            'branches': self.branches,
            'current_branch': self.current_branch,
            'head': self.head,
            'staging_area': self.staging_area,
            'rollback_stack': self.rollback_stack,
            'commit_graph': self.commit_graph,
            'audit_log': self.audit_log
        }
        
        state_file = self.vcs_dir / 'state.json'
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _save_commit(self, commit: Commit):
        """Save commit object to disk."""
        commit_file = self.vcs_dir / 'commits' / f"{commit.hash}.pkl"
        with open(commit_file, 'wb') as f:
            pickle.dump(commit, f)
    
    def _load_repo_state(self):
        """Load repository state from disk."""
        state_file = self.vcs_dir / 'state.json'
        if not state_file.exists():
            return
        
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        self.branches = state.get('branches', {})
        self.current_branch = state.get('current_branch', 'main')
        self.head = state.get('head')
        self.staging_area = state.get('staging_area', {})
        self.rollback_stack = state.get('rollback_stack', [])
        self.commit_graph = state.get('commit_graph', {})
        self.audit_log = state.get('audit_log', [])
        
        # Load commits
        commits_dir = self.vcs_dir / 'commits'
        if commits_dir.exists():
            for commit_file in commits_dir.glob('*.pkl'):
                with open(commit_file, 'rb') as f:
                    commit = pickle.load(f)
                    self.commits[commit.hash] = commit
    
    @classmethod
    def load(cls, repo_path: str) -> 'Repository':
        """Load existing repository from disk."""
        repo = cls(repo_path)
        if (repo.vcs_dir / 'state.json').exists():
            repo._load_repo_state()
        return repo
