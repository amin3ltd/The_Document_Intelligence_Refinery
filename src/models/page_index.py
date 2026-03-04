"""PageIndex tree schema for hierarchical document navigation."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class NodeType(str, Enum):
    """Types of nodes in the PageIndex tree."""
    ROOT = "root"
    CHAPTER = "chapter"
    SECTION = "section"
    SUBSECTION = "subsection"
    PAGE = "page"
    TABLE = "table"
    FIGURE = "figure"
    LIST = "list"


class NavigationNode(BaseModel):
    """
    A node in the hierarchical navigation tree representing
    the document's structure for intelligent navigation.
    """
    node_id: str = Field(..., description="Unique identifier for this node")
    node_type: NodeType = Field(..., description="Type of this navigation node")
    title: str = Field(..., description="Display title for this node")
    level: int = Field(default=0, ge=0, description="Hierarchy level (0=root)")
    
    # Content references
    page_number: Optional[int] = Field(default=None, ge=1, description="Associated page number")
    ldu_ids: List[str] = Field(
        default_factory=list,
        description="LDU IDs contained in or associated with this node"
    )
    
    # Navigation
    parent_id: Optional[str] = Field(default=None, description="Parent node ID")
    children: List[str] = Field(
        default_factory=list,
        description="Child node IDs"
    )
    
    # Summary for LLM consumption
    summary: Optional[str] = Field(
        default=None,
        description="AI-generated summary of this section's content"
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="Key points extracted from this section"
    )
    
    # Metadata
    word_count: int = Field(default=0, description="Total word count in this subtree")
    has_tables: bool = Field(default=False, description="Whether this section contains tables")
    has_figures: bool = Field(default=False, description="Whether this section contains figures")
    
    # Position for sorting
    position: int = Field(default=0, description="Position/order index")
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True


class PageIndex(BaseModel):
    """
    PageIndex is a hierarchical navigation tree that provides
    intelligent navigation through long documents.
    
    It serves as the table of contents for LLM consumption,
    solving the "needle in haystack" problem for RAG systems.
    """
    doc_id: str = Field(..., description="Document ID this index belongs to")
    root_nodes: List[str] = Field(
        default_factory=list,
        description="Root level node IDs"
    )
    nodes: Dict[str, NavigationNode] = Field(
        default_factory=dict,
        description="All nodes in the tree, keyed by node_id"
    )
    
    # Statistics
    total_nodes: int = Field(default=0, description="Total number of nodes")
    depth: int = Field(default=0, description="Maximum depth of the tree")
    page_count: int = Field(default=0, description="Number of pages covered")
    
    # Index metadata
    index_version: str = Field(default="1.0", description="PageIndex schema version")
    created_at: str = Field(..., description="ISO timestamp of creation")
    updated_at: str = Field(..., description="ISO timestamp of last update")
    
    def add_node(
        self,
        node_id: str,
        node_type: NodeType,
        title: str,
        level: int,
        parent_id: Optional[str] = None,
        page_number: Optional[int] = None,
        position: int = 0
    ) -> NavigationNode:
        """Add a new node to the PageIndex tree."""
        node = NavigationNode(
            node_id=node_id,
            node_type=node_type,
            title=title,
            level=level,
            parent_id=parent_id,
            page_number=page_number,
            position=position
        )
        
        self.nodes[node_id] = node
        
        # Update parent if exists
        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id].children.append(node_id)
        elif node_type != NodeType.ROOT:
            # No parent means it's a root node
            if node_id not in self.root_nodes:
                self.root_nodes.append(node_id)
        
        # Update statistics
        self.total_nodes += 1
        if level > self.depth:
            self.depth = level
            
        return node
    
    def get_node(self, node_id: str) -> Optional[NavigationNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_children(self, node_id: str) -> List[NavigationNode]:
        """Get all direct children of a node."""
        node = self.nodes.get(node_id)
        if not node:
            return []
        return [self.nodes[cid] for cid in node.children if cid in self.nodes]
    
    def get_page_nodes(self, page_number: int) -> List[NavigationNode]:
        """Get all nodes associated with a specific page."""
        return [
            node for node in self.nodes.values()
            if node.page_number == page_number
        ]
    
    def get_path_to_node(self, node_id: str) -> List[NavigationNode]:
        """Get the path from root to a specific node."""
        path = []
        current_id = node_id
        
        while current_id and current_id in self.nodes:
            node = self.nodes[current_id]
            path.insert(0, node)
            current_id = node.parent_id
            
        return path
    
    def to_outline(self) -> str:
        """Generate a text outline representation of the index."""
        lines = []
        
        def render_node(node_id: str, indent: int = 0):
            node = self.nodes.get(node_id)
            if not node:
                return
                
            prefix = "  " * indent
            page_info = f" (p.{node.page_number})" if node.page_number else ""
            lines.append(f"{prefix}- {node.title}{page_info}")
            
            for child_id in node.children:
                render_node(child_id, indent + 1)
        
        for root_id in self.root_nodes:
            render_node(root_id)
            
        return "\n".join(lines)
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "doc_id": "doc_001",
                "root_nodes": ["chapter_1", "chapter_2"],
                "nodes": {
                    "chapter_1": {
                        "node_id": "chapter_1",
                        "node_type": "chapter",
                        "title": "Executive Summary",
                        "level": 1,
                        "page_number": 1,
                        "children": ["section_1_1"],
                        "word_count": 1500
                    }
                },
                "total_nodes": 15,
                "depth": 3,
                "page_count": 42
            }
        }
