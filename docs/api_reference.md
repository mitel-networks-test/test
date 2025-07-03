# API Reference Documentation

## BedrockAgent Class

The main class for interacting with AWS Bedrock and managing document operations.

### Constructor

```python
BedrockAgent(config: BedrockAgentConfig)
```

Initializes the Bedrock agent with the provided configuration.

**Parameters:**
- `config`: BedrockAgentConfig object containing AWS and model settings

**Raises:**
- `NoCredentialsError`: If AWS credentials are not found
- `Exception`: If Bedrock client initialization fails

### Methods

#### index_directory(directory_path: str) -> Dict[str, int]

Indexes all supported documents in the specified directory and its subdirectories.

**Parameters:**
- `directory_path`: Path to the directory containing documents to index

**Returns:**
- Dictionary with indexing statistics:
  - `indexed`: Number of successfully indexed documents
  - `skipped`: Number of skipped documents (empty files)
  - `errors`: Number of documents that failed to index

**Supported File Types:**
- .txt (plain text)
- .md (Markdown)
- .rst (reStructuredText)
- .py (Python source)
- .json (JSON data)
- .yaml/.yml (YAML configuration)

**Example:**
```python
agent = BedrockAgent(config)
stats = agent.index_directory('./docs')
print(f"Indexed {stats['indexed']} documents")
```

#### answer_question(question: str) -> Dict[str, Any]

Processes a natural language question using relevant documents and Bedrock LLM.

**Parameters:**
- `question`: Natural language question about the documentation

**Returns:**
- Dictionary containing:
  - `answer`: Generated response from the LLM
  - `sources`: List of source document paths used
  - `confidence`: Confidence level ('high', 'medium', 'low')

**Example:**
```python
result = agent.answer_question("How do I configure AWS credentials?")
print(result['answer'])
print("Sources:", result['sources'])
```

#### summarize_document(doc_id: str) -> str

Generates a summary of a specific document using Bedrock LLM.

**Parameters:**
- `doc_id`: Unique identifier of the document to summarize

**Returns:**
- String containing the generated summary

**Raises:**
- `ValueError`: If the document ID is not found

**Example:**
```python
summary = agent.summarize_document("abc123")
print(summary)
```

#### query_bedrock(prompt: str) -> str

Low-level method to send a prompt directly to Bedrock LLM.

**Parameters:**
- `prompt`: Text prompt to send to the model

**Returns:**
- Generated response text from the model

**Raises:**
- `ClientError`: If the Bedrock API call fails
- `Exception`: For other unexpected errors

## DocumentIndex Class

Manages document storage and retrieval operations.

### Constructor

```python
DocumentIndex(index_file: str)
```

**Parameters:**
- `index_file`: Path to the JSON file for storing document index

### Methods

#### add_document(file_path: str, content: str, metadata: Optional[Dict] = None) -> str

Adds a document to the index.

**Parameters:**
- `file_path`: Original path of the document
- `content`: Full text content of the document
- `metadata`: Optional metadata dictionary

**Returns:**
- Unique document ID (MD5 hash of file path)

#### get_document(doc_id: str) -> Optional[Dict]

Retrieves a document by its ID.

**Parameters:**
- `doc_id`: Unique document identifier

**Returns:**
- Document dictionary or None if not found

#### search_documents(query: str) -> List[Dict]

Searches documents using simple text matching.

**Parameters:**
- `query`: Search query string

**Returns:**
- List of matching documents with relevance scores

#### list_documents() -> List[Dict]

Returns a list of all indexed documents with metadata.

**Returns:**
- List of document summaries

## BedrockAgentConfig Class

Configuration management for the Bedrock Agent.

### Environment Variables

The following environment variables can be used for configuration:

- `AWS_REGION`: AWS region (default: us-east-1)
- `BEDROCK_MODEL_ID`: Foundation model identifier
- `EMBEDDING_MODEL_ID`: Embedding model identifier  
- `MAX_TOKENS`: Maximum response tokens (default: 1000)
- `TEMPERATURE`: Model temperature (default: 0.3)
- `DOCS_DIRECTORY`: Default docs directory (default: ./docs)
- `INDEX_FILE`: Index file location (default: ./document_index.json)

### Default Values

```python
config = BedrockAgentConfig()
print(config.aws_region)           # us-east-1
print(config.bedrock_model_id)     # anthropic.claude-3-sonnet-20240229-v1:0
print(config.max_tokens)           # 1000
print(config.temperature)          # 0.3
```

## CLI Commands

### index

Index documents from a directory:
```bash
python3 bedrock_agent.py index <directory>
```

### query

Ask a question about the documents:
```bash
python3 bedrock_agent.py query "<question>"
```

### search

Search for documents containing specific terms:
```bash
python3 bedrock_agent.py search "<search_terms>"
```

### list

List all indexed documents:
```bash
python3 bedrock_agent.py list
```

### summarize

Summarize a specific document:
```bash
python3 bedrock_agent.py summarize <doc_id>
```

### status

Show agent status and configuration:
```bash
python3 bedrock_agent.py status
```

## Error Handling

### Common Exceptions

- `NoCredentialsError`: AWS credentials not configured
- `ClientError`: AWS API errors (permissions, model access, etc.)
- `FileNotFoundError`: Directory or file not found
- `ValueError`: Invalid parameters or document IDs
- `UnicodeDecodeError`: File encoding issues

### Best Practices

1. Always handle exceptions when calling agent methods
2. Check configuration before making API calls
3. Validate document IDs before operations
4. Use appropriate logging levels for debugging