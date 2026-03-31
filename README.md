# Multi-Agent Task Manager

A multi-agent AI system for managing tasks, schedules, and information using MCP (Model Context Protocol) integration.

## Features

- **Multi-Agent Coordination**: Primary agent coordinates sub-agents for different workflows
- **MCP Tool Integration**: Calendar, Task Manager, Notes, and Search tools via MCP
- **Persistent Database**: SQLite database for tasks, events, and notes
- **Real-time UI**: Web interface with live agent status and tool call transparency
- **API Deployment**: FastAPI-based REST API and WebSocket support
- **Predefined Workflows**:
  - Plan My Week
  - Proposal Deadline
  - Schedule Team Sync
  - What's On My Plate?

## Architecture

- **Backend**: FastAPI with SQLAlchemy
- **Database**: SQLite
- **Frontend**: HTML/CSS/JavaScript with WebSocket
- **Agent Framework**: Custom multi-agent coordination
- **Tools**: MCP-integrated tools for various functions

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open http://localhost:8002 in your browser

## Usage

1. **Chat View**: Interact with the AI system using natural language
2. **Database View**: Browse stored tasks, events, and notes
3. **Architecture View**: See system diagram and component descriptions

## API Endpoints

- `GET /`: Home page
- `GET /chat`: Chat interface
- `GET /database`: Database browser
- `GET /architecture`: System architecture
- `POST /api/chat`: REST API for chat
- `WS /ws/chat`: WebSocket for real-time chat

## Workflows

### Plan My Week
Generates a weekly brief with prioritized tasks, upcoming events, and relevant notes.

### Proposal Deadline
Creates a task for proposal completion, blocks focus time, and saves a preparation checklist.

### Schedule Team Sync
Books a team meeting, creates an agenda preparation task, and saves the agenda.

### What's On My Plate?
Provides a daily overview with overdue items, today's events, and top priorities.