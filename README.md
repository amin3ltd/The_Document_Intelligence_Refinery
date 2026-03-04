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
│   │   ├── document_profile.py
│   │   ├── extracted_document.py
│   │   ├── ldu.py
│   │   ├── page_index.py
│   │   └── provenance.py
│   ├── agents/          # Pipeline agents
│   │   ├── triage.py
│   │   ├── extractor.py
│   │   ├── chunker.py
│   │   ├── indexer.py
│   │   └── query_agent.py
│   ├── strategies/      # Extraction strategies
│   │   ├── fast_text.py      # Strategy A
│   │   ├── layout_aware.py   # Strategy B
│   │   └── vision.py         # Strategy C (supports Ollama/LM Studio)
│   ├── api/             # REST API server
│   │   └── server.py
│   └── utils/           # Utilities
│       ├── config.py
│       ├── ledger.py
│       └── ollama_client.py  # Local VLM client
├── tests/               # Unit tests
├── rubric/              # Configuration
│   └── extraction_rules.yaml
├── .refinery/           # Output directories
│   ├── profiles/        # DocumentProfile JSON
│   ├── extraction_ledger.jsonl
│   └── pageindex/
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
