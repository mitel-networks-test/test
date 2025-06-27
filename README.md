# Copilot Application

A simple Python program that provides basic text processing, file operations, and system information capabilities.

## AWS Three-Tier Architecture

This repository also includes a complete **AWS three-tier architecture** implementation with CloudFormation templates, designed for scalable, highly available web applications.

### 🏗️ Architecture Overview

```
Internet → ALB → EC2 Instances → RDS Database
           ↓
       S3 Static Website
```

- **Presentation Tier**: S3 static website hosting
- **Application Tier**: ALB + Auto Scaling Group with EC2 instances
- **Database Tier**: RDS Multi-AZ MySQL database

### 🚀 Quick Start - AWS Infrastructure

```bash
# Deploy development environment
cd aws-infrastructure/scripts
./deploy.sh --environment dev

# Deploy production environment  
./deploy.sh --environment prod
```

### 📁 AWS Infrastructure Files

```
aws-infrastructure/
├── cloudformation/           # CloudFormation templates
│   └── three-tier-architecture.yaml
├── parameters/              # Environment-specific parameters
│   ├── dev-parameters.json
│   └── prod-parameters.json
├── static-website/          # S3 static website content
│   ├── index.html
│   └── error.html
├── application/             # EC2 application code
│   └── app.py
├── scripts/                 # Deployment automation
│   ├── deploy.sh
│   └── cleanup.sh
└── docs/                    # Documentation
    ├── architecture-diagram.md
    └── deployment-guide.md
```

### ✨ Key Features

- **High Availability**: Multi-AZ deployment across 2 availability zones
- **Auto Scaling**: Automatically scales EC2 instances based on demand
- **Load Balancing**: Application Load Balancer distributes traffic
- **Database Redundancy**: RDS Multi-AZ with automatic failover
- **Security**: Proper security groups and network segmentation
- **Infrastructure as Code**: Complete CloudFormation templates
- **Monitoring**: Built-in health checks and monitoring

### 📖 Documentation

- [Complete Architecture Diagram](aws-infrastructure/docs/architecture-diagram.md)
- [Deployment Guide](aws-infrastructure/docs/deployment-guide.md)

---

## Features

- **Text Processing**: Transform text with various operations (uppercase, lowercase, title case, reverse, word count)
- **File Operations**: Read from and write to files with proper error handling
- **System Information**: Display platform and Python environment details
- **Command-line Interface**: Easy-to-use CLI with subcommands
- **Logging**: Configurable logging levels for debugging and monitoring

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mitel-networks-test/test.git
cd test
```

2. Ensure Python 3.6+ is installed:
```bash
python3 --version
```

3. Install dependencies (currently uses only standard library):
```bash
pip install -r requirements.txt
```

## Usage

The application supports several commands:

### Text Processing
```bash
# Convert text to uppercase
python3 copilot_app.py text "hello world" --operation upper

# Count words in text
python3 copilot_app.py text "hello world" --operation word_count

# Reverse text
python3 copilot_app.py text "hello world" --operation reverse

# Convert to title case
python3 copilot_app.py text "hello world" --operation title

# Convert to lowercase
python3 copilot_app.py text "HELLO WORLD" --operation lower
```

### File Operations
```bash
# Write content to a file
python3 copilot_app.py file --write myfile.txt "Hello, World!"

# Read content from a file
python3 copilot_app.py file --read myfile.txt
```

### System Information
```bash
# Display system information
python3 copilot_app.py info
```

### Logging
You can control the logging level:
```bash
# Debug level logging
python3 copilot_app.py --log-level DEBUG text "hello" --operation upper

# Error level logging only
python3 copilot_app.py --log-level ERROR info
```

## Command Reference

### General Options
- `--log-level {DEBUG,INFO,WARNING,ERROR}`: Set the logging level (default: INFO)
- `--help`: Show help message

### Text Command
```bash
python3 copilot_app.py text INPUT_TEXT [--operation OPERATION]
```

**Available Operations:**
- `upper`: Convert to uppercase
- `lower`: Convert to lowercase  
- `title`: Convert to title case
- `reverse`: Reverse the text
- `word_count`: Count words in the text

### File Command
```bash
python3 copilot_app.py file [--read FILE] [--write FILE CONTENT]
```

**Options:**
- `--read FILE`: Read and display content from a file
- `--write FILE CONTENT`: Write content to a file

### Info Command
```bash
python3 copilot_app.py info
```

Displays system information including platform, Python version, architecture, and current directory.

## Examples

```bash
# Process text
./copilot_app.py text "Python is awesome" --operation title
# Output: Python Is Awesome

# File operations
./copilot_app.py file --write greeting.txt "Hello, Copilot!"
./copilot_app.py file --read greeting.txt
# Output: Hello, Copilot!

# System info
./copilot_app.py info
# Output: System information with platform details
```

## Error Handling

The application includes comprehensive error handling:
- File not found errors
- Invalid operation errors
- Logging of all operations and errors
- Graceful exit with appropriate error codes

## Development

The application is structured with a main `CopilotApp` class that encapsulates all functionality. It follows Python best practices with:
- Type hints
- Proper logging
- Error handling
- Command-line argument parsing
- Modular design

## License

This project is part of the test repository and is available for educational and demonstration purposes.
