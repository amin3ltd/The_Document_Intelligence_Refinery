# Document Intelligence Refinery

> **Complete Implementation** | An intelligent document processing pipeline with tiered extraction strategies

The Document Intelligence Refinery is an agentic pipeline that intelligently processes documents using a tiered extraction strategy, optimizing for cost, quality, and processing time.

## Overview

The refinery implements a 5-stage agentic pipeline:

1. **Triage Agent** - Classifies documents to determine optimal extraction strategy
2. **Structure Extraction** - Extracts content using the appropriate strategy
3. **Semantic Chunking** - Creates Logical Document Units (LDUs) preserving context
4. **PageIndex Builder** - Builds hierarchical navigation trees
5. **Query Interface** - Provides natural language querying with provenance

## Architecture

```
INPUT          Stage 1        Stage 2        Stage 3        Stage 4        Stage 5
               (Triage)       (Extract)      (Chunk)        (Index)        (Query)
               
PDFs ──────► Classifier ──► Strategy A ──► LDUs ──────► Tree ──────► Semantic
Excel ─────► Document ───► Strategy B ──► (5 rules) ──► PageIndex ──► Search
Word ──────► Profile ─────► Strategy C ───────────────► Navigation ──► Query
Images ───────────────────────────►                   
```

## Quick Start

### Installation

```bash
# Clone the repository
cd document-intelligence-refinery

# Install with all dependencies
pip install -e .

# Or install with specific extras
pip install -e ".[test,dev]"
```

### Running the API Server

```bash
# Start the REST API server
py -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload

# Or use the module directly
python -m src.api.server
```

The API server will start at `http://localhost:8000`

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/documents/upload` | POST | Upload and process document |
| `/documents/{doc_id}/status` | GET | Get processing status |
| `/documents/{doc_id}/profile` | GET | Get document profile |
| `/documents/{doc_id}/extraction` | GET | Get extraction results |
| `/documents/{doc_id}/chunks` | GET | Get semantic chunks |
| `/documents/{doc_id}/pageindex` | GET | Get PageIndex tree |
| `/query` | POST | Query document |
| `/mcp/tools` | GET | List MCP tools (AI agent integration) |
| `/mcp/execute` | POST | Execute MCP tool |

### Example Usage

```bash
# Upload a document
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@document.pdf"

# Get document status
curl "http://localhost:8000/documents/{doc_id}/status"

# Query the document
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the revenue?", "doc_id": "your-doc-id"}'
```

### Basic Usage (Python)

```python
from src.agents.triage import triage_document
from src.agents.extractor import create_router
from src.agents.chunker import Chunker
from src.agents.indexer import Indexer

# Stage 1: Triage
profile = triage_document("document.pdf")
print(f"Origin: {profile.origin_type}")
print(f"Layout: {profile.layout_complexity}")
print(f"Strategy: {profile.extraction_cost_hint}")

# Stage 2: Extraction
router = create_router()
extracted_doc = router.route("document.pdf", profile)

# Stage 3: Chunking
chunker = Chunker()
ldu_set = chunker.chunk(extracted_doc, profile)

# Stage 4: Indexing
indexer = Indexer()
page_index = indexer.build_index(ldu_set, profile)
```

## Project Structure

```
document-intelligence-refinery/
├── src/
│   ├── models/           # Pydantic data models
│   │   ├── bbox.py           # Bounding box with geometric operations
│   │   ├── document_profile.py
│   │   ├── elements.py       # Element-based result format
│   │   ├── extracted_document.py
│   │   ├── ldu.py
│   │   ├── page_index.py
│   │   └── provenance.py
│   ├── agents/          # Pipeline agents
│   │   ├── triage.py
│   │   ├── extractor.py
│   │   ├── chunker.py        # Semantic chunking with ChunkValidator
│   │   ├── indexer.py        # PageIndex with LLM summaries
│   │   └── query_agent.py    # LangGraph with 3 tools
│   ├── strategies/      # Extraction strategies
│   │   ├── fast_text.py      # Strategy A
│   │   ├── layout_aware.py   # Strategy B
│   │   └── vision.py         # Strategy C (supports Ollama/LM Studio)
│   ├── api/             # REST API server
│   │   ├── server.py
│   │   └── mcp_server.py # MCP server for AI agents
│   └── utils/           # Utilities
│       ├── config.py
│       ├── data_layer.py    # FactTable, VectorStore, AuditMode
│       ├── ledger.py
│       ├── ollama_client.py  # Local VLM client
│       ├── plugin_system.py # Extensible plugin architecture
│       ├── rust_bindings.py # Rust performance bindings
│       ├── stopwords.py # 64 language stopwords + Amharic
│       ├── text_quality.py # OCR artifact detection
│       ├── token_reduction.py # CJK & semantic reduction
│       ├── keyword_extraction.py # YAKE & RAKE algorithms
│       ├── language_detection.py # Multi-language detection
│       ├── mcp_server.py # MCP server for AI agents
│       └── plugins/          # Plugin implementations
│           ├── ocr_backend.py
│           ├── validator.py
│           └── post_processor.py
├── rust_ext/            # Rust extensions for performance
│   ├── Cargo.toml
│   └── src/lib.rs
├── tests/               # Unit tests
├── rubric/              # Configuration
│   └── extraction_rules.yaml
├── .refinery/           # Output directories
│   ├── profiles/        # DocumentProfile JSON
│   ├── extraction_ledger.jsonl
│   ├── pageindex/
│   └── fact_tables.db  # SQLite for numerical data
├── Dockerfile           # Container deployment
├── pyproject.toml
└── README.md
```

## Extraction Strategies

| Strategy | Tool | Cost/Page | Use Case |
|----------|------|------------|----------|
| **Strategy A** | pdfplumber | ~$0.001 | Native digital, simple layouts |
| **Strategy B** | MinerU/Docling | ~$0.01-0.05 | Multi-column, tables, mixed |
| **Strategy C** | VLM (Ollama/LM Studio/GPT-4o) | Free/$0.10-0.50 | Scanned images, handwriting |

### Local VLM Support

The pipeline supports local Vision Language Models via:

- **Ollama** (http://localhost:11434) - Free, open-source
- **LM Studio** (http://localhost:1234) - Free, user-friendly

```python
from src.strategies.vision import VisionStrategy

# Use Ollama
strategy = VisionStrategy(provider="ollama", model="llava")

# Use LM Studio  
strategy = VisionStrategy(provider="lmstudio", model="llava")
```

## Decision Tree

The Triage Agent determines the extraction strategy based on:

1. **Origin Type**: native_digital, scanned_image, mixed
2. **Layout Complexity**: single_column, multi_column, table_heavy, figure_heavy
3. **Domain Hint**: financial, legal, technical, medical, general

### Escalation Logic

```
Strategy A → confidence < 0.50 → Strategy B
Strategy B → confidence < 0.80 → Strategy C
Strategy C → confidence < 0.75 → Manual Review
```

## Configuration

### Environment Variables

```bash
# Paths
REFINERY_PROFILES_DIR=.refinery/profiles
REFINERY_LEDGER_PATH=.refinery/extraction_ledger.jsonl
REFINERY_PAGEINDEX_DIR=.refinery/pageindex

# Extraction
REFINERY_DEFAULT_STRATEGY=strategy_a

# VLM Settings (Local)
REFINERY_VLM_PROVIDER=ollama
REFINERY_VLM_MODEL=llava
REFINERY_VLM_BASE_URL=http://localhost:11434

# Logging
REFINERY_LOG_LEVEL=INFO
```

## Plugin System

The refinery supports extensible plugins for custom processing:

```python
from src.utils.plugins import (
    get_ocr_backend, OcrBackendType,
    get_validator,
    get_post_processor, PostProcessorType
)

# OCR Backends
ocr = get_ocr_backend(OcrBackendType.TESSERACT)
ocr = get_ocr_backend(OcrBackendType.EASYOCR)
ocr = get_ocr_backend(OcrBackendType.PADDLEOCR)

# Validators
validator = get_validator("quality")
validator = get_validator("security")

# Post-processors
processor = get_post_processor(PostProcessorType.TEXT_CLEANUP)
processor = get_post_processor(PostProcessorType.LANGUAGE_DETECTION)
processor = get_post_processor(PostProcessorType.ENTITY_EXTRACTION)
```

## Text Processing Utilities

### Stopwords
Multi-language stopword filtering for 14+ languages:

```python
from src.utils.stopwords import Stopwords, get_stopwords, filter_stopwords

# Get stopwords for a language
stopwords = get_stopwords("en")  # English
stopwords = get_stopwords("am")  # Amharic
stopwords = get_stopwords("de")  # German

# Filter stopwords from text
filtered = filter_stopwords("This is a sample text", "en")

# Check if a word is a stopword
from src.utils.stopwords import is_stopword
print(is_stopword("the", "en"))  # True
```

### Language Detection
Detect document and page languages:

```python
from src.utils.language_detection import detect_language, detect_document_languages

# Detect single text language
lang, confidence = detect_language("This is English text")

# Detect multi-page document languages
pages = ["Page 1 text", "Page 2 text"]
result = detect_document_languages(pages)
```

### Keyword Extraction
Extract keywords using YAKE or RAKE algorithms:

```python
from src.utils.keyword_extraction import extract_keywords_yake, extract_keywords_rake

# YAKE keyword extraction
keywords = extract_keywords_yake("Sample text for keyword extraction", top_n=10)

# RAKE keyword extraction
keywords = extract_keywords_rake("Sample text for keyword extraction", top_n=10)
```

### Text Quality Processing
Assess and clean OCR-generated text:

```python
from src.utils.text_quality import calculate_quality_score, clean_text, get_quality_report

# Calculate quality score
score = calculate_quality_score("Sample text")
print(f"Quality: {score.overall}")  # 0.0 - 1.0

# Clean text with OCR artifacts
cleaned = clean_text("Text with    multiple   spaces")

# Get detailed quality report
report = get_quality_report("Sample text")
```

### Token Reduction
Reduce token count while preserving meaning:

```python
from src.utils.token_reduction import reduce_tokens, extract_cjk_keywords

# Reduce tokens (hybrid method)
result = reduce_tokens("Long text here...", max_tokens=512)
print(result.reduced_text)
print(result.reduction_ratio)

# Extract CJK keywords
keywords = extract_cjk_keywords("中文文本", top_n=10)
```

## Data Layer

### FactTable Extraction
Extract numerical data from documents into SQLite:

```python
from src.utils.data_layer import FactTableExtractor

extractor = FactTableExtractor(".refinery/fact_tables.db")
fact_count = extractor.extract_from_ldus(ldu_set)
facts = extractor.query_facts(doc_id, min_value=100, max_value=1000)
```

### Vector Store Ingestion
Store LDUs in ChromaDB or FAISS for semantic search:

```python
from src.utils.data_layer import VectorStoreIngestion

vector_store = VectorStoreIngestion(backend="chroma")
# or
vector_store = VectorStoreIngestion(backend="faiss")

count = vector_store.ingest_ldus(ldu_set)
```

### Audit Mode
Verify claims against provenance chain:

```python
from src.utils.data_layer import AuditMode

audit = AuditMode(provenance_chain)
claim = audit.verify_claim("The revenue increased by 15%")
report = audit.create_audit_report(claims)
```

## Rust Performance Extensions

For high-performance text processing, build the Rust extension:

```bash
cd rust_ext
cargo build --release
```

Python bindings automatically use Rust when available:

```python
from src.utils.rust_bindings import FastTextProcessor, FastBoundingBox

processor = FastTextProcessor(max_chunk_size=1000)
chunks = processor.split_into_chunks(text)
keywords = processor.extract_keywords(texts, top_k=20)

bbox = FastBoundingBox(0, 0, 100, 100)
iou = bbox.iou(other_bbox)
```

## Docker Deployment

```bash
# Build the image
docker build -t refinery:latest .

# Run the container
docker run -p 8000:8000 refinery:latest
```

### extraction_rules.yaml

The `rubric/extraction_rules.yaml` file defines:

- Confidence thresholds per strategy
- Routing rules
- Chunking constitution rules
- Domain classification keywords
- Quality gates

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_triage.py

# Run with coverage
pytest --cov=src tests/
```

## Development

```bash
# Setup pre-commit hooks
pre-commit install

# Format code
black .
isort .

# Type checking
mypy src/
```

## License

MIT License - See LICENSE file for details

---

*Document Intelligence Refinery - Complete Implementation*
