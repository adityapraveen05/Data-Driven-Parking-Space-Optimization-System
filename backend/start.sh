#!/bin/bash
echo "========================================"
echo "  SRM Parking System - Backend"
echo "========================================"
echo ""
echo "[1/2] Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "[2/2] Starting Flask server..."
echo ""
echo "Backend will run on: http://localhost:5000"
echo "Press CTRL+C to stop"
echo ""
python app.py
