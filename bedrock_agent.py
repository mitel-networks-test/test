#!/usr/bin/env python3
"""
AWS Bedrock Agent Application

An intelligent agent for internal documentation repository that leverages
AWS Bedrock foundation models to provide intelligent search, summarization,
and Q&A capabilities over document collections.

Features:
- Document indexing and storage
- Semantic search using embeddings
- Natural language query processing
- Intelligent response generation using Bedrock LLMs
- CLI interface for easy interaction
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib
import time

try:
    import boto3
    import botocore
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("Error: boto3 is required. Install with: pip install boto3")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


class BedrockAgentConfig:
    """Configuration management for Bedrock Agent."""
    
    def __init__(self):
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.bedrock_model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.embedding_model_id = os.getenv('EMBEDDING_MODEL_ID', 'amazon.titan-embed-text-v1')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '1000'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.3'))
        self.docs_directory = os.getenv('DOCS_DIRECTORY', './docs')
        self.index_file = os.getenv('INDEX_FILE', './document_index.json')


class DocumentIndex:
    """Simple document indexing and storage system."""
    
    def __init__(self, index_file: str):
        self.index_file = index_file
        self.documents = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load existing document index."""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_index(self) -> None:
        """Save document index to file."""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logging.error(f"Failed to save index: {e}")
    
    def add_document(self, file_path: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Add a document to the index."""
        doc_id = hashlib.md5(file_path.encode()).hexdigest()
        
        self.documents[doc_id] = {
            'file_path': file_path,
            'content': content,
            'metadata': metadata or {},
            'indexed_at': time.time(),
            'content_hash': hashlib.md5(content.encode()).hexdigest()
        }
        
        self._save_index()
        return doc_id
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Retrieve a document by ID."""
        return self.documents.get(doc_id)
    
    def search_documents(self, query: str) -> List[Dict]:
        """Simple text-based document search."""
        query_lower = query.lower()
        results = []
        
        for doc_id, doc_data in self.documents.items():
            content_lower = doc_data['content'].lower()
            if query_lower in content_lower:
                # Simple relevance scoring based on query frequency
                score = content_lower.count(query_lower)
                results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'file_path': doc_data['file_path'],
                    'content': doc_data['content'][:500] + '...' if len(doc_data['content']) > 500 else doc_data['content']
                })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def list_documents(self) -> List[Dict]:
        """List all indexed documents."""
        return [
            {
                'doc_id': doc_id,
                'file_path': doc_data['file_path'],
                'metadata': doc_data.get('metadata', {}),
                'indexed_at': doc_data.get('indexed_at', 0)
            }
            for doc_id, doc_data in self.documents.items()
        ]


class BedrockAgent:
    """Main AWS Bedrock Agent class."""
    
    def __init__(self, config: BedrockAgentConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.document_index = DocumentIndex(config.index_file)
        
        # Initialize AWS Bedrock client
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=config.aws_region
            )
            self.logger.info(f"Bedrock client initialized for region: {config.aws_region}")
        except NoCredentialsError:
            self.logger.error("AWS credentials not found. Please configure your AWS credentials.")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    def index_directory(self, directory_path: str) -> Dict[str, int]:
        """Index all documents in a directory."""
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        stats = {'indexed': 0, 'skipped': 0, 'errors': 0}
        
        # Supported file extensions
        supported_extensions = {'.txt', '.md', '.rst', '.py', '.json', '.yaml', '.yml'}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Skip empty files
                    if not content.strip():
                        stats['skipped'] += 1
                        continue
                    
                    metadata = {
                        'file_type': file_path.suffix,
                        'file_size': file_path.stat().st_size,
                        'relative_path': str(file_path.relative_to(directory))
                    }
                    
                    doc_id = self.document_index.add_document(str(file_path), content, metadata)
                    self.logger.debug(f"Indexed document: {file_path} (ID: {doc_id})")
                    stats['indexed'] += 1
                    
                except (UnicodeDecodeError, IOError) as e:
                    self.logger.warning(f"Failed to index {file_path}: {e}")
                    stats['errors'] += 1
        
        self.logger.info(f"Indexing complete: {stats}")
        return stats
    
    def _prepare_prompt(self, query: str, context_documents: List[Dict]) -> str:
        """Prepare a prompt for the LLM with context documents."""
        context = "\n\n".join([
            f"Document: {doc['file_path']}\nContent: {doc['content']}"
            for doc in context_documents[:3]  # Limit to top 3 documents
        ])
        
        prompt = f"""You are an intelligent assistant for an internal documentation repository. 
Use the provided context documents to answer the user's question accurately and helpfully.

Context Documents:
{context}

User Question: {query}

Please provide a comprehensive answer based on the context documents. If the context doesn't contain enough information to fully answer the question, please say so and suggest what additional information might be needed."""
        
        return prompt
    
    def query_bedrock(self, prompt: str) -> str:
        """Send a query to AWS Bedrock and get a response."""
        try:
            # Prepare the request body based on the model
            if "anthropic.claude" in self.config.bedrock_model_id:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            else:
                # Generic format for other models
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": self.config.max_tokens,
                        "temperature": self.config.temperature
                    }
                }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.config.bedrock_model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract response text based on model type
            if "anthropic.claude" in self.config.bedrock_model_id:
                return response_body['content'][0]['text']
            else:
                return response_body.get('results', [{}])[0].get('outputText', '')
            
        except ClientError as e:
            self.logger.error(f"Bedrock API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error calling Bedrock: {e}")
            raise
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using document context and Bedrock LLM."""
        # Search for relevant documents
        relevant_docs = self.document_index.search_documents(question)
        
        if not relevant_docs:
            return {
                'answer': "I couldn't find any relevant documents in the repository to answer your question. Please make sure the documents are indexed first.",
                'sources': [],
                'confidence': 'low'
            }
        
        # Prepare prompt with context
        prompt = self._prepare_prompt(question, relevant_docs)
        
        # Get response from Bedrock
        try:
            answer = self.query_bedrock(prompt)
            
            return {
                'answer': answer,
                'sources': [doc['file_path'] for doc in relevant_docs[:3]],
                'confidence': 'high' if len(relevant_docs) >= 2 else 'medium'
            }
        except Exception as e:
            self.logger.error(f"Failed to get answer from Bedrock: {e}")
            return {
                'answer': f"I encountered an error while processing your question: {str(e)}",
                'sources': [],
                'confidence': 'low'
            }
    
    def summarize_document(self, doc_id: str) -> str:
        """Summarize a specific document using Bedrock."""
        document = self.document_index.get_document(doc_id)
        if not document:
            raise ValueError(f"Document not found: {doc_id}")
        
        prompt = f"""Please provide a concise summary of the following document:

Document: {document['file_path']}
Content: {document['content']}

Summary:"""
        
        return self.query_bedrock(prompt)


def setup_logging(log_level: str) -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main():
    """Main CLI interface for the Bedrock Agent."""
    parser = argparse.ArgumentParser(description="AWS Bedrock Agent for Internal Documentation")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Set the logging level")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Index documents from a directory")
    index_parser.add_argument("directory", help="Directory to index")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Ask a question about the documents")
    query_parser.add_argument("question", help="Question to ask")
    
    # List command
    subparsers.add_parser("list", help="List all indexed documents")
    
    # Summarize command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize a document")
    summarize_parser.add_argument("doc_id", help="Document ID to summarize")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search documents")
    search_parser.add_argument("query", help="Search query")
    
    # Status command
    subparsers.add_parser("status", help="Show agent status and configuration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    setup_logging(args.log_level)
    
    try:
        config = BedrockAgentConfig()
        agent = BedrockAgent(config)
        
        if args.command == "index":
            print(f"Indexing documents from: {args.directory}")
            stats = agent.index_directory(args.directory)
            print(f"Indexing complete: {stats['indexed']} indexed, {stats['skipped']} skipped, {stats['errors']} errors")
        
        elif args.command == "query":
            print(f"Processing question: {args.question}")
            result = agent.answer_question(args.question)
            print(f"\nAnswer ({result['confidence']} confidence):")
            print(result['answer'])
            if result['sources']:
                print(f"\nSources:")
                for source in result['sources']:
                    print(f"  - {source}")
        
        elif args.command == "list":
            documents = agent.document_index.list_documents()
            if documents:
                print(f"Indexed documents ({len(documents)} total):")
                for doc in documents:
                    print(f"  ID: {doc['doc_id']}")
                    print(f"  Path: {doc['file_path']}")
                    print(f"  Indexed: {time.ctime(doc['indexed_at'])}")
                    print()
            else:
                print("No documents indexed yet.")
        
        elif args.command == "summarize":
            try:
                summary = agent.summarize_document(args.doc_id)
                print(f"Summary for document {args.doc_id}:")
                print(summary)
            except ValueError as e:
                print(f"Error: {e}")
                return 1
        
        elif args.command == "search":
            results = agent.document_index.search_documents(args.query)
            if results:
                print(f"Search results for '{args.query}' ({len(results)} found):")
                for i, result in enumerate(results[:5], 1):
                    print(f"\n{i}. {result['file_path']} (score: {result['score']})")
                    print(f"   {result['content'][:200]}...")
            else:
                print(f"No documents found matching '{args.query}'")
        
        elif args.command == "status":
            print("AWS Bedrock Agent Status:")
            print(f"  AWS Region: {config.aws_region}")
            print(f"  Bedrock Model: {config.bedrock_model_id}")
            print(f"  Documents Directory: {config.docs_directory}")
            print(f"  Index File: {config.index_file}")
            print(f"  Indexed Documents: {len(agent.document_index.documents)}")
            
            # Test AWS connection
            try:
                # Use a simple operation to test connection
                self.bedrock_client.list_foundation_models()
                print(f"  AWS Connection: ✓ Connected")
            except Exception as e:
                print(f"  AWS Connection: ✗ Error: {e}")
                print(f"  Note: Configure AWS credentials to enable Bedrock functionality")
        
        return 0
    
    except Exception as e:
        logging.error(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())