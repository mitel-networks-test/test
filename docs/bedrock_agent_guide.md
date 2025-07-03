# AWS Bedrock Agent Documentation

## Overview

The AWS Bedrock Agent is an intelligent documentation assistant that leverages AWS Bedrock foundation models to provide advanced search, summarization, and question-answering capabilities for internal documentation repositories.

## Features

### Document Indexing
- Automatically indexes documents from specified directories
- Supports multiple file formats: .txt, .md, .rst, .py, .json, .yaml, .yml
- Creates searchable metadata for each document
- Maintains a persistent document index

### Intelligent Query Processing
- Natural language question answering
- Context-aware responses using relevant documents
- Confidence scoring for answers
- Source attribution for transparency

### Search Capabilities
- Full-text search across all indexed documents
- Relevance scoring based on query match frequency
- Preview snippets for quick document overview

### Document Summarization
- AI-powered document summaries using Bedrock LLMs
- Concise extraction of key information
- Maintains context and important details

## Getting Started

### Prerequisites
- Python 3.8 or higher
- AWS account with Bedrock access
- Appropriate AWS credentials configured

### Installation
1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure AWS credentials and settings:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials and preferences
   ```

### Basic Usage

1. Index your documentation:
   ```bash
   python3 bedrock_agent.py index ./docs
   ```

2. Ask questions about your documents:
   ```bash
   python3 bedrock_agent.py query "How do I configure AWS credentials?"
   ```

3. Search for specific topics:
   ```bash
   python3 bedrock_agent.py search "authentication"
   ```

4. Summarize a document:
   ```bash
   python3 bedrock_agent.py summarize <document_id>
   ```

## Configuration

The agent can be configured through environment variables or a `.env` file:

- `AWS_REGION`: AWS region for Bedrock service (default: us-east-1)
- `BEDROCK_MODEL_ID`: Foundation model to use (default: Claude 3 Sonnet)
- `MAX_TOKENS`: Maximum tokens for responses (default: 1000)
- `TEMPERATURE`: Model temperature for creativity (default: 0.3)
- `DOCS_DIRECTORY`: Default directory for indexing (default: ./docs)
- `INDEX_FILE`: Location of document index file (default: ./document_index.json)

## Best Practices

1. **Document Organization**: Structure your documentation in a logical hierarchy
2. **Regular Indexing**: Re-index documents when they change
3. **Specific Queries**: Ask specific questions for better results
4. **Source Verification**: Always check the provided sources for accuracy
5. **Model Selection**: Choose appropriate models based on your use case

## Troubleshooting

### Common Issues
- **AWS Credentials**: Ensure your AWS credentials have Bedrock permissions
- **Model Access**: Verify that your AWS account has access to the selected Bedrock models
- **File Encoding**: Ensure documents are in UTF-8 encoding
- **Large Documents**: Very large documents may need to be split for better processing

### Error Messages
- "AWS credentials not found": Configure AWS credentials
- "Model not found": Check if the model ID is correct and accessible
- "No relevant documents": Index documents before querying

## API Reference

See the inline documentation in `bedrock_agent.py` for detailed API information.