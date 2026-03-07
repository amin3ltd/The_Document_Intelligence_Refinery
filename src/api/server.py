"""
Document Intelligence Refinery - REST API Server

FastAPI-based REST API for document extraction pipeline.
Supports Ollama/LM Studio for local VLM inference.

Endpoints:
- POST /documents/upload - Upload and process a document
- GET /documents/{doc_id}/profile - Get document profile
- GET /documents/{doc_id}/extraction - Get extraction results
- GET /documents/{doc_id}/chunks - Get semantic chunks
- GET /documents/{doc_id}/pageindex - Get PageIndex tree
- POST /query - Query the document knowledge base
"""

import os
import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.utils.config import get_config
from src.agents.triage import TriageAgent
from src.agents.extractor import ExtractionRouter
from src.agents.chunker import Chunker
from src.agents.indexer import Indexer
from src.strategies.fast_text import FastTextStrategy
from src.strategies.layout_aware import LayoutAwareStrategy
from src.strategies.vision import VisionStrategy
from src.agents.chunker import Chunker
from src.agents.indexer import Indexer
from src.agents.query_agent import create_query_agent, QueryResult
from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument
from src.models.ldu import LDU
from src.models.page_index import PageIndex
from src.models.provenance import ProvenanceSource
from src.utils.ledger import ExtractionLedger
from src.utils.system_check import check_system_health
from loguru import logger

# Initialize FastAPI app
app = FastAPI(
    title="Document Intelligence Refinery API",
    description="Production-grade document extraction pipeline with tiered strategy routing",
    version="0.1.0"
)

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
REFINERY_DIR = Path(".refinery")
PROFILES_DIR = REFINERY_DIR / "profiles"
EXTRACTIONS_DIR = REFINERY_DIR / "extractions"
PAGEINDEX_DIR = REFINERY_DIR / "pageindex"

# Create directories
PROFILES_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTIONS_DIR.mkdir(parents=True, exist_ok=True)
PAGEINDEX_DIR.mkdir(parents=True, exist_ok=True)

# Global instances
triage_agent = TriageAgent()
extraction_router = ExtractionRouter()
# Get config for VLM settings
config = get_config()
vlm_config = config.get("vlm", {})
# Register extraction strategies with proper VLM configuration
extraction_router.register_strategy(FastTextStrategy())
extraction_router.register_strategy(LayoutAwareStrategy())
extraction_router.register_strategy(VisionStrategy(
    provider=vlm_config.get("provider", "lmstudio"),
    model=vlm_config.get("model", "llava-1.6-mistral-7b"),
    base_url=vlm_config.get("base_url", "http://localhost:1234")
))
chunker_engine = Chunker()
indexer = Indexer()
ledger = ExtractionLedger()


# Pydantic models for API
class QueryRequest(BaseModel):
    question: str
    doc_id: str
    mode: str = "auto"  # "pageindex", "semantic", "structured", "auto"


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    tool_used: str


class DocumentStatus(BaseModel):
    doc_id: str
    status: str  # "processing", "completed", "failed"
    profile: Optional[DocumentProfile] = None
    extraction_complete: bool = False
    chunking_complete: bool = False
    indexing_complete: bool = False
    error: Optional[str] = None


# In-memory document status tracking
document_status: dict = {}


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Document Intelligence Refinery API",
        "version": "0.1.0",
        "description": "Production-grade document extraction pipeline",
        "endpoints": {
            "upload": "POST /documents/upload",
            "profile": "GET /documents/{doc_id}/profile",
            "extraction": "GET /documents/{doc_id}/extraction",
            "chunks": "GET /documents/{doc_id}/chunks",
            "pageindex": "GET /documents/{doc_id}/pageindex",
            "query": "POST /query"
        }
    }


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
) -> JSONResponse:
    """
    Upload and process a document through the full pipeline.
    
    Returns immediately with doc_id. Processing happens in background.
    """
    # Generate document ID
    doc_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_path = EXTRACTIONS_DIR / f"{doc_id}_{file.filename}"
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Initialize status
    document_status[doc_id] = DocumentStatus(
        doc_id=doc_id,
        status="processing",
        profile=None,
        extraction_complete=False,
        chunking_complete=False,
        indexing_complete=False
    )
    
    # Process in background
    if background_tasks:
        background_tasks.add_task(process_document, doc_id, file_path)
    
    return JSONResponse({
        "doc_id": doc_id,
        "filename": file.filename,
        "status": "processing",
        "message": "Document uploaded. Processing started in background."
    })


async def process_document(doc_id: str, file_path: Path):
    """Process document through all pipeline stages"""
    try:
        logger.info(f"Starting pipeline for document {doc_id}")
        
        # Stage 1: Triage
        logger.info(f"[{doc_id}] Stage 1: Triage")
        triage_result = triage_agent.analyze(str(file_path))
        profile = triage_result.profile  # DocumentProfile from TriageResult
        document_status[doc_id].profile = profile
        
        # Save profile
        profile_path = PROFILES_DIR / f"{doc_id}.json"
        with open(profile_path, "w", encoding="utf-8") as f:
            f.write(profile.model_dump_json())
        
        # Stage 2: Extraction
        logger.info(f"[{doc_id}] Stage 2: Extraction")
        extraction_result = extraction_router.route(str(file_path), profile)
        extracted_doc = extraction_result.document
        
        # Save extraction
        extraction_path = EXTRACTIONS_DIR / f"{doc_id}_extraction.json"
        with open(extraction_path, "w", encoding="utf-8") as f:
            f.write(extracted_doc.model_dump_json())
        document_status[doc_id].extraction_complete = True
        
        # Stage 3: Chunking
        logger.info(f"[{doc_id}] Stage 3: Chunking")
        ldu_set = chunker_engine.chunk(extracted_doc, profile)
        
        # Save chunks - from LDUSet.ldus
        chunks_path = EXTRACTIONS_DIR / f"{doc_id}_chunks.json"
        # Convert LDU objects to serializable format
        chunks_data = []
        for ldu in ldu_set.ldus:
            if hasattr(ldu, 'model_dump'):
                chunks_data.append(ldu.model_dump())
            else:
                chunks_data.append(str(ldu))
        with open(chunks_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(chunks_data, indent=2))
        document_status[doc_id].chunking_complete = True
        
        # Stage 4: Indexing
        logger.info(f"[{doc_id}] Stage 4: Indexing")
        page_index = indexer.build_index(ldu_set, profile)
        
        # Save PageIndex
        index_path = PAGEINDEX_DIR / f"{doc_id}_pageindex.json"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(page_index.model_dump_json())
        document_status[doc_id].indexing_complete = True
        
        # Mark complete
        document_status[doc_id].status = "completed"
        logger.info(f"Document {doc_id} processing complete")
        
    except Exception as e:
        import traceback
        logger.error(f"Error processing document {doc_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        document_status[doc_id].status = "failed"
        document_status[doc_id].error = str(e)


@app.get("/api/documents")
async def list_documents():
    """List all uploaded documents"""
    documents = []
    if PROFILES_DIR.exists():
        for profile_file in PROFILES_DIR.glob("*.json"):
            doc_id = profile_file.stem
            status = document_status.get(doc_id, DocumentStatus(doc_id=doc_id, status="unknown"))
            documents.append({
                "id": doc_id,
                "name": Path(status.profile.file_path).name if status.profile and status.profile.file_path else profile_file.name,
                "status": status.status,
            })
    return {"documents": documents}

@app.get("/api/documents/{doc_id}/status")
async def get_document_status(doc_id: str) -> DocumentStatus:
    """Get processing status of a document"""
    if doc_id not in document_status:
        raise HTTPException(status_code=404, detail="Document not found")
    return document_status[doc_id]


@app.get("/api/documents/{doc_id}/profile")
async def get_document_profile(doc_id: str) -> DocumentProfile:
    """Get document profile"""
    profile_path = PROFILES_DIR / f"{doc_id}.json"
    if not profile_path.exists():
        raise HTTPException(status_code=404, detail="Profile not found")
    
    with open(profile_path, "r") as f:
        data = json.load(f)
    return DocumentProfile(**data)


@app.get("/api/documents/{doc_id}/extraction")
async def get_extraction(doc_id: str) -> ExtractedDocument:
    """Get extraction results"""
    extraction_path = EXTRACTIONS_DIR / f"{doc_id}_extraction.json"
    if not extraction_path.exists():
        raise HTTPException(status_code=404, detail="Extraction not found")
    
    with open(extraction_path, "r") as f:
        data = json.load(f)
    return ExtractedDocument(**data)


@app.get("/api/documents/{doc_id}/chunks")
async def get_chunks(doc_id: str) -> List[LDU]:
    """Get semantic chunks"""
    chunks_path = EXTRACTIONS_DIR / f"{doc_id}_chunks.json"
    if not chunks_path.exists():
        raise HTTPException(status_code=404, detail="Chunks not found")
    
    with open(chunks_path, "r") as f:
        data = json.load(f)
    return [LDU(**chunk) for chunk in data]


@app.get("/api/documents/{doc_id}/pageindex")
async def get_pageindex(doc_id: str) -> PageIndex:
    """Get PageIndex tree"""
    index_path = PAGEINDEX_DIR / f"{doc_id}_pageindex.json"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="PageIndex not found")
    
    with open(index_path, "r") as f:
        data = json.load(f)
    return PageIndex(**data)


@app.post("/api/query", response_model=QueryResponse)
async def query_document(request: QueryRequest) -> QueryResponse:
    """Query the document knowledge base"""
    # Load document data
    doc_id = request.doc_id
    
    # If no specific document, try to query across all documents
    if not doc_id or doc_id == "":
        # Get all document profiles
        all_profiles = list(PROFILES_DIR.glob("*.json"))
        
        if not all_profiles:
            raise HTTPException(status_code=404, detail="No documents found. Upload a document first.")
        
        # Load the first available document for now
        # In a full implementation, this would query across all documents
        doc_id = all_profiles[0].stem
    
    # Check if document exists
    profile_path = PROFILES_DIR / f"{doc_id}.json"
    if not profile_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Load chunks and pageindex
    chunks_path = EXTRACTIONS_DIR / f"{doc_id}_chunks.json"
    index_path = PAGEINDEX_DIR / f"{doc_id}_pageindex.json"
    
    # Check if chunks exist
    if not chunks_path.exists():
        raise HTTPException(status_code=404, detail="Document not processed yet. Please wait for processing to complete.")
    
    # Create query agent for this document
    query_agent = create_query_agent(
        doc_id=doc_id,
        ldu_file=str(chunks_path),
        index_file=str(index_path)
    )
    
    # Query using the query agent
    result = query_agent.query(
        question=request.question,
        mode=request.mode
    )
    
    return QueryResponse(
        answer=result.answer,
        sources=result.sources,
        confidence=result.confidence,
        tool_used=result.tool_used
    )


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and all its associated files"""
    deleted_files = []
    errors = []
    
    # Check if document exists (at least one file)
    profile_path = PROFILES_DIR / f"{doc_id}.json"
    if not profile_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Files to delete
    files_to_delete = [
        profile_path,
        EXTRACTIONS_DIR / f"{doc_id}_extraction.json",
        EXTRACTIONS_DIR / f"{doc_id}_chunks.json",
        PAGEINDEX_DIR / f"{doc_id}_pageindex.json",
    ]
    
    # Also delete the original uploaded file (we need to find it)
    for ext in ["*.pdf", "*.docx", "*.doc", "*.txt", "*.png", "*.jpg", "*.jpeg"]:
        for file_path in EXTRACTIONS_DIR.glob(f"{doc_id}_{ext}"):
            files_to_delete.append(file_path)
    
    # Delete all files
    for file_path in files_to_delete:
        try:
            if file_path.exists():
                file_path.unlink()
                deleted_files.append(str(file_path))
        except Exception as e:
            errors.append(f"Failed to delete {file_path}: {str(e)}")
    
    # Remove from ledger (rewrite ledger without this doc_id)
    try:
        ledger_path = Path(".refinery/extraction_ledger/extraction_ledger.jsonl")
        if ledger_path.exists():
            with open(ledger_path, "r") as f:
                lines = f.readlines()
            
            # Filter out entries for this doc_id
            filtered_lines = [
                line for line in lines 
                if doc_id not in json.loads(line).get("doc_id", "")
            ]
            
            with open(ledger_path, "w") as f:
                f.writelines(filtered_lines)
    except Exception as e:
        errors.append(f"Failed to update ledger: {str(e)}")
    
    # Remove from in-memory status
    if doc_id in document_status:
        del document_status[doc_id]
    
    return {
        "success": len(errors) == 0,
        "doc_id": doc_id,
        "deleted_files": deleted_files,
        "errors": errors,
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint with system health information"""
    # Get system health report
    try:
        system_health = check_system_health()
        health_data = system_health.get_summary()
    except Exception as e:
        logger.warning(f"System health check failed: {e}")
        health_data = {"error": str(e)}
    
    return {
        "status": "healthy" if health_data.get("healthy", False) else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "documents_processed": len([s for s in document_status.values() if s.status == "completed"]),
        "system_health": health_data,
    }


@app.get("/api/config/safety-limits")
async def get_safety_limits():
    """Get all safety limits configuration - configurable from UI"""
    config = get_config()
    return {
        "safety_limits": config.safety_limits_config,
        "defaults": {
            "max_context_tokens": 4096,
            "temperature_min": 0.0,
            "temperature_max": 0.3,
            "temperature_default": 0.1,
            "max_memory_mb": 2048,
            "max_image_size_mb": 50,
            "max_pages_per_batch": 5,
            "request_timeout": 120.0,
            "page_process_timeout": 60.0,
            "total_timeout": 600.0,
            "max_retries": 3,
            "base_retry_delay": 1.0,
            "max_retry_delay": 30.0,
            "exponential_base": 2.0,
            "cpu_throttle_threshold": 80.0,
            "cpu_pause_threshold": 95.0,
            "health_check_interval": 5,
            "max_pages_total": 500,
            "max_document_size_mb": 100,
        }
    }


@app.put("/api/config/safety-limits")
async def update_safety_limits(limits: dict):
    """Update safety limits configuration - all configurable from UI"""
    config = get_config()
    config.update_safety_limits(limits)
    return {
        "status": "success",
        "safety_limits": config.safety_limits_config
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
