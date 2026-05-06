"""
SRM Smart Bike Parking System - Backend
Flask + YOLOv8 + Email Confirmation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import sqlite3, uuid, os, smtplib, re
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)

# ============================================================
# CONFIG — update these before running
# ============================================================
YOLO_MODEL_PATH = "best.pt"          # Path to your trained YOLOv8 model
DB_PATH         = "parking.db"

# Gmail SMTP — use an App Password (not your real password)
# Go to: myaccount.google.com → Security → App Passwords
SMTP_EMAIL    = "your_gmail@gmail.com"   # ← change this
SMTP_PASSWORD = "your_app_password"      # ← change this (16-char app password)
# ============================================================

# Load YOLO model
try:
    model = YOLO(YOLO_MODEL_PATH)
    print(f"✅ YOLO model loaded: {YOLO_MODEL_PATH}")
except Exception as e:
    model = None
    print(f"⚠️  YOLO model not loaded: {e}. Slots will use DB status only.")

# ============================================================
# DATABASE SETUP
# ============================================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email    TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name     TEXT,
            role     TEXT DEFAULT 'student'
        )
    """)

    # Slots table — 6 rows x 8 columns = 48 slots
    c.execute("""
        CREATE TABLE IF NOT EXISTS slots (
            id        TEXT PRIMARY KEY,
            status    TEXT DEFAULT 'available',
            booked_by TEXT
        )
    """)

    # Bookings table
    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id TEXT PRIMARY KEY,
            slot_id    TEXT NOT NULL,
            email      TEXT NOT NULL,
            name       TEXT,
            vehicle    TEXT,
            time       TEXT,
            active     INTEGER DEFAULT 1
        )
    """)

    # Seed slots if empty
    c.execute("SELECT COUNT(*) FROM slots")
    if c.fetchone()[0] == 0:
        rows, cols = 6, 8
        for r in range(rows):
            for col in range(cols):
                c.execute("INSERT INTO slots (id, status) VALUES (?, 'available')",
                          (f"r{r}_c{col}",))
        print(f"✅ Created {rows * cols} parking slots")

    # Seed demo users if empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        demo_users = [
            ("ak8815@srmist.edu.in", "1234", "Arjun Khanna", "student"),
            ("rs1234@srmist.edu.in", "1234", "Rahul Sharma", "student"),
            ("faculty@srmist.edu.in", "1234", "Dr. Ramesh", "faculty"),
        ]
        c.executemany("INSERT INTO users VALUES (?,?,?,?)", demo_users)
        print("✅ Demo users seeded")

    conn.commit()
    conn.close()

# ============================================================
# EMAIL
# ============================================================
def send_booking_email(to_email, name, slot_id, booking_id, vehicle, time_str):
    slot_display = slot_id.replace('_', '-').upper()
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 560px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: #3B5BDB; padding: 32px 40px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 22px; font-weight: 700; }}
        .header p {{ color: rgba(255,255,255,0.8); margin: 6px 0 0; font-size: 14px; }}
        .body {{ padding: 32px 40px; }}
        .greeting {{ font-size: 18px; font-weight: 600; color: #1a1d23; margin-bottom: 8px; }}
        .sub {{ color: #6b7280; font-size: 14px; margin-bottom: 28px; }}
        .detail-box {{ background: #f8f9ff; border: 1px solid #dbe4ff; border-radius: 12px; padding: 20px; margin-bottom: 24px; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e5e7eb; }}
        .detail-row:last-child {{ border-bottom: none; }}
        .detail-label {{ color: #6b7280; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
        .detail-value {{ color: #1a1d23; font-size: 14px; font-weight: 600; }}
        .slot-badge {{ background: #3B5BDB; color: white; padding: 4px 12px; border-radius: 99px; font-size: 13px; font-weight: 700; }}
        .reminder {{ background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 16px; margin-bottom: 24px; font-size: 13px; color: #92400e; }}
        .footer {{ background: #f8f9ff; padding: 20px 40px; text-align: center; font-size: 12px; color: #9ca3af; }}
        .srm-logo {{ width: 48px; height: 48px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.5); display: inline-flex; align-items: center; justify-content: center; font-weight: 800; color: white; font-size: 12px; margin-bottom: 12px; background: rgba(255,255,255,0.15); }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <div class="srm-logo">SRM</div>
          <h1>Parking Slot Confirmed!</h1>
          <p>Smart Bike Parking System • SRMIST</p>
        </div>
        <div class="body">
          <div class="greeting">Hi {name},</div>
          <div class="sub">Your parking slot has been successfully booked. Here are your booking details:</div>
          <div class="detail-box">
            <div class="detail-row">
              <span class="detail-label">Slot</span>
              <span class="slot-badge">{slot_display}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Name</span>
              <span class="detail-value">{name}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Email</span>
              <span class="detail-value">{to_email}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Vehicle</span>
              <span class="detail-value">{vehicle if vehicle else '—'}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Booked At</span>
              <span class="detail-value">{time_str}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Booking ID</span>
              <span class="detail-value">#{booking_id[:12].upper()}</span>
            </div>
          </div>
          <div class="reminder">
            ⚠️ <strong>Important:</strong> Please park only in your assigned slot <strong>{slot_display}</strong>.
            Unauthorized parking may result in penalties. Remember to release your slot after leaving.
          </div>
        </div>
        <div class="footer">
          <p>SRM Institute of Science and Technology • Smart Parking System</p>
          <p style="margin-top:4px">This is an automated email. Please do not reply.</p>
        </div>
      </div>
    </body>
    </html>
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"✅ Parking Slot {slot_display} Booked — SRMIST"
        msg['From']    = SMTP_EMAIL
        msg['To']      = to_email
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        print(f"📧 Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"⚠️  Email failed: {e}")
        return False

# ============================================================
# HELPERS
# ============================================================
def validate_srm_email(email):
    """Accepts: 2 letters + any digits + @srmist.edu.in"""
    return bool(re.match(r'^[a-zA-Z]{2}\d+@srmist\.edu\.in$', email))

# ============================================================
# ROUTES
# ============================================================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email    = data.get('email', '').strip()
    password = data.get('password', '')
    role     = data.get('role', 'student')

    if role == 'student' and not validate_srm_email(email):
        return jsonify(success=False, message="Invalid email format. Use: initials+numbers@srmist.edu.in")

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()
    conn.close()

    if user:
        return jsonify(success=True, name=user['name'], role=user['role'])
    return jsonify(success=False, message="Invalid credentials")


@app.route('/api/slots', methods=['GET'])
def get_slots():
    conn = get_db()
    slots = conn.execute("SELECT * FROM slots ORDER BY id").fetchall()
    conn.close()
    return jsonify(slots=[dict(s) for s in slots])


@app.route('/api/book', methods=['POST'])
def book_slot():
    data     = request.json
    slot_id  = data.get('slot_id')
    email    = data.get('email')
    name     = data.get('name', '')
    vehicle  = data.get('vehicle', '')

    if not slot_id or not email:
        return jsonify(success=False, message="Missing slot_id or email")

    conn = get_db()
    slot = conn.execute("SELECT * FROM slots WHERE id=?", (slot_id,)).fetchone()

    if not slot:
        conn.close()
        return jsonify(success=False, message="Slot not found")
    if slot['status'] != 'available':
        conn.close()
        return jsonify(success=False, message="Slot is not available")

    # Check user doesn't already have an active booking
    existing = conn.execute(
        "SELECT * FROM bookings WHERE email=? AND active=1", (email,)
    ).fetchone()
    if existing:
        conn.close()
        return jsonify(success=False, message="You already have an active booking")

    booking_id = str(uuid.uuid4()).replace('-', '').upper()
    time_str   = datetime.now().strftime("%d %b %Y, %I:%M %p")

    conn.execute("UPDATE slots SET status='booked', booked_by=? WHERE id=?", (email, slot_id))
    conn.execute(
        "INSERT INTO bookings VALUES (?,?,?,?,?,?,1)",
        (booking_id, slot_id, email, name, vehicle, time_str)
    )
    conn.commit()
    conn.close()

    # Send confirmation email
    send_booking_email(email, name, slot_id, booking_id, vehicle, time_str)

    return jsonify(success=True, booking_id=booking_id, message="Slot booked successfully")


@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    email = request.args.get('email')
    if not email:
        return jsonify(success=False, message="Email required")
    conn = get_db()
    bookings = conn.execute(
        "SELECT * FROM bookings WHERE email=? AND active=1", (email,)
    ).fetchall()
    conn.close()
    return jsonify(bookings=[dict(b) for b in bookings])


@app.route('/api/release', methods=['POST'])
def release_slot():
    data       = request.json
    slot_id    = data.get('slot_id')
    booking_id = data.get('booking_id')
    email      = data.get('email')

    conn = get_db()
    conn.execute("UPDATE slots SET status='available', booked_by=NULL WHERE id=?", (slot_id,))
    conn.execute("UPDATE bookings SET active=0 WHERE booking_id=? AND email=?", (booking_id, email))
    conn.commit()
    conn.close()
    return jsonify(success=True, message="Slot released")


@app.route('/api/predict', methods=['POST'])
def predict():
    """Run YOLO detection on an uploaded image and update slot statuses."""
    if model is None:
        return jsonify(success=False, message="YOLO model not loaded")

    if 'image' not in request.files:
        return jsonify(success=False, message="No image provided")

    img_file = request.files['image']
    img_path = f"/tmp/parking_{uuid.uuid4().hex}.jpg"
    img_file.save(img_path)

    try:
        results = model.predict(img_path, conf=0.25, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                cls  = int(box.cls)
                conf = float(box.conf)
                detections.append({
                    "class": "occupied" if cls == 0 else "vacant",
                    "confidence": round(conf, 3),
                    "bbox": [round(x, 2) for x in box.xyxy[0].tolist()]
                })
        os.remove(img_path)
        return jsonify(success=True, detections=detections, count=len(detections))
    except Exception as e:
        return jsonify(success=False, message=str(e))


@app.route('/api/register', methods=['POST'])
def register():
    """Register a new student user."""
    data     = request.json
    email    = data.get('email', '').strip()
    password = data.get('password', '')
    name     = data.get('name', '')

    if not validate_srm_email(email):
        return jsonify(success=False, message="Invalid SRMIST email format")
    if len(password) < 4:
        return jsonify(success=False, message="Password must be at least 4 characters")

    conn = get_db()
    existing = conn.execute("SELECT email FROM users WHERE email=?", (email,)).fetchone()
    if existing:
        conn.close()
        return jsonify(success=False, message="Email already registered")

    conn.execute("INSERT INTO users VALUES (?,?,?,'student')", (email, password, name))
    conn.commit()
    conn.close()
    return jsonify(success=True, message="Registered successfully")


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify(status="online", model_loaded=model is not None)


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    init_db()
    print("🚀 SRM Parking Backend running on http://localhost:5000")
    print("📧 Email configured:", SMTP_EMAIL)
    print("🤖 YOLO model:", "loaded" if model else "not loaded")
    app.run(debug=True, host='0.0.0.0', port=5000)
