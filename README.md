# Private AI Workmate

> A personal AI work assistant powered by NVIDIA Nemotron on Nebius Token Factory.

Private AI Workmate is an AI-powered personal productivity and developer assistant designed to combine **long-term memory, private document RAG, controlled agentic tools, and GitHub developer capabilities** in a single system.

Built for the **Nebius x NVIDIA Global AI Hackathon 2026 - Personal AI track**.

## Current Status

### Implemented

- ✅ NVIDIA Nemotron integration through Nebius Token Factory
- ✅ FastAPI backend
- ✅ Persistent conversation storage
- ✅ Long-term semantic memory
- ✅ Private document RAG
- ✅ PDF, DOCX and TXT document ingestion
- ✅ Qdrant vector search
- ✅ Agentic tool execution
- ✅ Tool permission system
- ✅ Tool execution audit logging
- ✅ Calculator tool
- ✅ Current-time tool
- ✅ Document search and retrieval
- ✅ GitHub Developer Mode
- ✅ GitHub repository inspection
- ✅ GitHub file browsing and reading
- ✅ GitHub code search
- ✅ GitHub issue inspection
- ✅ GitHub pull-request inspection

### Planned

- [ ] Intelligent model routing
- [ ] Advanced security and permission controls
- [ ] Personal AI Workmate frontend
- [ ] Production deployment on Nebius
- [ ] Evaluation and benchmarking framework
- [ ] Hackathon demo and documentation

---

## Architecture

```text
					+----------------------+
					|        User          |
					+----------+-----------+
							   |
							   v
					+----------------------+
					|    FastAPI Backend   |
					+----------+-----------+
							   |
							   v
					+----------------------+
					|  Agent Orchestrator  |
					|      Nemotron        |
					+-------+-------+------+
							|       |
				+-----------+       +------------+
				v                                v
	   +------------------+             +------------------+
	   |  Long-Term       |             |  Tool Execution  |
	   |  Memory          |             |                  |
	   | SQLite + Qdrant  |             | Calculator       |
	   +------------------+             | Documents        |
										| GitHub           |
										| Current Time     |
										+--------+---------+
												 |
												 v
										+------------------+
										|    Tool Result   |
										+--------+---------+
												 |
												 v
										+------------------+
										|     Nemotron     |
										|  Final Response  |
										+------------------+
```

---

## Key Features

### 1. NVIDIA Nemotron + Nebius

The system uses NVIDIA Nemotron through Nebius Token Factory as its core language model.

Current model:

```text
nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B
```

### 2. Persistent Long-Term Memory

Private AI Workmate can store useful information and retrieve it later using semantic similarity.

```text
User Information
	   |
	 SQLite
	   |
   Embeddings
	   |
	 Qdrant
	   |
Semantic Retrieval
	   |
	Nemotron
```

### 3. Private Document RAG

Users can upload personal documents and ask questions about them.

Supported formats:

- PDF
- DOCX
- TXT

Processing pipeline:

```text
Document
   |
Text Extraction
   |
Cleaning
   |
Chunking
   |
Embeddings
   |
Qdrant
   |
Semantic Retrieval
   |
Nemotron
   |
Grounded Answer
```

### 4. Agentic Tool Execution

The assistant can determine when a tool is required and execute controlled tools through a permission layer.

Available tools:

- Calculator
- Current time
- List documents
- Search documents
- Read documents
- GitHub repository information
- GitHub file listing
- GitHub file reading
- GitHub code search
- GitHub issue inspection
- GitHub pull-request inspection

Tool calls are recorded through an audit logging system.

---

## GitHub Developer Mode

Private AI Workmate includes a read-only GitHub developer mode.

The agent can:

1. Understand the developer's request
2. Select the appropriate GitHub tool
3. Query the GitHub API
4. Process the returned information
5. Provide a natural-language response

Currently, GitHub operations are intentionally **read-only**.

The agent does not currently:

- Push code
- Create commits
- Delete files
- Modify repositories
- Merge pull requests
- Approve pull requests
- Modify repository settings
- Execute GitHub Actions

---

## Security Approach

The project uses a controlled-tool architecture rather than exposing arbitrary system execution to the AI model.

```text
Nemotron
	|
Tool Request
	|
Permission Check
	|
Tool Executor
	|
Audit Log
	|
Tool Result
	|
Nemotron
	|
Final Response
```

Arbitrary shell or Python execution is not exposed to the agent.

Tool execution is restricted to explicitly registered tools.

---

## Technology Stack

### AI / ML

- NVIDIA Nemotron
- Nebius Token Factory
- Qwen3 Embedding
- Semantic Search
- Retrieval-Augmented Generation

### Backend

- Python
- FastAPI
- Uvicorn

### Storage

- SQLite
- Qdrant

### Document Processing

- PyPDF
- python-docx

### Developer Integration

- GitHub REST API
- HTTPX

### Development

- Git
- GitHub
- VS Code

---

## Project Structure

```text
private-ai-workmate/
|
+-- backend/
|   +-- app/
|   |   +-- agents/
|   |   +-- api/
|   |   +-- github/
|   |   +-- memory/
|   |   +-- rag/
|   |   +-- tools/
|   |   +-- config.py
|   |   +-- main.py
|   |   +-- nemotron.py
|   |
|   +-- .env.example
|   +-- requirements.txt
|
+-- frontend/
+-- tests/
+-- docs/
+-- .gitignore
+-- README.md
```

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/saad07072/private-ai-workmate.git
cd private-ai-workmate
```

### 2. Create a virtual environment

#### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Create:

```text
backend/.env
```

Add:

```env
NEBIUS_API_KEY=your_nebius_api_key
GITHUB_TOKEN=your_github_token
```

Never commit `.env` or API keys to GitHub.

### 5. Start the backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Example API Usage

### Health Check

```http
GET /health
```

### Chat

```http
POST /api/chat
```

Example:

```json
{
  "message": "What programming technologies have I worked with?"
}
```

### Upload a Document

```http
POST /api/documents/upload
```

### List Documents

```http
GET /api/documents
```

### Add Memory

```http
POST /api/memory
```

---

## Development Roadmap

### Phase 1 - Foundation

- [x] Nebius integration
- [x] NVIDIA Nemotron
- [x] FastAPI backend

### Phase 2 - Memory

- [x] Persistent conversations
- [x] Long-term memory
- [x] Semantic memory retrieval

### Phase 3 - Private Knowledge

- [x] PDF support
- [x] DOCX support
- [x] TXT support
- [x] Document chunking
- [x] Vector search
- [x] RAG

### Phase 4 - Agents

- [x] Agent orchestration
- [x] Tool registry
- [x] Permission layer
- [x] Tool execution
- [x] Audit logging

### Phase 5 - Developer AI

- [x] GitHub repository inspection
- [x] GitHub file browsing
- [x] GitHub code search
- [x] GitHub issue inspection
- [x] Pull-request inspection

### Phase 6 - Intelligence

- [ ] Model routing
- [ ] Task complexity detection
- [ ] Specialized model selection

### Phase 7 - Security

- [ ] Fine-grained permissions
- [ ] User approval workflows
- [ ] Security policies
- [ ] Improved audit interface

### Phase 8 - User Interface

- [ ] Workmate web UI
- [ ] Chat interface
- [ ] Memory interface
- [ ] Document management
- [ ] Developer mode interface

### Phase 9 - Production

- [ ] Nebius deployment
- [ ] Production architecture
- [ ] Monitoring
- [ ] Performance optimization

### Phase 10 - Evaluation

- [ ] Automated evaluation
- [ ] RAG evaluation
- [ ] Tool-use evaluation
- [ ] Memory retrieval evaluation
- [ ] Latency measurements
- [ ] Hackathon demo

---

## Vision

Private AI Workmate aims to become a personal AI workspace that can understand user context, remember useful information, work with private documents, assist with software development, and execute controlled tasks through explicit and auditable tools.

The long-term goal is to move beyond a simple chatbot toward a **personal AI system with memory, knowledge, tools, and developer capabilities**.

---

## Hackathon

Built for:

**Nebius x NVIDIA Global AI Hackathon 2026**

**Track:** Personal AI

Core technologies:

- NVIDIA Nemotron
- Nebius Token Factory
- Qdrant
- FastAPI
- Python
- GitHub API

---

## Author

**Saad Mujawar**

GitHub:  
https://github.com/saad07072

⭐ If you find the project interesting, consider starring the repository.
