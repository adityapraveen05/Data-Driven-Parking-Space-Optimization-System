# SRM Parking System — Backend

## Folder Structure
```
backend/
├── app.py                  ← Main Flask application
├── requirements.txt        ← Python dependencies
├── start.bat               ← Windows: double-click to run
├── start.sh                ← Mac/Linux: run in terminal
├── best.pt                 ← YOUR YOLO model (add this!)
├── parking.db              ← Auto-created on first run
├── PUT_YOUR_MODEL_HERE.txt ← Instructions for model
└── .vscode/
    ├── launch.json         ← VS Code debug config
    └── settings.json       ← VS Code settings
```

## Quick Start

### Option 1 — Terminal in VS Code (Ctrl + `)
```bash
pip install -r requirements.txt
python app.py
```

### Option 2 — Windows
Double-click `start.bat`

### Option 3 — VS Code Debug
Press F5 (uses .vscode/launch.json)

## Before Running — 2 things to update in app.py

### 1. Add your Gmail App Password (for email confirmations)
```python
SMTP_EMAIL    = "your_gmail@gmail.com"
SMTP_PASSWORD = "your_app_password"
```
Get App Password: myaccount.google.com → Security → App Passwords

### 2. Add your YOLO model
Copy `best.pt` from Google Colab downloads into this folder.

## Demo Login Credentials
| Email                  | Password | Role    |
|------------------------|----------|---------|
| ak8815@srmist.edu.in   | 1234     | Student |
| rs1234@srmist.edu.in   | 1234     | Student |
| faculty@srmist.edu.in  | 1234     | Faculty |

## API Endpoints
| Method | Endpoint        | Description         |
|--------|-----------------|---------------------|
| POST   | /api/login      | Login               |
| GET    | /api/slots      | Get all slots       |
| POST   | /api/book       | Book a slot         |
| GET    | /api/bookings   | Get user bookings   |
| POST   | /api/release    | Release a slot      |
| POST   | /api/predict    | YOLO prediction     |
| GET    | /api/health     | Health check        |

## Verify it's running
Open browser → http://localhost:5000/api/health
Should return: {"model_loaded": true, "status": "online"}
