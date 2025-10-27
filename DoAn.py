import tkinter as tk
from tkinter import ttk,messagebox
from tkcalendar import DateEntry
import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="",
        password="",
        database="qlbanhang"
    )

def center_window(win, w=700, h=500):
    ws=win.winfo_screenwidth()
    hs=win.winfo_screenheight()
    x=(ws // 2)-(w // 2)
    y=(hs // 2)-(h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

root=tk.Tk()
root.title("Quản lý bán hàng")
center_window(root, 700, 500)
root.resizable(False, False)

lbl_title=tk.Label(root,text="QUẢN LÝ BÁN HÀNG",font=("Arial",18,"bold"))
lbl_title.pack(pady=10)

frame_info=tk.Frame(root)
frame_info.pack(pady=5,padx=10,fill="x")

tk.Label(frame_info, text="Mã hàng").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_mahang=tk.Entry(frame_info,width=10)
entry_mahang.grid(row=0,column=1, padx=5, pady=5,sticky="w")

