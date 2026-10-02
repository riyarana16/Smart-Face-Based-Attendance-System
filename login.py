import tkinter as tk
from tkinter import messagebox
import main

def login():

    username = user_entry.get()
    password = pass_entry.get()

    if username == "admin" and password == "1605":
        root.destroy()
        main.dashboard()
    else:
        messagebox.showerror("Error","Invalid login")

root = tk.Tk()
root.title("Admin Login")
root.geometry("300x200")

tk.Label(root,text="Username").pack()
user_entry = tk.Entry(root)
user_entry.pack()

tk.Label(root,text="Password").pack()
pass_entry = tk.Entry(root,show="*")
pass_entry.pack()

tk.Button(root,text="Login",command=login).pack(pady=10)

root.mainloop()
