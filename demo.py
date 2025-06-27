#!/usr/bin/env python3
"""
Example usage script for the Copilot Application.

This script demonstrates various features of the copilot_app.py program.
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and print its output."""
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(f"Error: {result.stderr.strip()}")
    return result.returncode == 0

def main():
    """Demonstrate the Copilot Application features."""
    print("=== Copilot Application Demo ===\n")
    
    # Check if the main script exists
    if not os.path.exists("copilot_app.py"):
        print("Error: copilot_app.py not found in current directory")
        return 1
    
    print("1. Text Processing Examples:")
    
    # Text processing examples
    run_command(["python3", "copilot_app.py", "text", "hello world", "--operation", "upper"])
    run_command(["python3", "copilot_app.py", "text", "HELLO WORLD", "--operation", "lower"])
    run_command(["python3", "copilot_app.py", "text", "python programming", "--operation", "title"])
    run_command(["python3", "copilot_app.py", "text", "reverse this text", "--operation", "reverse"])
    run_command(["python3", "copilot_app.py", "text", "count these words here", "--operation", "word_count"])
    
    print("\n2. File Operations Examples:")
    
    # File operations examples
    demo_file = "demo_file.txt"
    demo_content = "This is a demonstration file created by the Copilot Application!"
    
    run_command(["python3", "copilot_app.py", "file", "--write", demo_file, demo_content])
    run_command(["python3", "copilot_app.py", "file", "--read", demo_file])
    
    # Clean up demo file
    if os.path.exists(demo_file):
        os.remove(demo_file)
        print(f"\nCleaned up {demo_file}")
    
    print("\n3. System Information:")
    
    # System info example
    run_command(["python3", "copilot_app.py", "info"])
    
    print("\n4. Help Information:")
    
    # Help example
    run_command(["python3", "copilot_app.py", "--help"])
    
    print("\n=== Demo Complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())