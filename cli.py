"""
Command-Line Interface (CLI) Handler for Version Control System
==============================================================

Implements a user-friendly CLI for interacting with the VCS.

Commands:
- init: Initialize repository
- add <file>: Stage file for commit
- commit -m "message": Create commit
- status: Show repository status
- log: Show commit history
- rollback [steps]: Undo commits
- branch <name>: Create branch
- checkout <branch>: Switch branch
- branches: List all branches
- merge <branch>: Merge branch
- graph: Visualize commit DAG
- audit: Show audit log
- help: Display help message

Design Pattern: Command Pattern
Each command is a method that executes a specific operation.
"""

import sys
import argparse
from typing import List
from repository import Repository
from pathlib import Path


class CLIHandler:
    """
    Command-Line Interface handler for VCS operations.
    
    Provides user-friendly commands that map to Repository operations.
    Uses argparse for command parsing and validation.
    """
    
    def __init__(self):
        """Initialize CLI handler."""
        self.repo: Repository = None
        self.repo_path = Path.cwd()
    
    def run(self, args: List[str]):
        """
        Main entry point for CLI.
        
        Args:
            args: Command-line arguments (excluding program name)
        """
        if not args:
            self.print_help()
            return
        
        command = args[0]
        command_args = args[1:]
        
        # Commands that don't require initialized repo
        if command == 'init':
            self.cmd_init(command_args)
            return
        elif command == 'help':
            self.print_help()
            return
        
        # Load repository for all other commands
        self._load_repository()
        
        # Execute command
        commands = {
            'add': self.cmd_add,
            'commit': self.cmd_commit,
            'status': self.cmd_status,
            'log': self.cmd_log,
            'rollback': self.cmd_rollback,
            'branch': self.cmd_branch,
            'checkout': self.cmd_checkout,
            'branches': self.cmd_branches,
            'merge': self.cmd_merge,
            'graph': self.cmd_graph,
            'audit': self.cmd_audit,
        }
        
        if command in commands:
            try:
                commands[command](command_args)
            except Exception as e:
                print(f"Error executing command '{command}': {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' to see available commands")
    
    def _load_repository(self):
        """Load repository or exit if not initialized."""
        vcs_dir = self.repo_path / '.vcs'
        if not vcs_dir.exists():
            print("Error: Not a VCS repository")
            print("Run 'vcs init' to initialize")
            sys.exit(1)
        
        self.repo = Repository.load(str(self.repo_path))
    
    def cmd_init(self, args: List[str]):
        """
        Initialize a new repository.
        
        Usage: vcs init
        """
        self.repo = Repository(str(self.repo_path))
        result = self.repo.init()
        print(result)
    
    def cmd_add(self, args: List[str]):
        """
        Add file(s) to staging area.
        
        Usage: vcs add <file> [<file2> ...]
        """
        if not args:
            print("Usage: vcs add <file> [<file2> ...]")
            return
        
        for filepath in args:
            result = self.repo.add(filepath)
            print(result)
    
    def cmd_commit(self, args: List[str]):
        """
        Create a new commit.
        
        Usage: vcs commit -m "message" [-a "author"]
        """
        parser = argparse.ArgumentParser(prog='vcs commit')
        parser.add_argument('-m', '--message', required=True, help='Commit message')
        parser.add_argument('-a', '--author', default='default', help='Commit author')
        
        try:
            parsed = parser.parse_args(args)
            result = self.repo.commit(parsed.message, parsed.author)
            print(result)
        except SystemExit:
            # argparse calls sys.exit on error, catch it
            pass
    
    def cmd_status(self, args: List[str]):
        """
        Show repository status.
        
        Usage: vcs status
        """
        result = self.repo.status()
        print(result)
    
    def cmd_log(self, args: List[str]):
        """
        Display commit history.
        
        Usage: vcs log [-n <number>]
        """
        parser = argparse.ArgumentParser(prog='vcs log')
        parser.add_argument('-n', '--number', type=int, help='Number of commits to show')
        
        try:
            parsed = parser.parse_args(args)
            result = self.repo.log(parsed.number)
            print(result)
        except SystemExit:
            pass
    
    def cmd_rollback(self, args: List[str]):
        """
        Rollback to previous commit(s).
        
        Usage: vcs rollback [steps]
        Default: 1 step
        """
        steps = 1
        if args:
            try:
                steps = int(args[0])
            except ValueError:
                print("Error: steps must be a number")
                return
        
        result = self.repo.rollback(steps)
        print(result)
    
    def cmd_branch(self, args: List[str]):
        """
        Create a new branch.
        
        Usage: vcs branch <name>
        """
        if not args:
            print("Usage: vcs branch <name>")
            return
        
        branch_name = args[0]
        result = self.repo.create_branch(branch_name)
        print(result)
    
    def cmd_checkout(self, args: List[str]):
        """
        Switch to a different branch.
        
        Usage: vcs checkout <branch>
        """
        if not args:
            print("Usage: vcs checkout <branch>")
            return
        
        branch_name = args[0]
        result = self.repo.switch_branch(branch_name)
        print(result)
    
    def cmd_branches(self, args: List[str]):
        """
        List all branches.
        
        Usage: vcs branches
        """
        result = self.repo.list_branches()
        print(result)
    
    def cmd_merge(self, args: List[str]):
        """
        Merge another branch into current branch.
        
        Usage: vcs merge <branch>
        """
        if not args:
            print("Usage: vcs merge <branch>")
            return
        
        branch_name = args[0]
        result = self.repo.merge(branch_name)
        print(result)
    
    def cmd_graph(self, args: List[str]):
        """
        Visualize commit graph.
        
        Usage: vcs graph [-o <output_file>]
        """
        parser = argparse.ArgumentParser(prog='vcs graph')
        parser.add_argument('-o', '--output', help='Output file (default: graph.png)')
        parser.add_argument('--format', choices=['png', 'dot'], default='png',
                          help='Output format')
        
        try:
            parsed = parser.parse_args(args)
            
            if parsed.format == 'dot':
                # Output DOT format
                dot_content = self.repo.get_commit_graph_dot()
                output_file = parsed.output or 'graph.dot'
                with open(output_file, 'w') as f:
                    f.write(dot_content)
                print(f"Commit graph saved to {output_file}")
                print("Use Graphviz to render: dot -Tpng graph.dot -o graph.png")
            else:
                # Try to generate PNG using visualization module
                try:
                    from visualization import visualize_commit_graph
                    output_file = parsed.output or 'graph.png'
                    visualize_commit_graph(self.repo, output_file)
                    print(f"Commit graph saved to {output_file}")
                except ImportError:
                    print("Visualization module not available.")
                    print("Install dependencies: pip install networkx matplotlib")
                    print("Or use --format dot to export DOT format")
        except SystemExit:
            pass
    
    def cmd_audit(self, args: List[str]):
        """
        Show audit log.
        
        Usage: vcs audit
        """
        result = self.repo.get_audit_log()
        print(result)
    
    def print_help(self):
        """Print help message with all commands."""
        help_text = """
VCS - Version Control System with Secure Commit Tracking
========================================================

Usage: vcs <command> [arguments]

Commands:

  Repository Management:
    init                     Initialize a new repository
    status                   Show repository status

  File Operations:
    add <file> [...]        Add file(s) to staging area
    commit -m "msg"         Create new commit with message
                            Optional: -a "author"

  History & Navigation:
    log [-n <num>]          Show commit history
                            Optional: limit number of commits
    rollback [steps]        Rollback to previous commit(s)
                            Default: 1 step

  Branch Operations:
    branch <name>           Create new branch
    checkout <branch>       Switch to branch
    branches                List all branches
    merge <branch>          Merge branch into current branch

  Visualization & Audit:
    graph [-o file]         Visualize commit DAG
                            --format: png (default) or dot
    audit                   Show audit log of all actions

  Help:
    help                    Show this help message

Examples:

  # Initialize repository
  vcs init

  # Add and commit files
  vcs add file1.txt file2.py
  vcs commit -m "Initial commit" -a "John Doe"

  # Create and switch branches
  vcs branch feature
  vcs checkout feature

  # Merge branches
  vcs checkout main
  vcs merge feature

  # View history and rollback
  vcs log -n 5
  vcs rollback 2

  # Visualize commit graph
  vcs graph -o commits.png

Features:
  • Directed Acyclic Graph (DAG) for commit history
  • SHA-256 cryptographic hashing for commit integrity
  • Merkle Tree for file integrity verification
  • Efficient data structures (hash maps, adjacency lists, stacks)
  • Branch management with merge conflict detection
  • Rollback using stack-based undo
  • Full audit trail of all operations
  • Optional commit graph visualization

Data Structures:
  • Hash Map: O(1) commit retrieval
  • Adjacency List: DAG representation
  • Stack: Rollback operations
  • Merkle Tree: File integrity verification
"""
        print(help_text)


def main():
    """Main entry point for CLI."""
    cli = CLIHandler()
    cli.run(sys.argv[1:])


if __name__ == '__main__':
    main()
