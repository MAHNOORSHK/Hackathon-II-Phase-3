# Hackathon-Todo Phase III AI Chatbot Specification

## Project Overview
Multi-user Todo AI Chatbot with natural language management capabilities. The system allows users to manage their tasks through conversational interface using natural language commands.

## Architecture Overview
- **Frontend**: OpenAI ChatKit (conversational UI)
- **Backend**: Python FastAPI
- **AI Logic**: OpenAI Agents SDK (agent + runner for processing)
- **MCP Server**: Official MCP SDK (exposing task operations as tools)
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT

## Technical Stack
- Python 3.11+
- FastAPI
- SQLModel
- Neon PostgreSQL
- Better Auth
- OpenAI Agents SDK
- MCP SDK
- OpenAI ChatKit (frontend)

## Database Models

### Task Model
```python
class Task(SQLModel, table=True):
    user_id: str = Field(index=True)
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Conversation Model
```python
class Conversation(SQLModel, table=True):
    user_id: str = Field(index=True)
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Message Model
```python
class Message(SQLModel, table=True):
    user_id: str = Field(index=True)
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str = Field(regex="^(user|assistant)$")  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## MCP Tools Specification

### 1. add_task
- **Description**: Creates a new task for a user
- **Parameters**:
  - `user_id` (str, required): ID of the user creating the task
  - `title` (str, required): Title of the task
  - `description` (str, optional): Description of the task
- **Returns**: Object with `task_id`, `status`, `title`

### 2. list_tasks
- **Description**: Lists tasks for a user
- **Parameters**:
  - `user_id` (str, required): ID of the user whose tasks to list
  - `status` (str, optional): Filter by status ("all", "active", "completed")
- **Returns**: Array of task objects with `task_id`, `status`, `title`

### 3. complete_task
- **Description**: Marks a task as completed
- **Parameters**:
  - `user_id` (str, required): ID of the user
  - `task_id` (int, required): ID of the task to complete
- **Returns**: Object with `task_id`, `status`, `title`

### 4. delete_task
- **Description**: Deletes a task
- **Parameters**:
  - `user_id` (str, required): ID of the user
  - `task_id` (int, required): ID of the task to delete
- **Returns**: Object with `task_id`, `status`, `title`

### 5. update_task
- **Description**: Updates task details
- **Parameters**:
  - `user_id` (str, required): ID of the user
  - `task_id` (int, required): ID of the task to update
  - `title` (str, optional): New title for the task
  - `description` (str, optional): New description for the task
- **Returns**: Object with `task_id`, `status`, `title`

## API Endpoints

### Chat Endpoint
- **Route**: `/api/{user_id}/chat`
- **Method**: POST
- **Description**: Main chat endpoint that handles conversation with the AI agent
- **Request Body**: Contains user message and conversation context
- **Response**: AI-generated response with potential tool invocations
- **Authentication**: JWT token verification via Better Auth

## Agent Behavior Requirements

### Natural Language Processing
- Parse natural language commands for task management
- Recognize intent for add/list/complete/delete/update operations
- Handle variations in user phrasing
- Provide helpful error messages for unrecognized commands

### Tool Invocation
- Map natural language to appropriate MCP tools
- Validate parameters before tool invocation
- Handle tool execution results appropriately
- Format responses back to user in natural language

### Error Handling
- Graceful handling of invalid inputs
- Proper error messages for failed operations
- Recovery from tool invocation failures

## Authentication Flow
- JWT token validation for all API endpoints
- User_id extraction from token claims
- Integration with Better Auth for user management
- Secure token storage and refresh mechanisms

## State Management
- Stateless backend architecture
- All conversation state persisted to database
- Task state managed through MCP tools
- Conversation history maintained per user

## Frontend Integration
- OpenAI ChatKit UI implementation
- WebSocket connection for real-time messaging
- User authentication integration
- Conversation history display
- Allowlisted domains configuration for ChatKit

## Deployment Configuration
- Docker containerization
- Environment variable configuration
- Database migration scripts
- Health check endpoints
- Port configuration (7860 for Hugging Face Spaces compatibility)

## Security Considerations
- Input validation for all user inputs
- SQL injection prevention through ORM
- JWT token security best practices
- Rate limiting for API endpoints
- Secure credential management

## Testing Strategy
- Unit tests for MCP tools
- Integration tests for API endpoints
- End-to-end tests for complete workflows
- Authentication flow testing
- Database operation validation