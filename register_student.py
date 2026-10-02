import tkinter as tk
import sqlite3

def save_student():

    sid = id_entry.get()
    name = name_entry.get()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO students VALUES (?,?)",(sid,name))

    conn.commit()
    conn.close()

    print("Student saved")

root = tk.Tk()
root.title("Register Student")

tk.Label(root,text="Student ID").pack()
id_entry = tk.Entry(root)
id_entry.pack()

tk.Label(root,text="Student Name").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Button(root,text="Save",command=save_student).pack()

root.mainloop()
