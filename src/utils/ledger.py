"""
Extraction Ledger for tracking document processing history.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.models.document_profile import DocumentProfile

logger = logging.getLogger(__name__)


class ExtractionLedger:
    """
    Tracks all document processing operations for audit trail.
    
    Records each extraction attempt, strategy used, confidence scores,
    and outcomes for quality tracking and debugging.
    """
    
    def __init__(self, ledger_path: str = ".refinery/extraction_ledger/extraction_ledger.jsonl"):
        """
        Initialize the ledger.
        
        Args:
            ledger_path: Path to the ledger file (JSONL format)
        """
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_extraction_start(
        self,
        doc_id: str,
        file_path: str,
        strategy: str,
    ) -> None:
        """Log the start of an extraction operation."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "extraction_start",
            "doc_id": doc_id,
            "file_path": file_path,
            "strategy": strategy,
        }
        self._write_entry(entry)
    
    def log_extraction_complete(
        self,
        doc_id: str,
        strategy: str,
        success: bool,
        pages_processed: int,
        confidence_score: float,
        extraction_time_ms: int,
        error: Optional[str] = None,
    ) -> None:
        """Log the completion of an extraction operation."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "extraction_complete",
            "doc_id": doc_id,
            "strategy": strategy,
            "success": success,
            "pages_processed": pages_processed,
            "confidence_score": confidence_score,
            "extraction_time_ms": extraction_time_ms,
        }
        
        if error:
            entry["error"] = error
        
        self._write_entry(entry)
    
    def log_escalation(
        self,
        doc_id: str,
        from_strategy: str,
        to_strategy: str,
        reason: str,
    ) -> None:
        """Log an escalation from one strategy to another."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "escalation",
            "doc_id": doc_id,
            "from_strategy": from_strategy,
            "to_strategy": to_strategy,
            "reason": reason,
        }
        self._write_entry(entry)
    
    def log_triage(
        self,
        profile: DocumentProfile,
    ) -> None:
        """Log the triage classification result."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "triage",
            "doc_id": profile.doc_id,
            "file_path": profile.file_path,
            "origin_type": profile.origin_type.value if hasattr(profile.origin_type, 'value') else profile.origin_type,
            "layout_complexity": profile.layout_complexity.value if hasattr(profile.layout_complexity, 'value') else profile.layout_complexity,
            "domain_hint": profile.domain_hint.value if hasattr(profile.domain_hint, 'value') else profile.domain_hint,
            "extraction_cost_hint": profile.extraction_cost_hint.value if hasattr(profile.extraction_cost_hint, 'value') else profile.extraction_cost_hint,
            "page_count": profile.page_count,
            "confidence_score": profile.confidence_score,
        }
        self._write_entry(entry)
    
    def log_chunking(
        self,
        doc_id: str,
        strategy: str,
        ldu_count: int,
        processing_time_ms: int,
    ) -> None:
        """Log chunking operation."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "chunking",
            "doc_id": doc_id,
            "strategy": strategy,
            "ldu_count": ldu_count,
            "processing_time_ms": processing_time_ms,
        }
        self._write_entry(entry)
    
    def log_indexing(
        self,
        doc_id: str,
        node_count: int,
        depth: int,
        processing_time_ms: int,
    ) -> None:
        """Log indexing operation."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "indexing",
            "doc_id": doc_id,
            "node_count": node_count,
            "depth": depth,
            "processing_time_ms": processing_time_ms,
        }
        self._write_entry(entry)
    
    def _write_entry(self, entry: Dict[str, Any]) -> None:
        """Write a single entry to the ledger."""
        try:
            with open(self.ledger_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write to ledger: {e}")
    
    def get_history(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get all entries for a specific document."""
        entries = []
        
        if not self.ledger_path.exists():
            return entries
        
        with open(self.ledger_path) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("doc_id") == doc_id:
                        entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        return entries
    
    def get_all_entries(self) -> List[Dict[str, Any]]:
        """Get all ledger entries."""
        entries = []
        
        if not self.ledger_path.exists():
            return entries
        
        with open(self.ledger_path) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        return entries
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from the ledger."""
        entries = self.get_all_entries()
        
        if not entries:
            return {
                "total_documents": 0,
                "total_extractions": 0,
                "total_escalations": 0,
                "success_rate": 0.0,
                "avg_confidence": 0.0,
            }
        
        # Count unique documents
        doc_ids = set(e.get("doc_id") for e in entries if e.get("doc_id"))
        
        # Count extractions
        extractions = [e for e in entries if e.get("event") == "extraction_complete"]
        
        # Count successes
        successes = [e for e in extractions if e.get("success")]
        
        # Count escalations
        escalations = [e for e in entries if e.get("event") == "escalation"]
        
        # Calculate average confidence
        confidences = [e.get("confidence_score", 0) for e in extractions]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "total_documents": len(doc_ids),
            "total_extractions": len(extractions),
            "successful_extractions": len(successes),
            "failed_extractions": len(extractions) - len(successes),
            "total_escalations": len(escalations),
            "success_rate": len(successes) / len(extractions) if extractions else 0.0,
            "avg_confidence": avg_confidence,
        }


# Global ledger instance
_ledger: Optional[ExtractionLedger] = None


def get_ledger(ledger_path: Optional[str] = None) -> ExtractionLedger:
    """Get the global ledger instance."""
    global _ledger
    
    if _ledger is None:
        _ledger = ExtractionLedger(ledger_path or ".refinery/extraction_ledger/extraction_ledger.jsonl")
    
    return _ledger
