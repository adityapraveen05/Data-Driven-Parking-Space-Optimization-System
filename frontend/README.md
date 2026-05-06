# SRM Parking System — Frontend

## Folder Structure
```
frontend/
├── index.html         ← Main app (all pages in one file)
├── README.md
└── .vscode/
    ├── settings.json  ← Live Server config (port 5500)
    └── extensions.json← Recommends Live Server extension
```

## Quick Start

### Step 1 — Install Live Server extension
- Open VS Code Extensions (Ctrl+Shift+X)
- Search: **Live Server**
- Install by Ritwick Dey

### Step 2 — Open frontend folder in VS Code
File → Open Folder → select this frontend/ folder

### Step 3 — Launch
Right-click `index.html` → **Open with Live Server**
OR click **Go Live** button in the bottom-right of VS Code

Frontend runs on → http://localhost:5500

## ⚠️ Make sure backend is running first!
The frontend connects to: http://localhost:5000/api
Start the backend before using the app.

## Demo Credentials
| Email                 | Password |
|-----------------------|----------|
| ak8815@srmist.edu.in  | 1234     |
| rs1234@srmist.edu.in  | 1234     |
| faculty@srmist.edu.in | 1234     |

## Pages Included
- Role Selection (Student / Faculty)
- Login with SRMIST email validation
- Dashboard with quick access cards
- Slots page with real-time grid (48 slots)
- Bookings page with active reservation management
