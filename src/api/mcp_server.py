"""MCP (Model Context Protocol) Server for Document Intelligence Refinery.

This module provides an MCP server that allows AI agents (like Claude, GPT-4)
to interact with the document processing pipeline.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP Tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPServer:
    """
    MCP Server for document processing.
    
    Provides tools for AI agents to:
    - Upload and process documents
    - Query extracted content
    - Get document metadata
    - Search by similarity
    """
    
    def __init__(self):
        """Initialize the MCP server."""
        self.tools = self._register_tools()
    
    def _register_tools(self) -> List[MCPTool]:
        """Register available MCP tools."""
        return [
            MCPTool(
                name="process_document",
                description="Upload and process a document with the refinery pipeline",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the document file"
                        },
                        "strategy": {
                            "type": "string",
                            "enum": ["auto", "fast", "layout", "vision"],
                            "description": "Extraction strategy to use"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            MCPTool(
                name="query_document",
                description="Query a processed document using natural language",
                input_schema={
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "Document ID to query"
                        },
                        "question": {
                            "type": "string",
                            "description": "Natural language question"
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["semantic_search", "pageindex_navigate", "structured_query"],
                            "description": "Query mode"
                        }
                    },
                    "required": ["doc_id", "question"]
                }
            ),
            MCPTool(
                name="get_document_profile",
                description="Get document profile information",
                input_schema={
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "Document ID"
                        }
                    },
                    "required": ["doc_id"]
                }
            ),
            MCPTool(
                name="get_extraction_result",
                description="Get full extraction results for a document",
                input_schema={
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "Document ID"
                        }
                    },
                    "required": ["doc_id"]
                }
            ),
            MCPTool(
                name="get_pageindex",
                description="Get hierarchical navigation index for a document",
                input_schema={
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "Document ID"
                        }
                    },
                    "required": ["doc_id"]
                }
            ),
            MCPTool(
                name="list_documents",
                description="List all processed documents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of documents to return"
                        }
                    }
                }
            ),
            MCPTool(
                name="search_content",
                description="Search for content across documents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results"
                        }
                    },
                    "required": ["query"]
                }
            ),
            MCPTool(
                name="verify_claim",
                description="Verify a claim against document sources",
                input_schema={
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "Document ID"
                        },
                        "claim": {
                            "type": "string",
                            "description": "Claim to verify"
                        }
                    },
                    "required": ["doc_id", "claim"]
                }
            ),
        ]
    
    def get_tools(self) -> List[MCPTool]:
        """Get all available tools."""
        return self.tools
    
    def get_tool_by_name(self, name: str) -> Optional[MCPTool]:
        """Get a specific tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool_by_name(tool_name)
        
        if tool is None:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        try:
            if tool_name == "process_document":
                return await self._tool_process_document(parameters)
            elif tool_name == "query_document":
                return await self._tool_query_document(parameters)
            elif tool_name == "get_document_profile":
                return await self._tool_get_document_profile(parameters)
            elif tool_name == "get_extraction_result":
                return await self._tool_get_extraction_result(parameters)
            elif tool_name == "get_pageindex":
                return await self._tool_get_pageindex(parameters)
            elif tool_name == "list_documents":
                return await self._tool_list_documents(parameters)
            elif tool_name == "search_content":
                return await self._tool_search_content(parameters)
            elif tool_name == "verify_claim":
                return await self._tool_verify_claim(parameters)
            else:
                return {"success": False, "error": f"Tool not implemented: {tool_name}"}
        
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _tool_process_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process a document."""
        from src.agents.triage import triage_document
        from src.agents.extractor import create_router
        from src.agents.chunker import Chunker
        
        file_path = params.get("file_path")
        strategy = params.get("strategy", "auto")
        
        # Triage
        profile = triage_document(file_path)
        
        # Extract
        router = create_router()
        extracted_doc = router.route(file_path, profile)
        
        # Chunk
        chunker = Chunker()
        ldu_set = chunker.chunk(extracted_doc, profile)
        
        return {
            "success": True,
            "doc_id": extracted_doc.doc_id,
            "profile": profile.model_dump(),
            "page_count": extracted_doc.page_count,
            "ldu_count": len(ldu_set.ldus)
        }
    
    async def _tool_query_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query a document."""
        # This would load the query agent and execute
        return {
            "success": True,
            "answer": "Query functionality requires loaded document",
            "sources": []
        }
    
    async def _tool_get_document_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get document profile."""
        return {
            "success": True,
            "profile": {}
        }
    
    async def _tool_get_extraction_result(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get extraction result."""
        return {
            "success": True,
            "result": {}
        }
    
    async def _tool_get_pageindex(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get page index."""
        return {
            "success": True,
            "index": {}
        }
    
    async def _tool_list_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List documents."""
        return {
            "success": True,
            "documents": []
        }
    
    async def _tool_search_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search content."""
        return {
            "success": True,
            "results": []
        }
    
    async def _tool_verify_claim(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a claim."""
        return {
            "success": True,
            "verified": False,
            "sources": []
        }


# Global MCP server instance
_mcp_server: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """Get the global MCP server instance."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server
