# VCS - Git-like Version Control System with Secure Commit Tracking

A fully-featured version control system built from scratch in Python, implementing core Git concepts with advanced data structures and cryptographic security.

## 🎯 Features

### Core Functionality
- **DAG-based Commit History**: Directed Acyclic Graph structure for version tracking
- **SHA-256 Cryptographic Hashing**: Secure commit identification and tamper detection
- **Merkle Tree Integrity**: File integrity verification for each commit
- **Branch Management**: Create, switch, and merge branches
- **Conflict Detection**: Automatic merge conflict identification
- **Stack-based Rollback**: Undo commits using efficient stack operations
- **Audit Trail**: Complete log of all repository operations
- **Graph Visualization**: Optional commit DAG visualization

### Data Structures Used

| Data Structure | Purpose | Time Complexity |
|---------------|---------|-----------------|
| **Hash Map** | Commit storage & retrieval | O(1) lookup |
| **Adjacency List** | DAG representation | O(1) edge lookup |
| **Stack** | Rollback operations | O(1) push/pop |
| **Merkle Tree** | File integrity verification | O(log n) verify |
| **Binary Tree** | Merkle tree structure | O(n) build |

### Security Features
- SHA-256 hashing for commit integrity
- Merkle root verification for file tampering detection
- Cryptographic proof of file inclusion
- Tamper-proof commit history

## 📋 Requirements

### Python Version
- Python 3.7 or higher

### Required Modules (Built-in)
- `hashlib` - SHA-256 cryptographic hashing
- `json` - Repository state serialization
- `pickle` - Commit object persistence
- `pathlib` - Cross-platform path handling
- `datetime` - Timestamp management
- `argparse` - CLI argument parsing

### Optional Dependencies (for visualization)
```bash
pip install networkx matplotlib
```

## 🚀 Installation

1. **Clone or download** the project files:
```bash
cd your-project-directory
```

2. **Ensure all files are present**:
   - `main.py` - Entry point
   - `cli.py` - Command-line interface
   - `repository.py` - Core repository logic
   - `commit.py` - Commit implementation
   - `merkle_tree.py` - Merkle tree structure
   - `visualization.py` - Graph visualization (optional)

3. **Install optional dependencies** (for graph visualization):
```bash
pip install networkx matplotlib
```

## 📖 Usage

### Basic Commands

#### Initialize Repository
```bash
python main.py init
```

#### Add Files to Staging Area
```bash
python main.py add file1.txt
python main.py add file1.txt file2.py file3.md
```

#### Create Commit
```bash
python main.py commit -m "Initial commit"
python main.py commit -m "Add feature" -a "John Doe"
```

#### Check Status
```bash
python main.py status
```

#### View Commit History
```bash
python main.py log
python main.py log -n 5  # Show last 5 commits
```

### Branch Operations

#### Create Branch
```bash
python main.py branch feature-x
```

#### List All Branches
```bash
python main.py branches
```

#### Switch Branch
```bash
python main.py checkout feature-x
```

#### Merge Branch
```bash
python main.py checkout main
python main.py merge feature-x
```

### Advanced Operations

#### Rollback Commits
```bash
python main.py rollback        # Rollback 1 commit
python main.py rollback 3      # Rollback 3 commits
```

#### View Audit Log
```bash
python main.py audit
```

#### Visualize Commit Graph
```bash
# Generate PNG (requires networkx and matplotlib)
python main.py graph -o commits.png

# Export DOT format (for Graphviz)
python main.py graph --format dot -o commits.dot
dot -Tpng commits.dot -o commits.png
```

#### Help
```bash
python main.py help
```

## 💡 Complete Example Workflow

```bash
# 1. Initialize repository
python main.py init

# 2. Create and add some files
echo "Hello World" > hello.txt
echo "def main(): pass" > app.py
python main.py add hello.txt app.py

# 3. Create initial commit
python main.py commit -m "Initial commit" -a "Alice"

# 4. Create a feature branch
python main.py branch feature

# 5. Switch to feature branch
python main.py checkout feature

# 6. Make changes
echo "print('Feature')" >> app.py
python main.py add app.py
python main.py commit -m "Add feature" -a "Alice"

# 7. Switch back to main
python main.py checkout main

# 8. Merge feature branch
python main.py merge feature

# 9. View history
python main.py log

# 10. View commit graph
python main.py graph -o my-commits.png

# 11. Check audit trail
python main.py audit
```

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────┐
│           CLI Handler (cli.py)          │
│  Command-line interface and parsing     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│       Repository (repository.py)        │
│  Core VCS logic and data structures:    │
│  • Hash maps for commits                │
│  • Adjacency list for DAG               │
│  • Stack for rollback                   │
│  • Branch management                    │
└───┬──────────────────────┬──────────────┘
    │                      │
    ▼                      ▼
┌─────────────┐    ┌──────────────────┐
│   Commit    │    │   Merkle Tree    │
│ (commit.py) │    │ (merkle_tree.py) │
│             │    │                  │
│ • SHA-256   │    │ • Binary tree    │
│ • Metadata  │    │ • File hashing   │
│ • Parents   │    │ • Integrity      │
└─────────────┘    └──────────────────┘
```

### Data Flow

1. **Add Operation**: File → Staging Area (HashMap)
2. **Commit Operation**: Staging Area → Merkle Tree → Commit Object → DAG
3. **Merge Operation**: Find LCA in DAG → Detect Conflicts → Create Merge Commit
4. **Rollback Operation**: Pop from Stack → Update HEAD → Restore Files

### Key Classes

#### `MerkleTree` (merkle_tree.py)
- **Purpose**: File integrity verification
- **Structure**: Binary tree with SHA-256 hashed nodes
- **Operations**: Build tree O(n), verify proof O(log n)

#### `Commit` (commit.py)
- **Purpose**: Represent a snapshot in time
- **Contains**: Files, metadata, Merkle root, parent refs
- **Hash**: Computed from all commit data using SHA-256

#### `Repository` (repository.py)
- **Purpose**: Manage entire VCS state
- **Data Structures**:
  - `commits`: HashMap (hash → Commit)
  - `commit_graph`: Adjacency List (hash → children)
  - `rollback_stack`: Stack for undo
  - `branches`: HashMap (name → hash)

#### `CLIHandler` (cli.py)
- **Purpose**: User interface
- **Pattern**: Command pattern with method dispatch

## 🔐 Security & Integrity

### SHA-256 Hashing
Every commit has a unique SHA-256 hash computed from:
- Parent commit hashes
- Merkle root hash
- Message, author, timestamp

Any change to history or files will change the hash, making tampering detectable.

### Merkle Tree Verification
Each commit includes a Merkle tree of all files:
```
         Root Hash
        /         \
    Hash1         Hash2
    /    \        /    \
File1  File2  File3  File4
```

**Benefits**:
- Detect file tampering: O(1) root comparison
- Prove file inclusion: O(log n) verification
- Efficient integrity checking

### Commit Integrity Check
```python
# Verify commit hasn't been tampered with
commit.verify_integrity()  # Returns True/False
```

## 📊 Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Add file | O(m) | O(m) |
| Create commit | O(n) | O(n) |
| Retrieve commit | O(1) | O(1) |
| Switch branch | O(n) | O(n) |
| Merge branches | O(V + E + n) | O(n) |
| Rollback | O(k + n) | O(1) |
| Find LCA | O(V + E) | O(V) |
| Verify Merkle proof | O(log n) | O(log n) |

Where:
- m = file size
- n = number of files
- V = number of commits (vertices)
- E = number of parent-child relationships (edges)
- k = rollback steps

## 🧪 Testing

### Manual Testing

Create test files and run commands:
```bash
# Create test files
echo "Test 1" > test1.txt
echo "Test 2" > test2.txt

# Test basic workflow
python main.py init
python main.py add test1.txt test2.txt
python main.py commit -m "Test commit"
python main.py log
```

### Test Scenarios

1. **Basic Operations**: init, add, commit, status, log
2. **Branching**: create branch, switch, merge without conflicts
3. **Merge Conflicts**: modify same file in two branches, attempt merge
4. **Rollback**: create multiple commits, rollback, verify state
5. **Integrity**: modify commit file manually, verify integrity fails

## 🔮 Future Enhancements

### Planned Features
1. **Distributed Synchronization**
   - Remote repository support
   - Push/pull operations
   - Conflict resolution

2. **User Authentication**
   - GPG signature verification
   - User credentials
   - Access control

3. **Performance Optimization**
   - Incremental Merkle tree updates
   - Commit compression
   - Index caching

4. **Advanced Features**
   - Cherry-pick commits
   - Rebase operations
   - Stash functionality
   - Tag support
   - Blame/annotate

5. **UI Improvements**
   - Interactive mode
   - Colored output
   - Progress bars
   - Web interface

## 🐛 Troubleshooting

### Repository Not Initialized
```
Error: Not a VCS repository
```
**Solution**: Run `python main.py init`

### Merge Conflicts
```
Merge conflict detected in X file(s)
```
**Solution**: Resolve conflicts manually, then commit

### Visualization Not Working
```
Visualization dependencies not available
```
**Solution**: Install dependencies:
```bash
pip install networkx matplotlib
```

### Permission Issues
**Windows**: Run PowerShell as Administrator if file access issues occur

**Linux/Mac**: Ensure execute permissions:
```bash
chmod +x main.py
```

## 📚 Algorithm Documentation

### Merkle Tree Construction
```
Algorithm: Build Merkle Tree
Input: List of (filename, content) tuples
Output: Binary tree with root hash

1. Create leaf nodes for each file
   - Hash: SHA-256(filename:content)
2. While nodes > 1:
   a. Pair consecutive nodes
   b. Create parent: Hash(left.hash + right.hash)
   c. If odd count, duplicate last node
3. Return root node

Time: O(n), Space: O(n)
```

### Lowest Common Ancestor (LCA)
```
Algorithm: Find LCA in DAG
Input: Two commit hashes
Output: Common ancestor hash

1. Traverse ancestors of commit1, mark visited
2. Traverse ancestors of commit2
3. First visited node found is LCA

Time: O(V + E), Space: O(V)
```

### Merge Conflict Detection
```
Algorithm: Detect Conflicts
Input: Two commits, common ancestor
Output: List of conflicting files

For each file in both commits:
  If modified in both branches:
    If different from ancestor in both:
      Add to conflicts
  If deleted in one, modified in other:
    Add to conflicts

Time: O(n), Space: O(n)
```

## 📄 License

This project is provided as an educational implementation of version control concepts.
Free to use for learning purposes.

## 👥 Contributing

This is an educational project. Suggestions for improvements:
1. Enhanced error handling
2. Additional test cases
3. Performance optimizations
4. Documentation improvements

## 🙏 Acknowledgments

Inspired by:
- Git version control system
- Merkle tree data structure (Bitcoin)
- Graph algorithms (Cormen et al.)
- Object-oriented design patterns

## 📧 Contact

For questions or feedback about this implementation, please refer to the code documentation and inline comments.

---

**Built with**: Python 3, Data Structures, Algorithms, and Cryptography

**Key Concepts**: DAG, Merkle Trees, SHA-256, Hash Maps, Adjacency Lists, Stacks, Binary Trees
