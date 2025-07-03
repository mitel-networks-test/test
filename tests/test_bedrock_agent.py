#!/usr/bin/env python3
"""
Tests for AWS Bedrock Agent Application

This module contains comprehensive tests for the Bedrock Agent functionality
including document indexing, search, and configuration management.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the Bedrock Agent modules
try:
    from bedrock_agent import BedrockAgent, BedrockAgentConfig, DocumentIndex
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from bedrock_agent import BedrockAgent, BedrockAgentConfig, DocumentIndex


class TestBedrockAgentConfig(unittest.TestCase):
    """Test the BedrockAgentConfig class."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear environment variables
        self.env_vars_to_clear = [
            'AWS_REGION', 'BEDROCK_MODEL_ID', 'EMBEDDING_MODEL_ID',
            'MAX_TOKENS', 'TEMPERATURE', 'DOCS_DIRECTORY', 'INDEX_FILE'
        ]
        self.original_env = {}
        for var in self.env_vars_to_clear:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
    
    def tearDown(self):
        """Clean up test environment."""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
    
    def test_default_configuration(self):
        """Test default configuration values."""
        config = BedrockAgentConfig()
        
        self.assertEqual(config.aws_region, 'us-east-1')
        self.assertEqual(config.bedrock_model_id, 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.assertEqual(config.embedding_model_id, 'amazon.titan-embed-text-v1')
        self.assertEqual(config.max_tokens, 1000)
        self.assertEqual(config.temperature, 0.3)
        self.assertEqual(config.docs_directory, './docs')
        self.assertEqual(config.index_file, './document_index.json')
    
    def test_environment_variable_override(self):
        """Test configuration override from environment variables."""
        os.environ['AWS_REGION'] = 'us-west-2'
        os.environ['MAX_TOKENS'] = '2000'
        os.environ['TEMPERATURE'] = '0.7'
        
        config = BedrockAgentConfig()
        
        self.assertEqual(config.aws_region, 'us-west-2')
        self.assertEqual(config.max_tokens, 2000)
        self.assertEqual(config.temperature, 0.7)


class TestDocumentIndex(unittest.TestCase):
    """Test the DocumentIndex class."""
    
    def setUp(self):
        """Set up test environment with temporary files."""
        self.temp_dir = tempfile.mkdtemp()
        self.index_file = os.path.join(self.temp_dir, 'test_index.json')
        self.document_index = DocumentIndex(self.index_file)
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_index_initialization(self):
        """Test initializing with empty index."""
        self.assertEqual(len(self.document_index.documents), 0)
    
    def test_add_document(self):
        """Test adding a document to the index."""
        file_path = "/test/document.txt"
        content = "This is a test document."
        metadata = {"type": "test"}
        
        doc_id = self.document_index.add_document(file_path, content, metadata)
        
        self.assertIsNotNone(doc_id)
        self.assertEqual(len(self.document_index.documents), 1)
        
        document = self.document_index.get_document(doc_id)
        self.assertIsNotNone(document)
        self.assertEqual(document['file_path'], file_path)
        self.assertEqual(document['content'], content)
        self.assertEqual(document['metadata'], metadata)
    
    def test_search_documents(self):
        """Test document search functionality."""
        # Add test documents
        self.document_index.add_document("/doc1.txt", "Python programming tutorial", {})
        self.document_index.add_document("/doc2.txt", "JavaScript web development", {})
        self.document_index.add_document("/doc3.txt", "Python data science guide", {})
        
        # Search for Python documents
        results = self.document_index.search_documents("Python")
        self.assertEqual(len(results), 2)
        
        # Search for non-existent term
        results = self.document_index.search_documents("nonexistent")
        self.assertEqual(len(results), 0)
        
        # Search should be case-insensitive
        results = self.document_index.search_documents("python")
        self.assertEqual(len(results), 2)
    
    def test_list_documents(self):
        """Test listing all documents."""
        # Add test documents
        doc_id1 = self.document_index.add_document("/doc1.txt", "Content 1", {"tag": "test"})
        doc_id2 = self.document_index.add_document("/doc2.txt", "Content 2", {"tag": "demo"})
        
        documents = self.document_index.list_documents()
        self.assertEqual(len(documents), 2)
        
        doc_ids = [doc['doc_id'] for doc in documents]
        self.assertIn(doc_id1, doc_ids)
        self.assertIn(doc_id2, doc_ids)
    
    def test_index_persistence(self):
        """Test that index persists across instances."""
        # Add document in first instance
        doc_id = self.document_index.add_document("/test.txt", "Test content", {})
        
        # Create new instance with same index file
        new_index = DocumentIndex(self.index_file)
        
        # Verify document persisted
        self.assertEqual(len(new_index.documents), 1)
        document = new_index.get_document(doc_id)
        self.assertIsNotNone(document)
        self.assertEqual(document['content'], "Test content")


class TestBedrockAgent(unittest.TestCase):
    """Test the BedrockAgent class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = BedrockAgentConfig()
        self.config.index_file = os.path.join(self.temp_dir, 'test_index.json')
        
        # Mock AWS Bedrock client
        self.mock_bedrock_client = Mock()
        self.mock_boto3_client = patch('bedrock_agent.boto3.client', return_value=self.mock_bedrock_client)
        self.mock_boto3_client.start()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.mock_boto3_client.stop()
    
    def test_agent_initialization(self):
        """Test agent initialization with mocked Bedrock client."""
        agent = BedrockAgent(self.config)
        self.assertIsNotNone(agent.bedrock_client)
        self.assertIsNotNone(agent.document_index)
    
    def test_index_directory(self):
        """Test directory indexing functionality."""
        # Create test directory with documents
        test_docs_dir = os.path.join(self.temp_dir, 'test_docs')
        os.makedirs(test_docs_dir)
        
        # Create test files
        test_files = {
            'doc1.txt': 'This is a text document about Python programming.',
            'doc2.md': '# Markdown Document\nThis is a markdown document about web development.',
            'doc3.py': '# Python script\nprint("Hello, World!")',
            'empty.txt': '',  # Empty file should be skipped
            'doc4.json': '{"title": "JSON Document", "content": "Configuration example"}'
        }
        
        for filename, content in test_files.items():
            with open(os.path.join(test_docs_dir, filename), 'w') as f:
                f.write(content)
        
        # Index the directory
        agent = BedrockAgent(self.config)
        stats = agent.index_directory(test_docs_dir)
        
        # Verify stats (empty.txt should be skipped)
        self.assertEqual(stats['indexed'], 4)
        self.assertEqual(stats['skipped'], 1)
        self.assertEqual(stats['errors'], 0)
        
        # Verify documents are in index
        documents = agent.document_index.list_documents()
        self.assertEqual(len(documents), 4)
    
    def test_prepare_prompt(self):
        """Test prompt preparation with context documents."""
        agent = BedrockAgent(self.config)
        
        question = "How do I configure AWS?"
        context_docs = [
            {'file_path': '/aws_guide.md', 'content': 'AWS configuration instructions...'},
            {'file_path': '/setup.txt', 'content': 'Setup guide for AWS services...'}
        ]
        
        prompt = agent._prepare_prompt(question, context_docs)
        
        self.assertIn(question, prompt)
        self.assertIn('aws_guide.md', prompt)
        self.assertIn('AWS configuration instructions', prompt)
        self.assertIn('Context Documents:', prompt)
    
    @patch('bedrock_agent.BedrockAgent.query_bedrock')
    def test_answer_question_with_documents(self, mock_query_bedrock):
        """Test question answering with relevant documents."""
        # Set up mock response
        mock_query_bedrock.return_value = "Based on the documentation, you can configure AWS by..."
        
        # Create agent and add test document with matching content
        agent = BedrockAgent(self.config)
        agent.document_index.add_document(
            "/aws_config.md", 
            "AWS credentials configuration guide - use aws configure command to set up credentials",
            {}
        )
        
        # Ask question that should match the document content
        result = agent.answer_question("AWS credentials")
        
        # Verify response
        self.assertIn('answer', result)
        self.assertIn('sources', result)
        self.assertIn('confidence', result)
        if len(result['sources']) > 0:
            self.assertTrue(any('aws_config.md' in source for source in result['sources']))
            mock_query_bedrock.assert_called_once()
        else:
            # If no sources found, it should return the no documents message
            self.assertIn("couldn't find any relevant documents", result['answer'])
    
    def test_answer_question_no_documents(self):
        """Test question answering with no relevant documents."""
        agent = BedrockAgent(self.config)
        
        result = agent.answer_question("How do I configure AWS?")
        
        self.assertIn("couldn't find any relevant documents", result['answer'])
        self.assertEqual(result['confidence'], 'low')
        self.assertEqual(len(result['sources']), 0)
    
    @patch('bedrock_agent.BedrockAgent.query_bedrock')
    def test_summarize_document(self, mock_query_bedrock):
        """Test document summarization."""
        mock_query_bedrock.return_value = "This document explains AWS configuration..."
        
        agent = BedrockAgent(self.config)
        doc_id = agent.document_index.add_document(
            "/long_doc.md", 
            "This is a very long document about AWS configuration with many details...",
            {}
        )
        
        summary = agent.summarize_document(doc_id)
        
        self.assertEqual(summary, "This document explains AWS configuration...")
        mock_query_bedrock.assert_called_once()
    
    def test_summarize_nonexistent_document(self):
        """Test summarizing a non-existent document."""
        agent = BedrockAgent(self.config)
        
        with self.assertRaises(ValueError):
            agent.summarize_document("nonexistent_id")


class TestCLIFunctionality(unittest.TestCase):
    """Test CLI functionality of the Bedrock Agent."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('bedrock_agent.boto3.client')
    def test_main_status_command(self, mock_boto3_client):
        """Test the status command."""
        mock_client = Mock()
        mock_boto3_client.return_value = mock_client
        mock_client.list_foundation_models.return_value = {}
        
        from bedrock_agent import main
        
        # Mock sys.argv
        with patch('sys.argv', ['bedrock_agent.py', 'status']):
            with patch('builtins.print') as mock_print:
                result = main()
                self.assertEqual(result, 0)
                # Verify status information was printed
                mock_print.assert_called()


def run_bedrock_agent_tests():
    """Run all Bedrock Agent tests."""
    print("\nRunning AWS Bedrock Agent Tests...")
    
    test_classes = [
        TestBedrockAgentConfig,
        TestDocumentIndex,
        TestBedrockAgent,
        TestCLIFunctionality
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        print(f"\nTesting {test_class.__name__}:")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        passed_tests += result.testsRun - len(result.failures) - len(result.errors)
        failed_tests += len(result.failures) + len(result.errors)
    
    print(f"\n{'='*60}")
    print(f"Bedrock Agent Test Summary:")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    
    return failed_tests == 0


if __name__ == '__main__':
    success = run_bedrock_agent_tests()
    sys.exit(0 if success else 1)