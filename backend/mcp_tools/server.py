from mcp import server, types
from .db_operations import add_task_db, list_tasks_db, complete_task_db, delete_task_db, update_task_db
from pydantic import BaseModel
from typing import List, Optional
import asyncio


class AddTaskResult(BaseModel):
    task_id: int
    status: str
    title: str


class TaskInfo(BaseModel):
    task_id: int
    status: str
    title: str


class TaskListResult(BaseModel):
    tasks: List[TaskInfo]


class TaskOperationResult(BaseModel):
    task_id: int
    status: str
    title: str


async def create_server():
    """Create and configure the MCP server"""
    s = server.Server("todo-mcp-server")
    
    @s.after_listen
    async def gather_prompts(context: server.Context) -> None:
        """Register tools after server starts listening"""
        await context.request(
            types.InitializeRequest(
                protocol_version="2.0",
                capabilities=types.ServerCapabilities(
                    tools=types.ToolCapabilities(list_changed=True)
                )
            )
        )
        
        # Register all tools
        await context.request(
            types.TextContent(
                role="system",
                content="Registered todo management tools"
            )
        )
    
    @s.collect_tools
    async def handle_collect_tools(context) -> types.CollectToolsResult:
        """Collect available tools"""
        tools = [
            types.Tool(
                name="add_task",
                description="Creates a new task for a user",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user creating the task"},
                        "title": {"type": "string", "description": "Title of the task"},
                        "description": {"type": "string", "description": "Description of the task"}
                    },
                    "required": ["user_id", "title"]
                }
            ),
            types.Tool(
                name="list_tasks",
                description="Lists tasks for a user",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user whose tasks to list"},
                        "status": {"type": "string", "description": "Filter by status (all, active, completed)"}
                    },
                    "required": ["user_id"]
                }
            ),
            types.Tool(
                name="complete_task",
                description="Marks a task as completed",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user"},
                        "task_id": {"type": "integer", "description": "ID of the task to complete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            ),
            types.Tool(
                name="delete_task",
                description="Deletes a task",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user"},
                        "task_id": {"type": "integer", "description": "ID of the task to delete"}
                    },
                    "required": ["user_id", "task_id"]
                }
            ),
            types.Tool(
                name="update_task",
                description="Updates task details",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user"},
                        "task_id": {"type": "integer", "description": "ID of the task to update"},
                        "title": {"type": "string", "description": "New title for the task"},
                        "description": {"type": "string", "description": "New description for the task"}
                    },
                    "required": ["user_id", "task_id"]
                }
            )
        ]
        return types.CollectToolsResult(tools=tools)
    
    @s.call_tool
    async def handle_call_tool(request: types.CallToolRequest, context: server.Context) -> types.CallToolResult:
        """Handle tool calls"""
        tool_name = request.name
        arguments = request.arguments or {}
        
        try:
            if tool_name == "add_task":
                result = await add_task_db(
                    user_id=arguments["user_id"],
                    title=arguments["title"],
                    description=arguments.get("description")
                )
                return types.CallToolResult(content=[
                    types.TextContent(
                        role="assistant",
                        content=f"Added task with ID: {result.task_id}"
                    )
                ], tool_result=AddTaskResult(
                    task_id=result.task_id,
                    status=result.status,
                    title=result.title
                ))
            
            elif tool_name == "list_tasks":
                results = await list_tasks_db(
                    user_id=arguments["user_id"],
                    status=arguments.get("status")
                )
                return types.CallToolResult(content=[
                    types.TextContent(
                        role="assistant",
                        content=f"Found {len(results)} tasks"
                    )
                ], tool_result=TaskListResult(tasks=results))
                
            elif tool_name == "complete_task":
                result = await complete_task_db(
                    user_id=arguments["user_id"],
                    task_id=arguments["task_id"]
                )
                return types.CallToolResult(content=[
                    types.TextContent(
                        role="assistant",
                        content=f"Completed task with ID: {result.task_id}"
                    )
                ], tool_result=TaskOperationResult(
                    task_id=result.task_id,
                    status=result.status,
                    title=result.title
                ))
                
            elif tool_name == "delete_task":
                result = await delete_task_db(
                    user_id=arguments["user_id"],
                    task_id=arguments["task_id"]
                )
                return types.CallToolResult(content=[
                    types.TextContent(
                        role="assistant",
                        content=f"Deleted task with ID: {result.task_id}"
                    )
                ], tool_result=TaskOperationResult(
                    task_id=result.task_id,
                    status=result.status,
                    title=result.title
                ))
                
            elif tool_name == "update_task":
                result = await update_task_db(
                    user_id=arguments["user_id"],
                    task_id=arguments["task_id"],
                    title=arguments.get("title"),
                    description=arguments.get("description")
                )
                return types.CallToolResult(content=[
                    types.TextContent(
                        role="assistant",
                        content=f"Updated task with ID: {result.task_id}"
                    )
                ], tool_result=TaskOperationResult(
                    task_id=result.task_id,
                    status=result.status,
                    title=result.title
                ))
                
            else:
                return types.CallToolResult(
                    content=[
                        types.TextContent(
                            role="error",
                            content=f"Unknown tool: {tool_name}"
                        )
                    ],
                    is_error=True
                )
        except Exception as e:
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        role="error",
                        content=f"Error executing tool {tool_name}: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    return s