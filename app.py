import cv2
import os
import base64
import numpy as np
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file
import openpyxl


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "database.db")

DATASET_FOLDER = os.path.join(BASE_DIR, "dataset")

TRAINER_FOLDER = os.path.join(BASE_DIR, "trainer")

ATTENDANCE_FOLDER = os.path.join(BASE_DIR, "attendance")

CASCADE_PATH = os.path.join(
    BASE_DIR,
    "haarcascade_frontalface_default.xml"
)

MODEL_PATH = os.path.join(
    TRAINER_FOLDER,
    "trainer.yml"
)


# =========================================================
# CREATE FOLDERS
# =========================================================

os.makedirs(DATASET_FOLDER, exist_ok=True)
os.makedirs(TRAINER_FOLDER, exist_ok=True)
os.makedirs(ATTENDANCE_FOLDER, exist_ok=True)


# =========================================================
# FACE DETECTOR
# =========================================================

face_detector = cv2.CascadeClassifier(
    CASCADE_PATH
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

def create_tables():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            UNIQUE(student_id, date)
        )
    """)

    conn.commit()

    conn.close()


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# REGISTER PAGE
# =========================================================

@app.route("/register")
def register():

    return render_template("register.html")


# =========================================================
# ATTENDANCE PAGE
# =========================================================

@app.route("/attendance")
def attendance():

    return render_template("attendance.html")


# =========================================================
# RECORDS PAGE
# =========================================================

@app.route("/records")
def records():

    conn = get_db_connection()

    attendance_data = conn.execute("""
        SELECT *
        FROM attendance
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "records.html",
        attendance=attendance_data
    )


# =========================================================
# REGISTER STUDENT
# =========================================================

@app.route("/api/register", methods=["POST"])
def register_student():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received."
            })

        student_id = data.get("id")
        name = data.get("name")

        if not student_id or not name:

            return jsonify({
                "success": False,
                "message": "Student ID and Name are required."
            })

        student_id = int(student_id)
        name = name.strip()

        if name == "":

            return jsonify({
                "success": False,
                "message": "Student name cannot be empty."
            })

        conn = get_db_connection()

        existing = conn.execute(
            """
            SELECT id
            FROM students
            WHERE id = ?
            """,
            (student_id,)
        ).fetchone()

        if existing:

            conn.close()

            return jsonify({
                "success": False,
                "message": "This Student ID already exists."
            })

        conn.execute(
            """
            INSERT INTO students
            (id, name)
            VALUES (?, ?)
            """,
            (student_id, name)
        )

        conn.commit()

        conn.close()

        return jsonify({
            "success": True,
            "message": "Student registered successfully."
        })

    except ValueError:

        return jsonify({
            "success": False,
            "message": "Student ID must be a number."
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Registration error: " + str(e)
        })


# =========================================================
# CAPTURE FACE SAMPLE
# =========================================================

@app.route("/api/capture", methods=["POST"])
def capture_face():

    try:

        data = request.get_json()

        student_id = data.get("id")
        image_data = data.get("image")
        image_number = data.get("image_number")

        if not student_id or not image_data:

            return jsonify({
                "success": False,
                "message": "Student ID or image is missing."
            })

        student_id = int(student_id)

        # Check student exists
        conn = get_db_connection()

        student = conn.execute(
            """
            SELECT *
            FROM students
            WHERE id = ?
            """,
            (student_id,)
        ).fetchone()

        conn.close()

        if not student:

            return jsonify({
                "success": False,
                "message": "Please register the student first."
            })

        # Remove base64 header
        if "," in image_data:

            image_data = image_data.split(
                ",",
                1
            )[1]

        # Decode image
        image_bytes = base64.b64decode(
            image_data
        )

        image_array = np.frombuffer(
            image_bytes,
            np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:

            return jsonify({
                "success": False,
                "message": "Could not read camera image."
            })

        # Grayscale
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # Detect face
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(100, 100)
        )

        if len(faces) == 0:

            return jsonify({
                "success": False,
                "message": "No face detected. Keep your face inside the camera."
            })

        # Select largest face
        x, y, w, h = max(
            faces,
            key=lambda face:
            face[2] * face[3]
        )

        face_crop = gray[
            y:y + h,
            x:x + w
        ]

        filename = os.path.join(
            DATASET_FOLDER,
            f"User.{student_id}.{image_number}.jpg"
        )

        cv2.imwrite(
            filename,
            face_crop
        )

        return jsonify({
            "success": True,
            "message":
                f"Face sample {image_number} captured successfully."
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message":
                "Capture error: " + str(e)
        })


# =========================================================
# TRAIN MODEL
# =========================================================

@app.route("/api/train", methods=["POST"])
def train_model():

    try:

        faces = []
        ids = []

        # Read dataset images
        for filename in os.listdir(
            DATASET_FOLDER
        ):

            if not filename.lower().endswith(".jpg"):
                continue

            parts = filename.split(".")

            if len(parts) != 4:
                continue

            try:

                student_id = int(parts[1])

            except ValueError:

                continue

            image_path = os.path.join(
                DATASET_FOLDER,
                filename
            )

            image = cv2.imread(
                image_path,
                cv2.IMREAD_GRAYSCALE
            )

            if image is None:
                continue

            faces.append(image)
            ids.append(student_id)

        if len(faces) == 0:

            return jsonify({
                "success": False,
                "message": "No training images found."
            })

        # Check OpenCV face module
        if not hasattr(cv2, "face"):

            return jsonify({
                "success": False,
                "message":
                    "OpenCV face module not found. Install opencv-contrib-python."
            })

        # Create LBPH model
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        # Train
        recognizer.train(
            faces,
            np.array(ids)
        )

        # Save model
        recognizer.write(
            MODEL_PATH
        )

        return jsonify({
            "success": True,
            "message":
                f"Model trained successfully using {len(faces)} images."
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message":
                "Training error: " + str(e)
        })


# =========================================================
# MARK ATTENDANCE
# =========================================================

def mark_attendance(
    student_id,
    name
):

    conn = get_db_connection()

    now = datetime.now()

    today = now.strftime(
        "%Y-%m-%d"
    )

    current_time = now.strftime(
        "%H:%M:%S"
    )

    # Check today's attendance
    existing = conn.execute(
        """
        SELECT *
        FROM attendance
        WHERE student_id = ?
        AND date = ?
        """,
        (
            student_id,
            today
        )
    ).fetchone()

    if existing:

        conn.close()

        return False

    conn.execute(
        """
        INSERT INTO attendance
        (
            student_id,
            name,
            date,
            time
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            student_id,
            name,
            today,
            current_time
        )
    )

    conn.commit()

    conn.close()

    return True


# =========================================================
# LIVE ATTENDANCE / FACE MATCHING
# =========================================================

@app.route("/api/predict", methods=["POST"])
def predict():

    try:

        # Check trained model
        if not os.path.exists(MODEL_PATH):

            return jsonify({
                "success": False,
                "message":
                    "Model not trained. Please train the model first."
            })

        data = request.get_json()

        if not data or not data.get("image"):

            return jsonify({
                "success": False,
                "message": "No image received."
            })

        image_data = data["image"]

        # Remove base64 header
        if "," in image_data:

            image_data = image_data.split(
                ",",
                1
            )[1]

        # Decode image
        image_bytes = base64.b64decode(
            image_data
        )

        image_array = np.frombuffer(
            image_bytes,
            np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:

            return jsonify({
                "success": False,
                "message": "Could not read image."
            })

        # Convert to grayscale
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # Detect all faces
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(100, 100)
        )

        if len(faces) == 0:

            return jsonify({
                "success": True,
                "faces": []
            })

        # Load model
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        recognizer.read(
            MODEL_PATH
        )

        # Get students
        conn = get_db_connection()

        students = conn.execute(
            """
            SELECT *
            FROM students
            """
        ).fetchall()

        conn.close()

        student_dict = {

            student["id"]:
            student["name"]

            for student in students

        }

        results = []

        # =================================================
        # PROCESS EVERY FACE
        # =================================================

        for (
            x,
            y,
            w,
            h
        ) in faces:

            face_crop = gray[
                y:y + h,
                x:x + w
            ]

            student_id, confidence = recognizer.predict(
                face_crop
            )

            # Threshold = 100
            if (
                student_id in student_dict
                and confidence < 100
            ):

                name = student_dict[
                    student_id
                ]

                marked = mark_attendance(
                    student_id,
                    name
                )

                results.append({

                    "id": student_id,

                    "name": name,

                    "confidence": round(
                        confidence,
                        2
                    ),

                    "marked": marked

                })

            else:

                results.append({

                    "id": None,

                    "name": "Unknown",

                    "confidence": round(
                        confidence,
                        2
                    ),

                    "marked": False

                })

        return jsonify({

            "success": True,

            "faces": results

        })

    except Exception as e:

        print(
            "Prediction error:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "Prediction error: " + str(e)

        })


# =========================================================
# GET STUDENTS
# =========================================================

@app.route("/api/students")
def get_students():

    try:

        conn = get_db_connection()

        students = conn.execute(
            """
            SELECT *
            FROM students
            ORDER BY id
            """
        ).fetchall()

        conn.close()

        result = []

        for student in students:

            result.append({

                "id":
                    student["id"],

                "name":
                    student["name"]

            })

        return jsonify(result)

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        })


# =========================================================
# GET ATTENDANCE
# =========================================================

@app.route("/api/attendance")
def get_attendance():

    try:

        conn = get_db_connection()

        attendance_data = conn.execute(
            """
            SELECT *
            FROM attendance
            ORDER BY id DESC
            """
        ).fetchall()

        conn.close()

        result = []

        for row in attendance_data:

            result.append({

                "id":
                    row["id"],

                "student_id":
                    row["student_id"],

                "name":
                    row["name"],

                "date":
                    row["date"],

                "time":
                    row["time"]

            })

        return jsonify(result)

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        })


# =========================================================
# DOWNLOAD EXCEL
# =========================================================

@app.route("/download/attendance")
def download_attendance():

    try:

        conn = get_db_connection()

        attendance_data = conn.execute(
            """
            SELECT
                student_id,
                name,
                date,
                time
            FROM attendance
            ORDER BY id DESC
            """
        ).fetchall()

        conn.close()

        workbook = openpyxl.Workbook()

        sheet = workbook.active

        sheet.title = "Attendance"

        # Headers
        sheet.append([
            "Student ID",
            "Student Name",
            "Date",
            "Time"
        ])

        # Data
        for row in attendance_data:

            sheet.append([
                row["student_id"],
                row["name"],
                row["date"],
                row["time"]
            ])

        excel_path = os.path.join(
            ATTENDANCE_FOLDER,
            "attendance_report.xlsx"
        )

        workbook.save(
            excel_path
        )

        return send_file(
            excel_path,
            as_attachment=True
        )

    except Exception as e:

        return jsonify({

            "success": False,

            "message":
                "Excel error: " + str(e)

        })


# =========================================================
# CREATE TABLES
# =========================================================

create_tables()


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )