"""Unit tests for data layer module (FactTable, VectorStore, AuditMode)."""

import pytest
import tempfile
import os
from pathlib import Path


class TestFactTableExtractor:
    """Test cases for FactTableExtractor class."""
    
    def test_fact_table_creation(self):
        """Test FactTable creation."""
        from src.utils.data_layer import FactTableExtractor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            extractor = FactTableExtractor(db_path)
            
            assert os.path.exists(db_path)
    
    def test_fact_table_schema(self):
        """Test FactTable schema."""
        from src.utils.data_layer import FactTableExtractor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            extractor = FactTableExtractor(db_path)
            
            # Verify table exists
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            assert "fact_tables" in tables


class TestVectorStoreIngestion:
    """Test cases for VectorStoreIngestion class."""
    
    def test_chroma_backend_creation(self):
        """Test ChromaDB backend creation."""
        from src.utils.data_layer import VectorStoreIngestion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStoreIngestion(backend="chroma", persist_directory=tmpdir)
            
            assert store is not None
            assert store.backend == "chroma"
    
    def test_faiss_backend_creation(self):
        """Test FAISS backend creation."""
        from src.utils.data_layer import VectorStoreIngestion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStoreIngestion(backend="faiss", persist_directory=tmpdir)
            
            assert store is not None
            assert store.backend == "faiss"


class TestAuditMode:
    """Test cases for AuditMode class."""
    
    def test_audit_mode_creation(self):
        """Test AuditMode creation."""
        from src.utils.data_layer import AuditMode
        
        # Create sample provenance chain
        provenance_chain = [
            {
                "doc_id": "test-doc-1",
                "page": 1,
                "text": "The revenue increased by 15%",
                "confidence": 0.95
            }
        ]
        
        audit = AuditMode(provenance_chain)
        
        assert audit is not None
    
    def test_verify_claim_with_matching_source(self):
        """Test claim verification with matching source."""
        from src.utils.data_layer import AuditMode
        
        provenance_chain = [
            {
                "doc_id": "test-doc-1",
                "page": 1,
                "text": "The revenue increased by 15% in Q4",
                "confidence": 0.95
            }
        ]
        
        audit = AuditMode(provenance_chain)
        claim = audit.verify_claim("The revenue increased by 15%")
        
        assert claim is not None
    
    def test_verify_claim_without_matching_source(self):
        """Test claim verification without matching source."""
        from src.utils.data_layer import AuditMode
        
        provenance_chain = [
            {
                "doc_id": "test-doc-1",
                "page": 1,
                "text": "The revenue increased by 15%",
                "confidence": 0.95
            }
        ]
        
        audit = AuditMode(provenance_chain)
        claim = audit.verify_claim("The company filed for bankruptcy")
        
        assert claim is not None
    
    def test_create_audit_report(self):
        """Test audit report creation."""
        from src.utils.data_layer import AuditMode
        
        provenance_chain = [
            {
                "doc_id": "test-doc-1",
                "page": 1,
                "text": "The revenue increased by 15%",
                "confidence": 0.95
            }
        ]
        
        audit = AuditMode(provenance_chain)
        claims = ["The revenue increased by 15%", "Company filed bankruptcy"]
        
        report = audit.create_audit_report(claims)
        
        assert report is not None
        assert "claims" in report


class TestDataLayerIntegration:
    """Integration tests for data layer."""
    
    def test_full_pipeline(self):
        """Test full FactTable + VectorStore pipeline."""
        from src.utils.data_layer import FactTableExtractor, VectorStoreIngestion
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create FactTable
            db_path = os.path.join(tmpdir, "facts.db")
            fact_extractor = FactTableExtractor(db_path)
            
            # Create VectorStore
            vector_store = VectorStoreIngestion(
                backend="chroma",
                persist_directory=os.path.join(tmpdir, "vectors")
            )
            
            # Both should be created
            assert os.path.exists(db_path)
            assert vector_store is not None
