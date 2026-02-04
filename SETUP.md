# Development Setup Guide

## Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend)
- npm or yarn

## Backend Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 2. Run Backend Server

```bash
python backend/server.py
```

The backend will start at `http://localhost:8000`

API documentation available at: `http://localhost:8000/docs`

## Frontend Setup

### 1. Install Node Dependencies

```bash
cd frontend
npm install
```

### 2. Create .env file

```bash
cp .env.example .env
```

### 3. Start Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Using the Application

### CLI Tool

```bash
# Make requests
python -m apiclient get <url>
python -m apiclient post <url> --body '<json>'

# Save requests
python -m apiclient save my-request -m GET -u <url>

# List and run
python -m apiclient list
python -m apiclient run my-request
```

### Web Interface

1. Open `http://localhost:5173` in browser
2. Enter request details in the left panel
3. Click "Send Request"
4. View formatted response on the right
5. Toggle dark mode with the moon icon
6. Save requests for reuse
7. View request history in sidebar

## Building for Production

### Frontend

```bash
cd frontend
npm run build
```

Output will be in `frontend/dist/`

### Deployment

Frontend can be deployed to:
- Vercel
- Netlify
- GitHub Pages
- Any static hosting

Backend can be deployed to:
- Render
- Railway
- AWS
- Heroku
- Any Python hosting platform

## Architecture

```
┌─────────────────────────────────────────┐
│          Web Browser UI                 │
│  (React + Vite @ localhost:5173)        │
└────────────────┬────────────────────────┘
                 │
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────────────┐
│       FastAPI Backend Server            │
│  (localhost:8000)                       │
│  ┌───────────────────────────────────┐  │
│  │   APIClient (HTTP Client Logic)   │  │
│  │   Config Manager (Request Store)  │  │
│  └───────────────────────────────────┘  │
└────────────────┬────────────────────────┘
                 │
                 │ HTTPS
                 ▼
          Third-party APIs
        (jsonplaceholder.typicode.com,
         api.github.com, etc.)
```

## Troubleshooting

### Backend won't start
- Ensure port 8000 is not in use: `netstat -ano | findstr :8000`
- Check Python installation: `python --version`
- Verify all dependencies: `pip list`

### Frontend won't load
- Ensure Node.js is installed: `node --version`
- Clear node_modules: `rm -r frontend/node_modules`
- Reinstall: `cd frontend && npm install`

### API requests fail
- Ensure backend is running
- Check CORS settings in `backend/server.py`
- Verify API URL in frontend `.env` file

## Project Structure

```
API Testing/
├── apiclient/              # CLI package
│   ├── cli.py
│   ├── client.py
│   ├── config.py
│   └── formatter.py
├── backend/
│   ├── server.py           # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── vite.config.js
│   ├── package.json
│   └── index.html
├── README.md
└── requirements.txt
```
