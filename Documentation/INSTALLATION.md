# Installation and Setup Guide

## 🚀 Quick Start (2 minutes)

### Step 1: Verify Python Installation
```bash
python --version
```
**Required**: Python 3.7 or higher

### Step 2: Navigate to Project Directory
```bash
cd "c:\Users\anees\Desktop\SEM 3\DSA\Version Control System"
```

### Step 3: Test the Installation
```bash
python main.py help
```

✅ If you see the help message, you're ready to go!

---

## 📦 Optional Dependencies

### For Visualization Features

Install networkx and matplotlib for graph rendering:

```powershell
pip install networkx matplotlib
```

Or use the requirements file:

```powershell
pip install -r requirements.txt
```

**Note**: The VCS works perfectly without these - they're only needed for graph visualization.

---

## 🧪 Verify Installation

### Run the Test Suite
```bash
python test_vcs.py
```

Expected output:
```
==================================================================
  VCS Test Suite
==================================================================

Running 43 tests...

✓ Merkle Tree Empty
✓ Merkle Tree Single File
✓ Merkle Tree Multiple Files
...
✓ All tests passed!
```

### Run the Demo
```bash
python demo.py
```

This will create a `vcs_demo` directory and demonstrate all features.

---

## 📖 First Usage

### Initialize Your First Repository

1. **Create a project directory**:
```powershell
mkdir my-vcs-project
cd my-vcs-project
```

2. **Initialize VCS**:
```powershell
python ..\main.py init
```

3. **Create a file**:
```powershell
echo "Hello, VCS!" > hello.txt
```

4. **Add and commit**:
```powershell
python ..\main.py add hello.txt
python ..\main.py commit -m "Initial commit"
```

5. **View history**:
```powershell
python ..\main.py log
```

🎉 **Congratulations!** You've made your first commit!

---

## 🛠️ System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.7+
- **Disk Space**: 10 MB
- **RAM**: 256 MB

### Recommended
- **Python**: 3.9+
- **Disk Space**: 50 MB (for large repositories)
- **RAM**: 512 MB

### Optional (for visualization)
- **networkx**: 2.8+
- **matplotlib**: 3.5+

---

## 📂 Project Structure

After installation, you should have:

```
Project/
├── main.py                    # ⭐ Entry point - run this
├── cli.py                     # Command-line interface
├── repository.py              # Core VCS logic
├── commit.py                  # Commit implementation
├── merkle_tree.py             # Merkle tree for integrity
├── visualization.py           # Graph rendering
├── demo.py                    # 🎬 Demo script
├── test_vcs.py                # 🧪 Test suite
├── requirements.txt           # Optional dependencies
├── README.md                  # 📖 User guide
├── TECHNICAL_DOCS.md          # 🔧 Technical details
├── QUICK_REFERENCE.md         # ⚡ Quick reference
└── PROJECT_SUMMARY.md         # 📊 Project overview
```

---

## 🐛 Troubleshooting

### Issue: "python: command not found"

**Solution**: Use `py` instead:
```powershell
py main.py help
```

### Issue: "No module named 'xyz'"

**Solution**: The core VCS doesn't need external modules. If you see this:
1. Check you're running the right file: `python main.py`
2. If it's about networkx/matplotlib, they're optional - visualization won't work

### Issue: "Permission denied" when creating .vcs

**Solution**: 
- Windows: Run PowerShell as Administrator
- Linux/Mac: Check directory permissions

### Issue: Demo fails

**Solution**:
1. Make sure you're in the Project directory
2. Run: `python demo.py`
3. Check you have write permissions

---

## 💻 Platform-Specific Notes

### Windows (PowerShell)
```powershell
# Run commands
python main.py init

# Create files
New-Item -ItemType File test.txt
Set-Content test.txt "content"

# Or use echo
echo "content" > test.txt
```

### Windows (Command Prompt)
```cmd
python main.py init
echo content > test.txt
```

### Linux / macOS (Bash)
```bash
python3 main.py init
echo "content" > test.txt
```

---

## 📚 Next Steps

### 1. Read the Documentation
- **README.md**: User guide with examples
- **QUICK_REFERENCE.md**: Command cheat sheet
- **TECHNICAL_DOCS.md**: Deep dive into internals

### 2. Try the Demo
```bash
python demo.py
```

### 3. Run the Tests
```bash
python test_vcs.py
```

### 4. Create Your First Repository
Follow the "First Usage" section above.

### 5. Explore Advanced Features
- Create branches
- Merge changes
- Visualize commit graph
- Check audit log

---

## 🔧 Advanced Setup

### Create an Alias (Optional)

#### Windows (PowerShell Profile)
```powershell
# Edit profile
notepad $PROFILE

# Add this line:
function vcs { python "c:\Users\anees\Desktop\SEM 3\DSA\Project\main.py" $args }

# Reload
. $PROFILE

# Now use:
vcs init
vcs add file.txt
```

#### Linux/macOS (Bash)
```bash
# Edit .bashrc or .zshrc
nano ~/.bashrc

# Add this line:
alias vcs='python3 /path/to/Project/main.py'

# Reload
source ~/.bashrc

# Now use:
vcs init
vcs add file.txt
```

---

## 🎓 Learning Path

### Beginner (Day 1)
1. ✅ Install and verify
2. ✅ Run demo
3. ✅ Read README.md
4. ✅ Create first repository
5. ✅ Make commits

### Intermediate (Day 2)
1. ✅ Create branches
2. ✅ Switch branches
3. ✅ Merge without conflicts
4. ✅ Use rollback
5. ✅ View audit log

### Advanced (Day 3)
1. ✅ Create merge conflicts
2. ✅ Understand conflict detection
3. ✅ Read TECHNICAL_DOCS.md
4. ✅ Explore Merkle trees
5. ✅ Visualize commit graph

### Expert (Day 4+)
1. ✅ Study the source code
2. ✅ Understand algorithms
3. ✅ Run tests
4. ✅ Modify/extend the system
5. ✅ Compare with Git internals

---

## 📦 Installation Checklist

Before starting, verify:

- [ ] Python 3.7+ installed
- [ ] Project files downloaded
- [ ] Can run: `python main.py help`
- [ ] Tests pass: `python test_vcs.py`
- [ ] Demo runs: `python demo.py`
- [ ] (Optional) Visualization deps installed

---

## 🎯 Quick Commands Reference

### Most Used Commands
```bash
python main.py init              # Initialize repo
python main.py add <file>        # Stage file
python main.py commit -m "msg"   # Commit changes
python main.py status            # Check status
python main.py log               # View history
python main.py branch <name>     # Create branch
python main.py checkout <name>   # Switch branch
python main.py merge <name>      # Merge branch
python main.py rollback          # Undo commit
```

### Full command list
```bash
python main.py help
```

---

## 🆘 Getting Help

### 1. Built-in Help
```bash
python main.py help
```

### 2. Documentation Files
- README.md - User guide
- QUICK_REFERENCE.md - Command reference
- TECHNICAL_DOCS.md - Technical details

### 3. Demo Script
```bash
python demo.py
```
Watch it in action!

### 4. Source Code
All code is well-commented. Read the files to understand internals.

---

## ✅ Installation Complete!

You're now ready to use the VCS system. Try this quick test:

```bash
# Create test directory
mkdir vcs-test
cd vcs-test

# Initialize
python ..\main.py init

# Create file
echo "test" > test.txt

# Commit
python ..\main.py add test.txt
python ..\main.py commit -m "Test commit"

# Success!
python ..\main.py log
```

**Happy Version Controlling!** 🚀

---

## 📞 Support

For issues or questions:
1. Check QUICK_REFERENCE.md for common solutions
2. Review README.md troubleshooting section
3. Examine the source code (well-documented)
4. Run the test suite to verify installation

---

**Installation Guide Version**: 1.0  
**Last Updated**: 2025-01-22  
**Compatible With**: Python 3.7+, All platforms
