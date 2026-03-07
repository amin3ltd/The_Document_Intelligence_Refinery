"""Data Layer for Document Intelligence Refinery.

Provides:
- FactTable extractor with SQLite backend for numerical documents
- Vector store ingestion (ChromaDB/FAISS) for semantic search
- Audit mode with claim verification and source citation
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.models.ldu import LDU, LDUSet
from src.models.provenance import Claim, ProvenanceChain, ProvenanceSource, VerificationStatus

logger = logging.getLogger(__name__)


class FactTableExtractor:
    """
    Extracts numerical/fact data from documents into SQLite.
    
    Ideal for financial documents, scientific papers, and reports
    that contain structured numerical data.
    """
    
    def __init__(self, db_path: str = ".refinery/fact_tables.db"):
        """
        Initialize the FactTable extractor.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the database schema."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create fact tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                doc_name TEXT,
                source_path TEXT,
                created_at TEXT,
                total_facts INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fact_tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT,
                table_name TEXT,
                row_count INTEGER,
                column_count INTEGER,
                page_number INTEGER,
                ldu_id TEXT,
                extracted_at TEXT,
                FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_table_id INTEGER,
                row_index INTEGER,
                column_name TEXT,
                value TEXT,
                value_numeric REAL,
                ldu_id TEXT,
                confidence REAL,
                FOREIGN KEY (fact_table_id) REFERENCES fact_tables(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def extract_from_ldus(self, ldu_set: LDUSet, doc_name: str = "") -> int:
        """
        Extract numerical facts from LDUs into SQLite.
        
        Args:
            ldu_set: The LDU set to extract from
            doc_name: Optional document name
            
        Returns:
            Number of facts extracted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert document record
        cursor.execute("""
            INSERT OR REPLACE INTO documents (doc_id, doc_name, created_at)
            VALUES (?, ?, ?)
        """, (ldu_set.doc_id, doc_name, datetime.utcnow().isoformat()))
        
        fact_count = 0
        
        # Process LDUs that contain numerical data
        for ldu in ldu_set.ldus:
            if not ldu.has_numbers:
                continue
            
            # Extract numerical values from content
            facts = self._extract_facts_from_ldu(ldu)
            
            if facts:
                # Create fact table entry
                cursor.execute("""
                    INSERT INTO fact_tables (doc_id, table_name, row_count, column_count, page_number, ldu_id, extracted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    ldu_set.doc_id,
                    f"table_{ldu.ldu_id}",
                    1,  # Single row for now
                    len(facts),
                    ldu.page_number,
                    ldu.ldu_id,
                    datetime.utcnow().isoformat()
                ))
                
                fact_table_id = cursor.lastrowid
                
                # Insert facts
                for row_idx, (col_name, value) in enumerate(facts.items()):
                    try:
                        numeric_value = float(value.replace(",", "").replace("$", "").replace("%", ""))
                    except (ValueError, AttributeError):
                        numeric_value = None
                    
                    cursor.execute("""
                        INSERT INTO facts (fact_table_id, row_index, column_name, value, value_numeric, ldu_id, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        fact_table_id,
                        row_idx,
                        col_name,
                        value,
                        numeric_value,
                        ldu.ldu_id,
                        0.9  # Default confidence
                    ))
                    
                    fact_count += 1
        
        # Update document fact count
        cursor.execute("""
            UPDATE documents SET total_facts = ? WHERE doc_id = ?
        """, (fact_count, ldu_set.doc_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Extracted {fact_count} facts from document {ldu_set.doc_id}")
        
        return fact_count
    
    def _extract_facts_from_ldu(self, ldu: LDU) -> Dict[str, str]:
        """Extract key-value facts from an LDU."""
        import re
        
        facts = {}
        
        # Pattern: "Key: Value" or "Key - Value"
        patterns = [
            r"(\w+(?:\s+\w+)?)\s*[:=]\s*([\d,.$%]+)",
            r"(\w+(?:\s+\w+)?)\s+-\s+([\d,.$%]+)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, ldu.content)
            for key, value in matches:
                facts[key.strip()] = value.strip()
        
        return facts
    
    def query_facts(self, doc_id: str, min_value: Optional[float] = None, max_value: Optional[float] = None) -> List[Dict]:
        """
        Query facts from a document.
        
        Args:
            doc_id: Document ID
            min_value: Minimum numeric value filter
            max_value: Maximum numeric value filter
            
        Returns:
            List of fact dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT f.column_name, f.value, f.value_numeric, ft.page_number
            FROM facts f
            JOIN fact_tables ft ON f.fact_table_id = ft.id
            WHERE ft.doc_id = ?
        """
        params = [doc_id]
        
        if min_value is not None:
            query += " AND f.value_numeric >= ?"
            params.append(min_value)
        
        if max_value is not None:
            query += " AND f.value_numeric <= ?"
            params.append(max_value)
        
        cursor.execute(query, params)
        
        results = [
            {
                "column_name": row[0],
                "value": row[1],
                "value_numeric": row[2],
                "page_number": row[3]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return results


class VectorStoreIngestion:
    """
    Ingest LDUs into vector stores for semantic search.
    
    Supports ChromaDB and FAISS backends.
    """
    
    def __init__(
        self,
        backend: str = "chroma",
        persist_directory: str = ".refinery/vector_store"
    ):
        """
        Initialize vector store ingestion.
        
        Args:
            backend: Vector store backend ("chroma" or "faiss")
            persist_directory: Directory to persist the vector store
        """
        self.backend = backend
        self.persist_directory = persist_directory
        self.embeddings = None
        
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
    
    def set_embeddings(self, embeddings: Any) -> None:
        """
        Set the embeddings model.
        
        Args:
            embeddings: Embeddings model (e.g., sentence-transformers)
        """
        self.embeddings = embeddings
    
    def ingest_ldus(self, ldu_set: LDUSet) -> int:
        """
        Ingest LDUs into the vector store.
        
        Args:
            ldu_set: The LDU set to ingest
            
        Returns:
            Number of LDUs ingested
        """
        if self.embeddings is None:
            # Use simple keyword-based embeddings as fallback
            return self._ingest_with_keywords(ldu_set)
        
        if self.backend == "chroma":
            return self._ingest_chroma(ldu_set)
        elif self.backend == "faiss":
            return self._ingest_faiss(ldu_set)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
    
    def _ingest_with_keywords(self, ldu_set: LDUSet) -> int:
        """Simple keyword-based ingestion (fallback)."""
        # Create simple index file
        index_data = {
            "doc_id": ldu_set.doc_id,
            "ldus": [
                {
                    "ldu_id": ldu.ldu_id,
                    "content": ldu.content,
                    "page_number": ldu.page_number,
                    "chunk_type": ldu.chunk_type,
                    "keywords": list(set(ldu.content.lower().split()))
                }
                for ldu in ldu_set.ldus
            ]
        }
        
        output_path = Path(self.persist_directory) / f"{ldu_set.doc_id}_index.json"
        with open(output_path, "w") as f:
            json.dump(index_data, f, indent=2)
        
        logger.info(f"Ingested {len(ldu_set.ldus)} LDUs (keyword index)")
        
        return len(ldu_set.ldus)
    
    def _ingest_chroma(self, ldu_set: LDUSet) -> int:
        """Ingest into ChromaDB."""
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            logger.warning("ChromaDB not installed, using keyword fallback")
            return self._ingest_with_keywords(ldu_set)
        
        client = chromadb.PersistentClient(path=self.persist_directory)
        collection = client.get_or_create_collection(name=ldu_set.doc_id)
        
        # Generate embeddings
        texts = [ldu.content for ldu in ldu_set.ldus]
        embeddings = self.embeddings.embed_documents(texts)
        
        # Add to collection
        collection.add(
            ids=[ldu.ldu_id for ldu in ldu_set.ldus],
            documents=texts,
            embeddings=embeddings,
            metadatas=[
                {
                    "page_number": ldu.page_number,
                    "chunk_type": ldu.chunk_type,
                    "doc_id": ldu.doc_id
                }
                for ldu in ldu_set.ldus
            ]
        )
        
        logger.info(f"Ingested {len(ldu_set.ldus)} LDUs (ChromaDB)")
        
        return len(ldu_set.ldus)
    
    def _ingest_faiss(self, ldu_set: LDUSet) -> int:
        """Ingest into FAISS."""
        try:
            import faiss
            import numpy as np
        except ImportError:
            logger.warning("FAISS not installed, using keyword fallback")
            return self._ingest_with_keywords(ldu_set)
        
        # Generate embeddings
        texts = [ldu.content for ldu in ldu_set.ldus]
        embeddings = self.embeddings.embed_documents(texts)
        
        # Convert to numpy and normalize
        embeddings_matrix = np.array(embeddings).astype("float32")
        
        # Create index
        dimension = embeddings_matrix.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        index.add(embeddings_matrix)
        
        # Save index
        faiss.write_index(index, f"{self.persist_directory}/{ldu_set.doc_id}.index")
        
        # Save metadata
        metadata = [
            {
                "ldu_id": ldu.ldu_id,
                "content": ldu.content,
                "page_number": ldu.page_number,
                "chunk_type": ldu.chunk_type
            }
            for ldu in ldu_set.ldus
        ]
        
        with open(f"{self.persist_directory}/{ldu_set.doc_id}_meta.json", "w") as f:
            json.dump(metadata, f)
        
        logger.info(f"Ingested {len(ldu_set.ldus)} LDUs (FAISS)")
        
        return len(ldu_set.ldus)


class AuditMode:
    """
    Audit mode for claim verification with source citation.
    
    Verifies claims against the provenance chain and provides
    source citations or "unverifiable" flags.
    """
    
    def __init__(self, provenance_chain: ProvenanceChain):
        """
        Initialize audit mode.
        
        Args:
            provenance_chain: The provenance chain to verify against
        """
        self.provenance_chain = provenance_chain
    
    def verify_claim(self, claim_text: str) -> Claim:
        """
        Verify a claim against the provenance chain.
        
        Args:
            claim_text: The claim to verify
            
        Returns:
            Claim with verification status and sources
        """
        claim_id = f"claim_{hash(claim_text) % 100000:05d}"
        
        # Search for supporting evidence in the provenance chain
        supporting_sources: List[ProvenanceSource] = []
        claim_keywords = set(claim_text.lower().split())
        
        for claim in self.provenance_chain.claims:
            for source in claim.sources:
                source_keywords = set(source.content.text.lower().split())
                
                # Check for keyword overlap
                overlap = claim_keywords & source_keywords
                
                if len(overlap) >= 2:  # At least 2 matching keywords
                    supporting_sources.append(source)
        
        # Determine verification status
        if len(supporting_sources) >= 2:
            status = VerificationStatus.VERIFIED
            verification_note = f"Found {len(supporting_sources)} supporting sources"
        elif len(supporting_sources) == 1:
            status = VerificationStatus.PARTIALLY_VERIFIED
            verification_note = "Found 1 supporting source"
        else:
            status = VerificationStatus.UNVERIFIABLE
            verification_note = "No supporting sources found in provenance chain"
        
        # Create the claim
        claim = Claim(
            claim_id=claim_id,
            claim_text=claim_text,
            verification_status=status,
            supporting_sources=supporting_sources,
            verification_note=verification_note,
            verified_at=datetime.utcnow().isoformat()
        )
        
        return claim
    
    def batch_verify(self, claims: List[str]) -> List[Claim]:
        """
        Verify multiple claims at once.
        
        Args:
            claims: List of claim texts to verify
            
        Returns:
            List of verified claims
        """
        return [self.verify_claim(claim) for claim in claims]
    
    def create_audit_report(self, claims: List[Claim]) -> Dict[str, Any]:
        """
        Create an audit report from verified claims.
        
        Args:
            claims: List of verified claims
            
        Returns:
            Audit report dictionary
        """
        total_claims = len(claims)
        verified = sum(1 for c in claims if c.verification_status == VerificationStatus.VERIFIED)
        partially_verified = sum(1 for c in claims if c.verification_status == VerificationStatus.PARTIALLY_VERIFIED)
        unverifiable = sum(1 for c in claims if c.verification_status == VerificationStatus.UNVERIFIABLE)
        
        report = {
            "audit_date": datetime.utcnow().isoformat(),
            "doc_id": self.provenance_chain.doc_id,
            "chain_id": self.provenance_chain.chain_id,
            "summary": {
                "total_claims": total_claims,
                "verified": verified,
                "partially_verified": partially_verified,
                "unverifiable": unverifiable,
                "verification_rate": verified / total_claims if total_claims > 0 else 0.0
            },
            "claims": [
                {
                    "claim_id": c.claim_id,
                    "claim_text": c.claim_text,
                    "status": c.verification_status.value,
                    "note": c.verification_note,
                    "source_count": len(c.supporting_sources)
                }
                for c in claims
            ]
        }
        
        return report
