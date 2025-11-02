# VCS Quick Reference Guide

## Command Cheat Sheet

### Repository Setup
```bash
python main.py init                    # Initialize new repository
```

### Basic Workflow
```bash
python main.py add file.txt            # Stage single file
python main.py add *.py                # Stage multiple files
python main.py commit -m "message"     # Commit with message
python main.py commit -m "msg" -a "Author"  # Commit with author
python main.py status                  # Check repository status
python main.py log                     # View commit history
python main.py log -n 10               # View last 10 commits
```

### Branching
```bash
python main.py branch feature          # Create new branch
python main.py branches                # List all branches
python main.py checkout feature        # Switch to branch
python main.py merge feature           # Merge branch into current
```

### History & Undo
```bash
python main.py rollback                # Undo last commit
python main.py rollback 3              # Undo last 3 commits
python main.py audit                   # View audit log
```

### Visualization
```bash
python main.py graph                   # Generate graph.png
python main.py graph -o custom.png     # Custom output file
python main.py graph --format dot      # Export DOT format
```

### Help
```bash
python main.py help                    # Show full help
```

---

## Common Workflows

### Start New Project
```bash
# 1. Initialize
python main.py init

# 2. Create files
echo "content" > file1.txt

# 3. Stage and commit
python main.py add file1.txt
python main.py commit -m "Initial commit"
```

### Feature Branch Workflow
```bash
# 1. Create feature branch
python main.py branch new-feature

# 2. Switch to it
python main.py checkout new-feature

# 3. Make changes and commit
python main.py add changed-files
python main.py commit -m "Implement feature"

# 4. Switch back to main
python main.py checkout main

# 5. Merge feature
python main.py merge new-feature
```

### Fix Mistakes
```bash
# Undo last commit
python main.py rollback

# Undo multiple commits
python main.py rollback 3
```

---

## File Structure

```
your-project/
├── .vcs/                    # VCS internal directory
│   ├── commits/            # Serialized commits
│   ├── objects/            # File storage
│   ├── refs/               # Branch references
│   └── state.json          # Repository state
│
├── main.py                 # Entry point
├── cli.py                  # CLI handler
├── repository.py           # Core logic
├── commit.py               # Commit class
├── merkle_tree.py          # Merkle tree
├── visualization.py        # Graph rendering
├── demo.py                 # Demo script
└── README.md               # Documentation
```

---

## Data Structures at a Glance

| Structure | Usage | Time Complexity |
|-----------|-------|-----------------|
| Hash Map | Commits, branches, staging | O(1) lookup |
| Adjacency List | DAG (commit graph) | O(1) edge access |
| Stack | Rollback history | O(1) push/pop |
| Merkle Tree | File integrity | O(log n) verify |

---

## Security Features

### SHA-256 Hashing
- Every commit has unique hash
- Tamper-proof: any change → new hash
- Collision-resistant

### Merkle Tree
- Root hash in each commit
- Detects file tampering
- Logarithmic verification

### Integrity Check
```python
# In code:
commit.verify_integrity()  # Returns True/False
```

---

## Troubleshooting

### "Not a VCS repository"
**Problem**: Trying to run commands in non-initialized directory  
**Solution**: Run `python main.py init`

### "Merge conflict detected"
**Problem**: Same file modified in both branches  
**Solution**: Resolve manually, then commit

### Visualization not working
**Problem**: Dependencies missing  
**Solution**: `pip install networkx matplotlib`

### Can't switch branch
**Problem**: Staged changes  
**Solution**: Commit or clear staging first

---

## Performance Tips

### For Large Projects
- Commit frequently (smaller changesets)
- Use specific file paths when adding
- Limit log output: `log -n 20`

### For Visualization
- Large graphs take time to render
- Use DOT format for huge repos
- Consider limiting branches

---

## Key Concepts

### DAG (Directed Acyclic Graph)
- No cycles: can't be your own ancestor
- Directed: clear parent-child relationships
- Enables branching and merging

### Merkle Root
- Single hash representing all files
- Root of binary tree of file hashes
- Changes if ANY file changes

### Commit Hash
- Computed from: parents + merkle_root + metadata
- Uniquely identifies commit
- Forms chain of trust

### Staging Area
- Intermediate step before commit
- Select which changes to include
- Clear after each commit

---

## Python API Usage

### Use as Library
```python
from repository import Repository

# Initialize
repo = Repository("./my-project")
repo.init()

# Stage and commit
repo.add("file.txt")
repo.commit("My commit", author="Me")

# Branching
repo.create_branch("feature")
repo.switch_branch("feature")
repo.merge("main")

# History
print(repo.log())
```

### Access Commit Data
```python
# Get commit
commit = repo.commits[commit_hash]

# Check integrity
is_valid = commit.verify_integrity()

# Get files
files = commit.get_all_files()

# Get Merkle root
root = commit.merkle_root
```

---

## Advanced Usage

### Export Commit Graph
```python
# Generate DOT format
dot_content = repo.get_commit_graph_dot()
with open('graph.dot', 'w') as f:
    f.write(dot_content)
```

### Audit Trail
```python
# Access audit log
log = repo.get_audit_log()
print(log)
```

### Check Merkle Proof
```python
# Generate proof for file
proof = commit.merkle_tree.get_proof("file.txt")

# Verify proof
is_valid = merkle_tree.verify_proof(
    "file.txt", 
    content, 
    proof, 
    commit.merkle_root
)
```

---

## Testing Commands

### Quick Test
```bash
# Run demo script
python demo.py
```

### Manual Test
```bash
# Create test directory
mkdir test-vcs
cd test-vcs

# Initialize
python ../main.py init

# Create and commit
echo "test" > test.txt
python ../main.py add test.txt
python ../main.py commit -m "Test"

# Verify
python ../main.py log
```

---

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Repository already initialized" | .vcs exists | Delete .vcs or use existing repo |
| "Nothing to commit" | Empty staging | Add files first |
| "Cannot switch branch" | Staged changes | Commit or clear staging |
| "Branch already exists" | Name conflict | Use different name |
| "Cannot rollback" | No history | Need commits to rollback |

---

## Best Practices

### Commit Messages
✓ Clear and descriptive  
✓ Present tense: "Add feature" not "Added feature"  
✓ Reference what changed  
✗ Avoid: "fix", "update", "changes"

### Branching Strategy
- `main`: Stable code
- `feature-*`: New features
- `bugfix-*`: Bug fixes
- Merge back when complete

### File Organization
- Keep related files together
- Don't commit generated files
- Commit source, not builds

---

## Keyboard Shortcuts (for future GUI)

Currently CLI-only. Future GUI could support:
- Ctrl+C: Commit
- Ctrl+B: Create branch
- Ctrl+M: Merge
- Ctrl+Z: Rollback

---

## Resources

### Documentation Files
- `README.md`: User guide
- `TECHNICAL_DOCS.md`: Technical details
- `demo.py`: Working examples

### Source Code
- `merkle_tree.py`: Merkle tree implementation
- `commit.py`: Commit structure
- `repository.py`: Core logic
- `cli.py`: User interface

### External Resources
- Git documentation (for comparison)
- Merkle trees in Bitcoin
- SHA-256 specification
- Graph algorithms

---

## Version Information

**Current Version**: 1.0  
**Python Required**: 3.7+  
**Optional Deps**: networkx, matplotlib

---

## Getting Help

1. **View help**: `python main.py help`
2. **Check docs**: Read README.md
3. **Run demo**: `python demo.py`
4. **Read source**: Well-commented code

---

## Quick Start (30 seconds)

```bash
# Setup
python main.py init

# Make changes
echo "Hello" > hello.txt

# Commit
python main.py add hello.txt
python main.py commit -m "First commit"

# Done!
python main.py log
```

---

**Happy Version Controlling!** 🚀
