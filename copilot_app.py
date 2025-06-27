#!/usr/bin/env python3
"""
Copilot Application - A simple Python program for demonstration purposes.

This application provides basic functionality including:
- Text processing capabilities
- File operations
- Command-line interface
- Logging and error handling
"""

import argparse
import logging
import sys
import os
from typing import Optional, List


class CopilotApp:
    """Main application class for the Copilot program."""
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize the application with logging configuration."""
        self.setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Copilot Application initialized")
    
    def setup_logging(self, log_level: str) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def process_text(self, text: str, operation: str = "upper") -> str:
        """Process text with various operations."""
        self.logger.debug(f"Processing text with operation: {operation}")
        
        operations = {
            "upper": lambda: text.upper(),
            "lower": lambda: text.lower(),
            "title": lambda: text.title(),
            "reverse": lambda: text[::-1],
            "word_count": lambda: str(len(text.split()))
        }
        
        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}. Available: {list(operations.keys())}")
        
        result = operations[operation]()
        self.logger.info(f"Text processed successfully with operation: {operation}")
        return result
    
    def read_file(self, filepath: str) -> str:
        """Read content from a file."""
        self.logger.debug(f"Reading file: {filepath}")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            self.logger.info(f"Successfully read file: {filepath}")
            return content
        except Exception as e:
            self.logger.error(f"Error reading file {filepath}: {e}")
            raise
    
    def write_file(self, filepath: str, content: str) -> None:
        """Write content to a file."""
        self.logger.debug(f"Writing to file: {filepath}")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            self.logger.info(f"Successfully wrote to file: {filepath}")
        except Exception as e:
            self.logger.error(f"Error writing to file {filepath}: {e}")
            raise
    
    def get_system_info(self) -> dict:
        """Get basic system information."""
        import platform
        
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "current_directory": os.getcwd()
        }
        
        self.logger.info("System information retrieved")
        return info


def main():
    """Main function to run the application."""
    parser = argparse.ArgumentParser(description="Copilot Application - A simple Python program")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Set the logging level")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Text processing command
    text_parser = subparsers.add_parser("text", help="Process text")
    text_parser.add_argument("input_text", help="Text to process")
    text_parser.add_argument("--operation", default="upper", 
                           choices=["upper", "lower", "title", "reverse", "word_count"],
                           help="Operation to perform on text")
    
    # File operations command
    file_parser = subparsers.add_parser("file", help="File operations")
    file_parser.add_argument("--read", help="Read from file")
    file_parser.add_argument("--write", nargs=2, metavar=("FILE", "CONTENT"),
                           help="Write content to file")
    
    # System info command
    subparsers.add_parser("info", help="Show system information")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        app = CopilotApp(log_level=args.log_level)
        
        if args.command == "text":
            result = app.process_text(args.input_text, args.operation)
            print(f"Result: {result}")
        
        elif args.command == "file":
            if args.read:
                content = app.read_file(args.read)
                print(f"File content:\n{content}")
            elif args.write:
                app.write_file(args.write[0], args.write[1])
                print(f"Content written to {args.write[0]}")
            else:
                print("Please specify --read or --write operation")
                return 1
        
        elif args.command == "info":
            info = app.get_system_info()
            print("System Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        
        return 0
    
    except Exception as e:
        logging.error(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())