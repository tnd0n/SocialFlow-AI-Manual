# SocialFlow AI - React Frontend Setup Guide

## Overview
This React app displays SocialFlow AI content queues and execution logs in a dashboard format.

## Setup Instructions

### 1. Pre-Requisites
- Node.js and npm installed locally

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Run Development Server
```bash
npm start
```

Visit `http://localhost:3000` to view the dashboard.

### 4. Build for Production
```bash
npm run build
```

This generates static assets in the `build/` folder.

### 5. Serve with Python Backend

If you want integrated Python backend and React frontend:
- Build the React app
- Serve the static files from a Python HTTP server (Flask, FastAPI, or traditional HTTP server).

### 6. Example Flask server snippet
```python
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='../frontend/build')

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

Your SocialFlow content queues and logs must be placed in a folder the React app can access through HTTP, or served via the Flask static folder.

---

## Summary
- React frontend fetches JSON from `/content_queue/` and log Markdown
- Python backend/serving required for integration (CORS enabled)
- Consider hosting frontend separately using Vercel/Netlify and backend on cloud

This setup allows a clean separation with native React UI and powerful Python automation backend.
