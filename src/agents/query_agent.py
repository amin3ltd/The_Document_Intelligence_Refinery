"""
Query Interface Agent for Document Intelligence Refinery.

The Query Agent provides natural language interfaces for querying
extracted document content with provenance tracking using LangGraph.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from src.models.document_profile import DocumentProfile
from src.models.ldu import LDU, LDUSet
from src.models.page_index import PageIndex
from src.models.provenance import Claim, ProvenanceChain, ProvenanceSource

logger = logging.getLogger(__name__)


# Define the state for the query agent
class QueryAgentState(dict):
    """State container for the query agent."""
    question: str
    mode: str
    answer: str
    sources: List[ProvenanceSource]
    confidence: float
    page_refs: List[int]
    tool_used: str


class QueryResult:
    """Result of a query with provenance information."""
    
    def __init__(
        self,
        answer: str,
        sources: List[ProvenanceSource],
        confidence: float,
        page_refs: List[int],
    ):
        self.answer = answer
        self.sources = sources
        self.confidence = confidence
        self.page_refs = page_refs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "answer": self.answer,
            "sources": [
                {
                    "document": s.location.document_name,
                    "page": s.location.page_number,
                    "bbox": s.location.bbox,
                    "text": s.content.text,
                }
                for s in self.sources
            ],
            "confidence": self.confidence,
            "page_refs": self.page_refs,
        }


class QueryAgent:
    """
    Query interface agent for querying document content using LangGraph.
    
    Provides multiple query modes via LangGraph tools:
    - pageindex_navigate: Navigate by document structure
    - semantic_search: Search by semantic similarity
    - structured_query: Query with structured filters
    """
    
    def __init__(
        self,
        ldu_set: LDUSet,
        page_index: PageIndex,
        provenance_chain: Optional[ProvenanceChain] = None,
    ):
        """
        Initialize the query agent.
        
        Args:
            ldu_set: The LDU set from chunking
            page_index: The PageIndex for navigation
            provenance_chain: Optional provenance chain for verification
        """
        self.ldu_set = ldu_set
        self.page_index = page_index
        self.provenance_chain = provenance_chain or ProvenanceChain(
            chain_id=f"prov_{ldu_set.doc_id}",
            doc_id=ldu_set.doc_id,
        )
        
        # Build the LangGraph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow with 3 tools."""
        workflow = StateGraph(QueryAgentState)
        
        # Add nodes for each tool
        workflow.add_node("pageindex_navigate", self._tool_pageindex_navigate)
        workflow.add_node("semantic_search", self._tool_semantic_search)
        workflow.add_node("structured_query", self._tool_structured_query)
        workflow.add_node("format_response", self._format_response)
        
        # Add routing node
        workflow.add_node("route", self._route_question)
        
        # Define edges - router decides which tool to use
        workflow.add_edge("__start__", "route")
        workflow.add_conditional_edges(
            "route",
            lambda x: x,
            {
                "pageindex_navigate": "pageindex_navigate",
                "semantic_search": "semantic_search",
                "structured_query": "structured_query",
            }
        )
        
        # All tools lead to format_response
        workflow.add_edge("pageindex_navigate", "format_response")
        workflow.add_edge("semantic_search", "format_response")
        workflow.add_edge("structured_query", "format_response")
        workflow.add_edge("format_response", "__end__")
        
        return workflow.compile()
    
    def _route_question(self, state: QueryAgentState) -> str:
        """Route the question to the appropriate tool based on its content."""
        import re
        
        question = state.get("question", "").lower()
        
        # Check for explicit mode specification
        if "page" in question and re.search(r"\d+", question):
            return "pageindex_navigate"
        if "section" in question or "chapter" in question:
            return "pageindex_navigate"
        if any(keyword in question for keyword in ["find", "search", "what is", "explain"]):
            return "semantic_search"
        if any(keyword in question for keyword in ["filter", "where", "list all"]):
            return "structured_query"
        
        # Default to semantic search
        return "semantic_search"
    
    def _tool_pageindex_navigate(self, state: QueryAgentState) -> QueryAgentState:
        """Tool: Navigate by document structure (PageIndex)."""
        import re
        
        question = state.get("question", "")
        
        # Extract section/page references from question
        page_match = re.search(r"page\s+(\d+)", question, re.IGNORECASE)
        section_match = re.search(r"(?:section|chapter)\s+(\d+\.?\d*)", question, re.IGNORECASE)
        
        if page_match:
            page_num = int(page_match.group(1))
            nodes = self.page_index.get_page_nodes(page_num)
            
            # Gather content from that page
            page_ldus = self.ldu_set.get_by_page(page_num)
            content = " ".join(ldu.content for ldu in page_ldus[:5])
            
            sources = self._create_sources_from_ldus(page_ldus[:5])
            
            state["answer"] = content
            state["sources"] = sources
            state["confidence"] = 0.9
            state["page_refs"] = [page_num]
            state["tool_used"] = "pageindex_navigate"
        
        elif section_match:
            section_num = section_match.group(1)
            # Find section in page index
            for node in self.page_index.nodes.values():
                if section_num in node.title:
                    if node.page_number:
                        page_ldus = self.ldu_set.get_by_page(node.page_number)
                        content = " ".join(ldu.content for ldu in page_ldus[:5])
                        sources = self._create_sources_from_ldus(page_ldus[:5])
                        
                        state["answer"] = content
                        state["sources"] = sources
                        state["confidence"] = 0.85
                        state["page_refs"] = [node.page_number]
                        state["tool_used"] = "pageindex_navigate"
                        break
        
        # Default to semantic search if no match
        if "answer" not in state:
            return self._tool_semantic_search(state)
        
        return state
    
    def _tool_semantic_search(self, state: QueryAgentState) -> QueryAgentState:
        """Tool: Semantic search using keyword overlap scoring."""
        question = state.get("question", "")
        question_lower = question.lower()
        
        # Find relevant LDUs based on keyword matching
        relevant_ldus: List[LDU] = []
        
        for ldu in self.ldu_set.ldus:
            # Score by keyword overlap
            ldu_words = set(ldu.content.lower().split())
            question_words = set(question_lower.split())
            
            overlap = len(ldu_words & question_words)
            if overlap > 0:
                relevant_ldus.append(ldu)
        
        # Sort by relevance (word overlap)
        relevant_ldus.sort(
            key=lambda l: len(set(l.content.lower().split()) & set(question_lower.split())),
            reverse=True,
        )
        
        # Take top results
        top_ldus = relevant_ldus[:5]
        
        if not top_ldus:
            state["answer"] = "No relevant content found."
            state["sources"] = []
            state["confidence"] = 0.0
            state["page_refs"] = []
            state["tool_used"] = "semantic_search"
            return state
        
        # Combine content
        answer = " ".join(ldu.content for ldu in top_ldus)
        
        # Create sources
        sources = self._create_sources_from_ldus(top_ldus)
        page_refs = list(set(ldu.page_number for ldu in top_ldus))
        
        state["answer"] = answer[:1000]  # Limit answer length
        state["sources"] = sources
        state["confidence"] = 0.75
        state["page_refs"] = page_refs
        state["tool_used"] = "semantic_search"
        
        return state
    
    def _tool_structured_query(self, state: QueryAgentState) -> QueryAgentState:
        """Tool: Structured query with filters."""
        # For now, delegate to semantic search with filter logic
        # In production, this would support SQL-like queries
        return self._tool_semantic_search(state)
    
    def _format_response(self, state: QueryAgentState) -> QueryAgentState:
        """Format the final response."""
        return state
    
    def query(self, question: str, mode: str = "semantic_search") -> QueryResult:
        """
        Query the document with a natural language question using LangGraph.
        
        Args:
            question: The question to answer
            mode: Query mode (pageindex_navigate, semantic_search, structured_query)
            
        Returns:
            QueryResult with answer and provenance
        """
        # Initialize state
        initial_state = QueryAgentState(
            question=question,
            mode=mode,
            answer="",
            sources=[],
            confidence=0.0,
            page_refs=[],
            tool_used=""
        )
        
        # Route to appropriate tool based on mode
        if mode == "pageindex_navigate":
            result_state = self._tool_pageindex_navigate(initial_state)
        elif mode == "semantic_search":
            result_state = self._tool_semantic_search(initial_state)
        elif mode == "structured_query":
            result_state = self._tool_structured_query(initial_state)
        else:
            # Use LangGraph to route automatically
            result_state = self._route_and_execute(initial_state)
        
        return QueryResult(
            answer=result_state.get("answer", ""),
            sources=result_state.get("sources", []),
            confidence=result_state.get("confidence", 0.0),
            page_refs=result_state.get("page_refs", []),
        )
    
    def _route_and_execute(self, state: QueryAgentState) -> QueryAgentState:
        """Use LangGraph to route and execute the query."""
        tool = self._route_question(state)
        
        if tool == "pageindex_navigate":
            return self._tool_pageindex_navigate(state)
        elif tool == "semantic_search":
            return self._tool_semantic_search(state)
        elif tool == "structured_query":
            return self._tool_structured_query(state)
        
        return self._tool_semantic_search(state)
    
    def _create_sources_from_ldus(self, ldus: List[LDU]) -> List[ProvenanceSource]:
        """Create ProvenanceSource objects from LDUs."""
        sources = []
        
        for ldu in ldus:
            source = ProvenanceSource(
                location={
                    "document_name": Path(self.ldu_set.doc_id).name,
                    "document_path": "",
                    "page_number": ldu.page_number,
                    "bbox": ldu.bbox,
                },
                content={
                    "text": ldu.content,
                    "text_hash": ldu.content_hash,
                    "extraction_method": "semantic_chunking",
                },
                document_id=self.ldu_set.doc_id,
                page_id=f"page_{ldu.page_number}",
            )
            sources.append(source)
        
        return sources
    
    def verify_claim(self, claim_text: str) -> bool:
        """
        Verify a claim against the provenance chain.
        
        Args:
            claim_text: The claim to verify
            
        Returns:
            True if the claim can be verified
        """
        # Simple verification: check if claim keywords appear in sources
        claim_words = set(claim_text.lower().split())
        
        for claim in self.provenance_chain.claims:
            for source in claim.sources:
                source_words = set(source.content.text.lower().split())
                if claim_words & source_words:
                    return True
        
        return False


def create_query_agent(
    doc_id: str,
    ldu_file: str,
    index_file: str,
) -> QueryAgent:
    """
    Create a QueryAgent from saved files.
    
    Args:
        doc_id: Document ID
        ldu_file: Path to LDU JSON file
        index_file: Path to PageIndex JSON file
        
    Returns:
        QueryAgent instance
    """
    # Load LDUs
    with open(ldu_file) as f:
        ldu_data = json.load(f)
    
    # Handle various JSON formats
    if isinstance(ldu_data, list):
        # JSON is a list of LDU dicts - convert directly
        ldus = [LDU(**ldu_dict) for ldu_dict in ldu_data]
        ldu_set = LDUSet(
            doc_id=doc_id,
            ldus=ldus,
            chunking_strategy="unknown",
            processing_time_ms=0,
        )
    elif "ldus" in ldu_data and isinstance(ldu_data.get("ldus"), list):
        # JSON has dict with "ldus" key - convert to LDU objects
        ldus = [LDU(**ldu_dict) for ldu_dict in ldu_data["ldus"]]
        ldu_set = LDUSet(
            doc_id=ldu_data["doc_id"],
            ldus=ldus,
            chunking_strategy=ldu_data.get("chunking_strategy", "unknown"),
            processing_time_ms=ldu_data.get("processing_time_ms", 0),
            content_hash=ldu_data.get("content_hash"),
        )
    else:
        # Try as full LDUSet format
        ldu_set = LDUSet(**ldu_data)
    
    # Load PageIndex
    with open(index_file) as f:
        index_data = json.load(f)
    page_index = PageIndex(**index_data)
    
    return QueryAgent(ldu_set, page_index)
