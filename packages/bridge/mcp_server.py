"""
MCP Server Integration for Aura Sphere

This module provides MCP (Model Context Protocol) tools that expose
the agent's capabilities to AI models like Claude.
"""

import logging
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import (
    TextContent,
    Tool,
    ListToolsResult,
    CallToolRequest,
    CallToolResult,
)

from agent import get_agent_service
from llm_service import get_llm_service
from embedding_service import get_embedding_service
from mempalace.memory import MemoryEngine

logger = logging.getLogger(__name__)

# Initialize services
agent_service = get_agent_service()
llm_service = get_llm_service()
embedding_service = get_embedding_service()
memory_engine = MemoryEngine()

# Create MCP Server
server = Server("aura-sphere-mcp")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="agent_session_report",
            description="Get the current agent session report including active tasks and status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="agent_add_task",
            description="Add a new task to the agent session",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description of the task to add"
                    }
                },
                "required": ["description"]
            }
        ),
        Tool(
            name="agent_complete_task",
            description="Mark an agent task as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of the task to complete"
                    },
                    "details": {
                        "type": "string",
                        "description": "Optional completion details"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="agent_sandbox_execute",
            description="Execute code in a sandboxed environment",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    },
                    "inputs": {
                        "type": "object",
                        "description": "Input variables for the code"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID for the execution"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="memory_search",
            description="Search user memory using semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to search memory for"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["user_id", "query"]
            }
        ),
        Tool(
            name="memory_add",
            description="Add new content to user memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to add to memory"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category for the memory entry",
                        "default": "general"
                    }
                },
                "required": ["user_id", "content"]
            }
        ),
        Tool(
            name="llm_chat",
            description="Send a chat message to the LLM and get response",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "description": "List of chat messages",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {"type": "string", "enum": ["user", "assistant", "system"]},
                                "content": {"type": "string"}
                            },
                            "required": ["role", "content"]
                        }
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "System prompt for the conversation"
                    },
                    "ai_name": {
                        "type": "string",
                        "description": "Name of the AI assistant",
                        "default": "Aurora"
                    }
                },
                "required": ["messages"]
            }
        ),
        Tool(
            name="embedding_search",
            description="Search for similar content using embeddings",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "candidates": {
                        "type": "array",
                        "description": "List of candidate texts to search in",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "text": {"type": "string"}
                            },
                            "required": ["id", "text"]
                        }
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of top results to return",
                        "default": 5
                    }
                },
                "required": ["query", "candidates"]
            }
        )
    ]


@server.call_tool()
async def call_tool(request: CallToolRequest) -> List[TextContent]:
    """Execute the requested MCP tool."""
    tool_name = request.params.name
    arguments = request.params.arguments or {}

    logger.info(f"Executing MCP tool: {tool_name} with args: {arguments}")

    try:
        if tool_name == "agent_session_report":
            report = agent_service.get_session_report()
            return [TextContent(type="text", text=str(report))]

        elif tool_name == "agent_add_task":
            description = arguments.get("description", "")
            if not description:
                return [TextContent(type="text", text="Error: description is required")]
            task = agent_service.add_session_task(description)
            return [TextContent(type="text", text=f"Task added: {task.id} - {task.description}")]

        elif tool_name == "agent_complete_task":
            task_id = arguments.get("task_id", "")
            details = arguments.get("details")
            if not task_id:
                return [TextContent(type="text", text="Error: task_id is required")]
            success = agent_service.complete_session_task(task_id, details)
            if success:
                return [TextContent(type="text", text=f"Task {task_id} completed successfully")]
            else:
                return [TextContent(type="text", text=f"Task {task_id} not found")]

        elif tool_name == "agent_sandbox_execute":
            code = arguments.get("code", "")
            inputs = arguments.get("inputs", {})
            user_id = arguments.get("user_id", "mcp-user")
            if not code:
                return [TextContent(type="text", text="Error: code is required")]
            result = agent_service.run_code_in_sandbox(code=code, inputs=inputs, user_id=user_id)
            return [TextContent(type="text", text=str(result))]

        elif tool_name == "memory_search":
            user_id = arguments.get("user_id", "")
            query = arguments.get("query", "")
            limit = arguments.get("limit", 10)
            if not user_id or not query:
                return [TextContent(type="text", text="Error: user_id and query are required")]

            # Perform semantic search
            with SessionLocal() as session:
                memory_items = (
                    session.query(MemoryEntry)
                    .filter(MemoryEntry.user_id == user_id)
                    .order_by(MemoryEntry.created_at.desc())
                    .all()
                )

                if not memory_items:
                    return [TextContent(type="text", text="No memory items found")]

                candidates = [
                    (str(item.id), embedding_service.embed_text(item.content), item.content)
                    for item in memory_items
                ]

                search_results = embedding_service.search_similar(query, candidates, top_k=limit)

                results = []
                for result in search_results:
                    item = next(i for i in memory_items if str(i.id) == result["id"])
                    results.append(f"ID: {item.id}, Content: {item.content}, Category: {item.category}")

                return [TextContent(type="text", text="\n".join(results))]

        elif tool_name == "memory_add":
            user_id = arguments.get("user_id", "")
            content = arguments.get("content", "")
            category = arguments.get("category", "general")
            if not user_id or not content:
                return [TextContent(type="text", text="Error: user_id and content are required")]

            memory_engine.add_memory(user_id, content, category=category)
            return [TextContent(type="text", text="Memory added successfully")]

        elif tool_name == "llm_chat":
            messages = arguments.get("messages", [])
            system_prompt = arguments.get("system_prompt")
            ai_name = arguments.get("ai_name", "Aurora")

            if not messages:
                return [TextContent(type="text", text="Error: messages are required")]

            # Convert messages format
            formatted_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]

            # Get response
            full_response = ""
            async for chunk in llm_service.stream_chat_completion(
                formatted_messages,
                system_prompt=system_prompt
            ):
                full_response += chunk

            return [TextContent(type="text", text=full_response)]

        elif tool_name == "embedding_search":
            query = arguments.get("query", "")
            candidates = arguments.get("candidates", [])
            top_k = arguments.get("top_k", 5)

            if not query or not candidates:
                return [TextContent(type="text", text="Error: query and candidates are required")]

            # Prepare candidates for search
            search_candidates = [
                (str(i), embedding_service.embed_text(cand["text"]), cand["text"])
                for i, cand in enumerate(candidates)
            ]

            results = embedding_service.search_similar(query, search_candidates, top_k=top_k)

            output = []
            for result in results:
                idx = int(result["id"])
                cand = candidates[idx]
                output.append(f"ID: {cand['id']}, Text: {cand['text']}, Score: {result['score']}")

            return [TextContent(type="text", text="\n".join(output))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {tool_name}")]

    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# Import here to avoid circular imports
from database import SessionLocal, MemoryEntry