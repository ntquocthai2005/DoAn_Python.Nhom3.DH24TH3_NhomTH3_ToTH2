import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ==========================
# CƠ SỞ DỮ LIỆU
# ==========================
def create_db():
    conn = sqlite3.connect("banhang.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sanpham (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten TEXT NOT NULL,
            gia REAL NOT NULL,
            soluong INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_data(ten, gia, soluong):
    conn = sqlite3.connect("banhang.db")
    c = conn.cursor()
    c.execute("INSERT INTO sanpham (ten, gia, soluong) VALUES (?, ?, ?)", (ten, gia, soluong))
    conn.commit()
    conn.close()

def fetch_data():
    conn = sqlite3.connect("banhang.db")
    c = conn.cursor()
    c.execute("SELECT * FROM sanpham")
    rows = c.fetchall()
    conn.close()
    return rows

def update_data(id, ten, gia, soluong):
    conn = sqlite3.connect("banhang.db")
    c = conn.cursor()
    c.execute("UPDATE sanpham SET ten=?, gia=?, soluong=? WHERE id=?", (ten, gia, soluong, id))
    conn.commit()
    conn.close()

def delete_data(id):
    conn = sqlite3.connect("banhang.db")
    c = conn.cursor()
    c.execute("DELETE FROM sanpham WHERE id=?", (id,))
    conn.commit()
    conn.close()

# ==========================
# GIAO DIỆN TKINTER
# ==========================
class QuanLyBanHang:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản Lý Bán Hàng")
        self.root.geometry("700x500")

        self.ten = tk.StringVar()
        self.gia = tk.StringVar()
        self.soluong = tk.StringVar()
        self.selected_id = None

        # --- Nhập dữ liệu ---
        frame_input = tk.LabelFrame(root, text="Thông tin sản phẩm", padx=10, pady=10)
        frame_input.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_input, text="Tên sản phẩm:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(frame_input, textvariable=self.ten).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_input, text="Giá:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(frame_input, textvariable=self.gia).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_input, text="Số lượng:").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(frame_input, textvariable=self.soluong).grid(row=2, column=1, padx=5, pady=5)

        tk.Button(frame_input, text="Thêm", command=self.add).grid(row=3, column=0, pady=10)
        tk.Button(frame_input, text="Cập nhật", command=self.update).grid(row=3, column=1, pady=10)
        tk.Button(frame_input, text="Xóa", command=self.delete).grid(row=3, column=2, pady=10)

        # --- Bảng dữ liệu ---
        frame_table = tk.Frame(root)
        frame_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(frame_table, columns=("ID", "Tên", "Giá", "Số lượng", "Thành tiền"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Tên", text="Tên")
        self.tree.heading("Giá", text="Giá")
        self.tree.heading("Số lượng", text="Số lượng")
        self.tree.heading("Thành tiền", text="Thành tiền")
        self.tree.column("ID", width=40)
        self.tree.bind("<ButtonRelease-1>", self.get_selected_row)
        self.tree.pack(fill="both", expand=True)

        # --- Tổng doanh thu ---
        self.lbl_total = tk.Label(root, text="Tổng doanh thu: 0", font=("Arial", 12, "bold"))
        self.lbl_total.pack(pady=10)

        self.load_data()

    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_data()
        total = 0
        for row in rows:
            thanh_tien = row[2] * row[3]
            total += thanh_tien
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], thanh_tien))
        self.lbl_total.config(text=f"Tổng doanh thu: {total:,.0f} VNĐ")

    def add(self):
        if not self.ten.get() or not self.gia.get() or not self.soluong.get():
            messagebox.showwarning("Lỗi", "Vui lòng nhập đủ thông tin!")
            return
        try:
            insert_data(self.ten.get(), float(self.gia.get()), int(self.soluong.get()))
            self.load_data()
            self.clear_input()
        except ValueError:
            messagebox.showerror("Lỗi", "Giá và số lượng phải là số!")

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("Lỗi", "Chưa chọn sản phẩm!")
            return
        update_data(self.selected_id, self.ten.get(), float(self.gia.get()), int(self.soluong.get()))
        self.load_data()
        self.clear_input()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Lỗi", "Chưa chọn sản phẩm!")
            return
        delete_data(self.selected_id)
        self.load_data()
        self.clear_input()

    def get_selected_row(self, event):
        item = self.tree.focus()
        values = self.tree.item(item, "values")
        if values:
            self.selected_id = values[0]
            self.ten.set(values[1])
            self.gia.set(values[2])
            self.soluong.set(values[3])

    def clear_input(self):
        self.ten.set("")
        self.gia.set("")
        self.soluong.set("")
        self.selected_id = None


# ==========================
# CHẠY CHƯƠNG TRÌNH
# ==========================
if __name__ == "__main__":
    create_db()
    root = tk.Tk()
    app = QuanLyBanHang(root)
    root.mainloop()
