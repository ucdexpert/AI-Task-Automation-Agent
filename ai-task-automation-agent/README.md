# AI Task Automation Agent

An intelligent AI-powered task automation platform that uses LLMs and tool integration to automate daily workflows.

## 🚀 Features

- **Multi-Step Task Automation**: Execute complex tasks with multiple steps automatically
- **Tool Integration**: Email, Web Scraping, File Operations, Calendar Management
- **AI-Powered Decision Making**: LLM decides which tools to use and in what order
- **Memory System**: Persistent conversation history and task context
- **Analytics Dashboard**: Track success rates, execution times, and tool usage
- **Real-Time Logs**: Monitor agent actions and performance

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Python web framework for building APIs
- **Groq API**: LLM inference with function calling support
- **PostgreSQL**: Database for tasks, conversations, and logs
- **SQLAlchemy**: ORM for database operations

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Data visualization
- **Axios**: HTTP client

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL database
- Groq API key

## 🚀 Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Update `.env` with your credentials:
- `DATABASE_URL`: Your PostgreSQL connection string
- `GROQ_API_KEY`: Your Groq API key
- `EMAIL_ADDRESS` & `EMAIL_PASSWORD`: For email tool (optional)

6. Run the backend:
```bash
uvicorn app.main:app --reload
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the frontend:
```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 📁 Project Structure

```
ai-task-automation-agent/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent orchestrator & memory
│   │   ├── api/             # API endpoints
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── tools/           # Tool implementations
│   │   ├── services/        # External services (LLM, Email)
│   │   └── config.py        # Configuration
│   └── requirements.txt
└── frontend/
    ├── app/                 # Next.js pages
    ├── components/          # React components
    └── lib/                 # API client & utilities
```

## 🔧 Available Tools

### 1. Email Tool
- Send emails with text/HTML content
- Draft emails without sending
- SMTP configuration required

### 2. Web Scraper Tool
- Extract text from websites
- Get all links from a page
- Summarize web content

### 3. File Tool
- Create and save documents
- Read existing files
- List directory contents
- Support for TXT, JSON, Markdown

### 4. More Tools (Coming Soon)
- Google Calendar integration
- Database queries
- API requests
- Image generation

## 🎯 Example Tasks

1. **"Scrape AI news from TechCrunch and summarize the top 5 stories"**
2. **"Create a productivity tips document and save it as a text file"**
3. **"Send an email to john@example.com with the meeting summary"**
4. **"Research Next.js best practices and save findings to a file"**

## 📊 API Endpoints

- `POST /api/tasks/execute` - Execute a new task
- `GET /api/tasks/` - List all tasks
- `GET /api/tasks/{id}` - Get specific task
- `GET /api/conversations/{session_id}` - Get conversation history
- `GET /api/analytics/dashboard` - Get dashboard analytics
- `GET /api/analytics/logs` - Get execution logs

## 🚀 Deployment

### Backend (Railway/Render/Hugging Face)
1. Set environment variables
2. Connect GitHub repository
3. Deploy automatically

### Frontend (Vercel)
1. Push to GitHub
2. Connect to Vercel
3. Set `NEXT_PUBLIC_API_URL` environment variable
4. Deploy

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Muhammad Uzair**
- GitHub: @ucdexpert
- LinkedIn: muhammaduzair-066733314
- Portfolio: uzair-portfolio01.vercel.app
