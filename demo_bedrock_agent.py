#!/usr/bin/env python3
"""
Demo script to show AWS Bedrock Agent functionality
This simulates the agent working with mocked AWS Bedrock responses
"""

import json
import sys
import os
from unittest.mock import Mock, patch

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bedrock_agent import BedrockAgent, BedrockAgentConfig


def demo_bedrock_agent():
    """Demonstrate the Bedrock Agent functionality with mocked responses."""
    print("🤖 AWS Bedrock Agent Demonstration")
    print("=" * 50)
    
    # Setup configuration
    config = BedrockAgentConfig()
    config.index_file = './document_index.json'
    
    # Mock the AWS Bedrock client
    with patch('bedrock_agent.boto3.client') as mock_boto3:
        mock_client = Mock()
        mock_boto3.return_value = mock_client
        
        # Mock successful Bedrock responses
        def mock_invoke_model(**kwargs):
            body_str = kwargs.get('body', '{}')
            body = json.loads(body_str)
            
            if 'messages' in body:
                user_message = body['messages'][0]['content']
                
                # Generate contextual responses based on the query
                if 'aws credentials' in user_message.lower():
                    response_text = """Based on the documentation, you can configure AWS credentials in several ways:

1. **AWS CLI Configuration**: Run `aws configure` and provide your Access Key ID, Secret Access Key, and default region.

2. **Environment Variables**: Set the following environment variables:
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_DEFAULT_REGION

3. **IAM Roles**: For applications running on AWS infrastructure (EC2, Lambda), use IAM roles instead of hardcoded credentials.

4. **Credentials File**: Store credentials in ~/.aws/credentials file with the format:
   ```
   [default]
   aws_access_key_id = your_access_key
   aws_secret_access_key = your_secret_key
   ```

The documentation emphasizes using IAM roles when possible and never committing credentials to source code."""

                elif 'document' in user_message.lower() and 'index' in user_message.lower():
                    response_text = """The Bedrock Agent supports indexing various document types including:

- **Text files** (.txt): Plain text documents
- **Markdown** (.md): Formatted documentation files  
- **Python source** (.py): Source code with comments
- **JSON files** (.json): Configuration and data files
- **YAML files** (.yaml, .yml): Configuration files

The indexing process:
1. Scans the specified directory recursively
2. Extracts text content from supported file types
3. Creates searchable metadata for each document
4. Stores everything in a persistent JSON index

You can re-index documents when they change, and the system will update the existing entries."""

                elif 'summarize' in user_message.lower():
                    response_text = """This document provides comprehensive API reference documentation for the AWS Bedrock Agent. Key highlights include:

**Main Components:**
- BedrockAgent class for core functionality
- DocumentIndex for local storage and search
- BedrockAgentConfig for configuration management

**Key Features:**
- Document indexing with metadata extraction
- Natural language question answering
- Full-text search capabilities  
- Document summarization using AI
- Multiple file format support

**CLI Commands:**
The agent provides six main commands: index, query, search, list, summarize, and status, each designed for specific document management tasks.

The documentation includes detailed examples, error handling guidance, and best practices for using the agent effectively."""

                else:
                    response_text = """I can help you with questions about the AWS Bedrock Agent documentation. The agent provides features like document indexing, intelligent search, Q&A capabilities, and document summarization using AWS Bedrock foundation models.

Some things you can ask about:
- How to configure AWS credentials
- Document indexing and supported file types
- Using the CLI commands
- API reference and examples
- Troubleshooting common issues

Please feel free to ask specific questions about any of these topics!"""
                
                mock_response = {
                    'body': Mock()
                }
                mock_response['body'].read.return_value = json.dumps({
                    'content': [{'text': response_text}]
                }).encode()
                
                return mock_response
            
            return {'body': Mock()}
        
        mock_client.invoke_model.side_effect = mock_invoke_model
        
        # Create agent
        agent = BedrockAgent(config)
        
        print(f"\n📚 Indexed Documents: {len(agent.document_index.documents)}")
        
        # Demo questions
        questions = [
            "How do I configure AWS credentials?",
            "What document types can be indexed?",
            "Can you summarize the API documentation?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n🔍 Question {i}: {question}")
            print("-" * 40)
            
            result = agent.answer_question(question)
            print(f"💡 Answer ({result['confidence']} confidence):")
            print(result['answer'])
            
            if result['sources']:
                print(f"\n📖 Sources:")
                for source in result['sources']:
                    print(f"  • {source}")
        
        print(f"\n🔎 Search Demo: 'Bedrock model'")
        print("-" * 40)
        search_results = agent.document_index.search_documents("Bedrock model")
        if search_results:
            for i, result in enumerate(search_results[:2], 1):
                print(f"{i}. {result['file_path']} (relevance: {result['score']})")
                print(f"   {result['content'][:150]}...")
        
        print(f"\n✅ Demo completed successfully!")
        print(f"\nTo use with real AWS credentials:")
        print(f"1. Configure AWS credentials: aws configure")
        print(f"2. Enable Bedrock model access in AWS console")
        print(f"3. Run: python3 bedrock_agent.py query \"your question\"")


if __name__ == "__main__":
    demo_bedrock_agent()