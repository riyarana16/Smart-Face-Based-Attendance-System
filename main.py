import tkinter as tk
import os

def capture_faces():
    os.system("python capture_faces.py")

def train_model():
    os.system("python train_model.py")

def recognize_face():
    os.system("python recognize_face.py")

def register_student():
    os.system("python register_student.py")

def dashboard():

    root = tk.Tk()
    root.title("Face Recognition Attendance System")
    root.geometry("400x450")

    tk.Label(root,text="Attendance System",
             font=("Arial",20,"bold")).pack(pady=20)

    tk.Button(root,text="Register Student",
              width=20,height=2,
              command=register_student).pack(pady=10)

    tk.Button(root,text="Capture Faces",
              width=20,height=2,
              command=capture_faces).pack(pady=10)

    tk.Button(root,text="Train Model",
              width=20,height=2,
              command=train_model).pack(pady=10)

    tk.Button(root,text="Start Attendance",
              width=20,height=2,
              command=recognize_face).pack(pady=10)

    tk.Button(root,text="Exit",
              width=20,height=2,
              command=root.quit).pack(pady=10)

    root.mainloop()