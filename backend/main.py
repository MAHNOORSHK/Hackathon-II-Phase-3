from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from .database import create_db_and_tables
from .models import Task, Conversation, Message
from .ai_agent import TodoAssistant
import asyncio
import uvicorn
import os


# Global instance of the AI assistant
todo_assistant = TodoAssistant()


app = FastAPI(title="Todo AI Chatbot API", version="1.0.0")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables and AI assistant on startup"""
    create_db_and_tables()
    await todo_assistant.initialize()


# Pydantic models for request/response
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: str
    updated_at: str


class MessageCreate(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: int


@app.post("/api/{user_id}/chat")
async def chat_endpoint(user_id: str, request: ChatRequest):
    """
    Main chat endpoint that handles conversation with the AI agent
    """
    # Process the message with the AI agent
    result = await todo_assistant.process_message(
        user_id=user_id,
        message=request.message,
        conversation_id=request.conversation_id
    )
    
    return result


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Todo AI Chatbot API is running!"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Placeholder for starting the MCP server
async def start_mcp_server():
    """Start the MCP server in the background"""
    server = await create_server()
    # Note: Actual server startup would happen here
    print("MCP Server initialized")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)