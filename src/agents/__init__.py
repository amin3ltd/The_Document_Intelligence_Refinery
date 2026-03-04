"""Agents package for the Document Intelligence Refinery."""

from src.agents.triage import (
    DomainClassifier,
    PageAnalysis,
    TriageAgent,
    TriageResult,
    triage_document,
)
from src.agents.extractor import (
    ExtractionRouter,
    ExtractionStrategy,
    create_router,
)
from src.agents.chunker import (
    ChunkingRules,
    Chunker,
)
from src.agents.indexer import (
    Indexer,
    build_pageindex,
)
from src.agents.query_agent import (
    QueryAgent,
    QueryResult,
    create_query_agent,
)

__all__ = [
    # Triage
    "DomainClassifier",
    "PageAnalysis",
    "TriageAgent",
    "TriageResult",
    "triage_document",
    # Extraction
    "ExtractionRouter",
    "ExtractionStrategy",
    "create_router",
    # Chunking
    "ChunkingRules",
    "Chunker",
    # Indexing
    "Indexer",
    "build_pageindex",
    # Query
    "QueryAgent",
    "QueryResult",
    "create_query_agent",
]
