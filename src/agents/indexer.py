"""
PageIndex Builder Agent for Document Intelligence Refinery.

The Indexer builds a hierarchical navigation tree from LDUs
for intelligent document navigation.
Includes LLM-generated section summaries.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable

from src.models.document_profile import DocumentProfile
from src.models.ldu import LDU, LDUSet
from src.models.page_index import NavigationNode, NodeType, PageIndex

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """
    Generates LLM-powered summaries for document sections.
    
    Uses a configurable LLM to create concise summaries
    that enable efficient navigation and question answering.
    """
    
    def __init__(self, llm_provider: Optional[Callable] = None):
        """
        Initialize the summary generator.
        
        Args:
            llm_provider: Optional callable that takes text and returns summary
        """
        self.llm_provider = llm_provider
    
    def generate_section_summary(self, section_ldus: List[LDU]) -> str:
        """
        Generate a summary for a section of LDUs.
        
        Args:
            section_ldus: List of LDUs in the section
            
        Returns:
            Summary text
        """
        if not section_ldus:
            return ""
        
        # Combine content from all LDUs
        combined_text = " ".join(ldu.content for ldu in section_ldus[:10])  # Limit to first 10
        
        if self.llm_provider:
            try:
                return self.llm_provider(combined_text)
            except Exception as e:
                logger.warning(f"LLM summary generation failed: {e}")
        
        # Fallback: simple extractive summary
        return self._extractive_summary(combined_text)
    
    def generate_page_summary(self, page_ldus: List[LDU]) -> str:
        """
        Generate a summary for a page.
        
        Args:
            page_ldus: List of LDUs on the page
            
        Returns:
            Summary text
        """
        if not page_ldus:
            return ""
        
        # Take first paragraph as summary
        for ldu in page_ldus:
            if ldu.chunk_type.value == "paragraph":
                return ldu.content[:200] + "..." if len(ldu.content) > 200 else ldu.content
        
        return page_ldus[0].content[:200]
    
    def _extractive_summary(self, text: str, max_length: int = 200) -> str:
        """
        Create a simple extractive summary.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length
            
        Returns:
            Summary text
        """
        # Take first sentences
        sentences = text.split(". ")
        summary = ""
        for sentence in sentences[:3]:
            if len(summary) + len(sentence) <= max_length:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip() or text[:max_length] + "..."


class Indexer:
    """
    Builds hierarchical PageIndex trees from LDUs.
    
    The PageIndex provides intelligent navigation through long documents,
    solving the "needle in haystack" problem for RAG systems.
    Includes LLM-generated section summaries.
    """
    
    def __init__(
        self,
        output_dir: str = ".refinery/pageindex",
        llm_provider: Optional[Callable] = None
    ):
        """
        Initialize the indexer.
        
        Args:
            output_dir: Directory to save PageIndex outputs
            llm_provider: Optional callable for LLM summarization
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.summary_generator = SummaryGenerator(llm_provider)
    
    def build_index(
        self,
        ldu_set: LDUSet,
        profile: DocumentProfile,
    ) -> PageIndex:
        """
        Build a PageIndex from LDUs.
        
        Args:
            ldu_set: The LDU set from chunking
            profile: Document profile for context
            
        Returns:
            PageIndex hierarchical navigation tree
        """
        logger.info(f"Building PageIndex for document {ldu_set.doc_id}")
        
        # Initialize the index
        index = PageIndex(
            doc_id=ldu_set.doc_id,
            page_count=profile.page_count,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )
        
        # Group LDUs by page and section
        page_nodes: Dict[int, List[LDU]] = {}
        sections: Dict[str, List[LDU]] = {}
        
        for ldu in ldu_set.ldus:
            page_num = ldu.page_number
            if page_num not in page_nodes:
                page_nodes[page_num] = []
            page_nodes[page_num].append(ldu)
            
            # Track sections
            if ldu.parent_section:
                if ldu.parent_section not in sections:
                    sections[ldu.parent_section] = []
                sections[ldu.parent_section].append(ldu)
        
        # Build section hierarchy from LDU section paths
        section_tree = self._build_section_tree(ldu_set.ldus)
        
        # Create navigation nodes for sections
        node_counter = 0
        for section_path, section_ldus in section_tree.items():
            parent_id = None
            
            # Generate section summary
            section_summary = self.summary_generator.generate_section_summary(section_ldus)
            
            # Create nodes for each level in the path
            for level, section_name in enumerate(section_path):
                node_id = f"node_{node_counter:04d}"
                node_counter += 1
                
                # Determine node type based on level
                if level == 0:
                    node_type = NodeType.CHAPTER
                elif level == 1:
                    node_type = NodeType.SECTION
                else:
                    node_type = NodeType.SUBSECTION
                
                # Get page number from first LDU in section
                page_num = section_ldus[0].page_number if section_ldus else None
                
                # Add node to index
                index.add_node(
                    node_id=node_id,
                    node_type=node_type,
                    title=section_name,
                    level=level + 1,
                    parent_id=parent_id,
                    page_number=page_num,
                    position=level,
                )
                
                parent_id = node_id
        
        # Add page-level nodes
        for page_num in sorted(page_nodes.keys()):
            page_ldus = page_nodes[page_num]
            
            # Skip if already added as part of section
            page_texts = [ldu.content for ldu in page_ldus if ldu.chunk_type == "paragraph"]
            if not page_texts:
                continue
            
            # Generate page summary
            page_summary = self.summary_generator.generate_page_summary(page_ldus)
            
            node_id = f"page_{page_num}"
            index.add_node(
                node_id=node_id,
                node_type=NodeType.PAGE,
                title=f"Page {page_num}",
                level=len(section_tree) + 1 if section_tree else 1,
                page_number=page_num,
                position=page_num,
                summary=page_summary,
            )
        
        # Add table and figure nodes
        tables = [ldu for ldu in ldu_set.ldus if ldu.chunk_type == "table"]
        figures = [ldu for ldu in ldu_set.ldus if ldu.chunk_type == "figure_caption"]
        
        for i, table_ldu in enumerate(tables):
            node_id = f"table_{i}"
            index.add_node(
                node_id=node_id,
                node_type=NodeType.TABLE,
                title=f"Table {i + 1}",
                level=index.depth + 1,
                page_number=table_ldu.page_number,
                position=i,
            )
        
        for i, fig_ldu in enumerate(figures):
            node_id = f"figure_{i}"
            index.add_node(
                node_id=node_id,
                node_type=NodeType.FIGURE,
                title=f"Figure {i + 1}",
                level=index.depth + 1,
                page_number=fig_ldu.page_number,
                position=i,
            )
        
        # Save the index
        self._save_index(index)
        
        logger.info(f"Built PageIndex with {index.total_nodes} nodes, depth {index.depth}")
        
        return index
    
    def _build_section_tree(self, ldus: List[LDU]) -> Dict[tuple, List[LDU]]:
        """Build a tree of sections from LDU section paths."""
        section_tree: Dict[tuple, List[LDU]] = {}
        
        for ldu in ldus:
            if ldu.section_path:
                path_tuple = tuple(ldu.section_path)
                if path_tuple not in section_tree:
                    section_tree[path_tuple] = []
                section_tree[path_tuple].append(ldu)
        
        return section_tree
    
    def _save_index(self, index: PageIndex) -> None:
        """Save the index to a JSON file."""
        output_path = self.output_dir / f"{index.doc_id}_index.json"
        with open(output_path, "w") as f:
            json.dump(index.model_dump(mode="json"), f, indent=2)
        logger.info(f"PageIndex saved to: {output_path}")


def build_pageindex(
    ldu_set: LDUSet,
    profile: DocumentProfile,
    output_dir: str = ".refinery/pageindex",
) -> PageIndex:
    """
    Convenience function to build a PageIndex.
    
    Args:
        ldu_set: The LDU set
        profile: Document profile
        output_dir: Output directory
        
    Returns:
        PageIndex hierarchical navigation tree
    """
    indexer = Indexer(output_dir)
    return indexer.build_index(ldu_set, profile)
