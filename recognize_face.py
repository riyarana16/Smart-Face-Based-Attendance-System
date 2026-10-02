import cv2
import sqlite3
from datetime import datetime
import openpyxl
import os

# Load trained model
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')

# Load face detector
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Start camera
cam = cv2.VideoCapture(0)

font = cv2.FONT_HERSHEY_SIMPLEX

# Store IDs already marked
recorded_ids = set()


# Function to get student name from database
def get_name(student_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM students WHERE id=?", (student_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return "Unknown"


# Function to save attendance in Excel
def mark_attendance(student_id, name):

    file = "attendance/attendance.xlsx"

    # Create Excel file if it doesn't exist
    if not os.path.exists(file):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["ID", "Name", "Date", "Time"])
        workbook.save(file)

    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active

    now = datetime.now()

    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%H:%M:%S")

    sheet.append([student_id, name, date, time])

    workbook.save(file)


# Start recognition loop
while True:

    ret, img = cam.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(gray, 1.2, 5)

    for (x, y, w, h) in faces:

        student_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

        if confidence < 70:

            name = get_name(student_id)

            # Mark attendance only once
            if student_id not in recorded_ids:
                mark_attendance(student_id, name)
                recorded_ids.add(student_id)

        else:
            name = "Unknown"

        # Display name on screen
        cv2.putText(img, name, (x, y-10),
                    font, 1, (0, 255, 0), 2)

        cv2.rectangle(img, (x, y), (x+w, y+h),
                      (255, 0, 0), 2)

    cv2.imshow("Face Recognition Attendance System", img)

    # Press ESC to stop
    if cv2.waitKey(1) == 27:
        break


cam.release()
cv2.destroyAllWindows()