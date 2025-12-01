import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import mysql.connector

# =============================================================================
# 1. CẤU HÌNH KẾT NỐI DATABASE
# =============================================================================
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",  # <--- MẬT KHẨU CỦA BẠN ĐÃ ĐƯỢC CHỈNH LẠI
            database="StockWise"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Lỗi Kết Nối", f"Không thể kết nối MySQL!\nLỗi: {err}")
        return None

# =============================================================================
# 2. XỬ LÝ DỮ LIỆU 
# =============================================================================
class DataManager:
    # --- ĐĂNG NHẬP ---
    def login(self):
        u = self.u.get().strip()
        p = self.p.get().strip()
        
        print(f"--- ĐANG THỬ ĐĂNG NHẬP: User={u}, Pass={p} ---") 
        
        # Gọi hàm kiểm tra từ class DataManager (Kết nối SQL)
        try:
            user_info = db.check_login(u, p)
            print(f"--- KẾT QUẢ TỪ SQL: {user_info} ---") 
        except Exception as e:
            print(f"--- LỖI KHI GỌI SQL: {e} ---") 
            return

        if user_info:
            print("--- ĐĂNG NHẬP THÀNH CÔNG! ĐANG MỞ APP CHÍNH... ---") 
            self.withdraw()
            def show(): self.deiconify(); self.u.delete(0,'end'); self.p.delete(0,'end')
            ModernApp(tb.Toplevel(self), user_data=user_info, logout_callback=show)
        else:
            print("--- ĐĂNG NHẬP THẤT BẠI ---") 
            messagebox.showerror('Lỗi', 'Sai thông tin hoặc chưa kết nối DB!\nKiểm tra Terminal để xem chi tiết.')
    def check_login(self, username, password):
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """SELECT TK.ten_dang_nhap, NV.ho_ten, NV.chuc_vu, NV.ma_nhan_vien 
                     FROM TaiKhoan TK JOIN NhanVien NV ON TK.ma_nhan_vien = NV.ma_nhan_vien
                     WHERE TK.ten_dang_nhap = %s AND TK.mat_khau = %s"""
            cursor.execute(sql, (username, password))
            return cursor.fetchone()
        finally: conn.close()

    # --- ĐĂNG KÝ (TRANSACTION) ---
    def register_user(self, user, pwd, name, phone, addr):
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM NhanVien")
            new_id = f"NV{cursor.fetchone()[0] + 1:02d}"
            
            # Thêm Nhân viên trước
            cursor.execute("INSERT INTO NhanVien (ma_nhan_vien, ho_ten, chuc_vu, ngay_vao_lam, luong_co_ban) VALUES (%s, %s, 'Sale', NOW(), 5000000)", (new_id, name))
            # Thêm Tài khoản sau
            cursor.execute("INSERT INTO TaiKhoan (ten_dang_nhap, mat_khau, ma_nhan_vien) VALUES (%s, %s, %s)", (user, pwd, new_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback(); print(e); return False
        finally: conn.close()

    # --- SẢN PHẨM ---
    def get_products(self):
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("SELECT * FROM SanPham")
        data = cursor.fetchall(); conn.close(); return data

    def add_product(self, p):
        conn = get_db_connection(); cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO SanPham VALUES (%s,%s,%s,%s,%s,%s)", p)
            conn.commit(); messagebox.showinfo("OK", "Đã thêm!")
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

    def update_product(self, p):
        conn = get_db_connection(); cursor = conn.cursor()
        try: # p: (Ten, Loai, Gia, Ton, Anh, Ma)
            cursor.execute("UPDATE SanPham SET ten_san_pham=%s, danh_muc=%s, gia_ban=%s, so_luong_ton=%s, hinh_anh=%s WHERE ma_san_pham=%s", p)
            conn.commit(); messagebox.showinfo("OK", "Đã sửa!")
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

    def delete_product(self, code):
        conn = get_db_connection(); cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM SanPham WHERE ma_san_pham=%s", (code,))
            conn.commit(); messagebox.showinfo("OK", "Đã xóa!")
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

    # --- KHÁCH HÀNG ---
    def get_customers(self):
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("SELECT * FROM KhachHang")
        data = cursor.fetchall(); conn.close(); return data

    def add_customer(self, p):
        conn = get_db_connection(); cursor = conn.cursor()
        try: cursor.execute("INSERT INTO KhachHang VALUES (%s,%s,%s,%s)", p); conn.commit(); messagebox.showinfo("OK", "Đã thêm!")
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

    def delete_customer(self, code):
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("DELETE FROM KhachHang WHERE ma_khach_hang=%s", (code,)); conn.commit(); conn.close()

    # --- NHÂN VIÊN ---
    def get_employees(self):
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("SELECT * FROM NhanVien")
        data = cursor.fetchall(); conn.close(); return data

    def delete_employee(self, code):
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("DELETE FROM NhanVien WHERE ma_nhan_vien=%s", (code,)); conn.commit(); conn.close()

    # --- THANH TOÁN (POS) ---
    def save_order(self, cart, total, ma_nv, ma_kh):
        conn = get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            # 1. Tạo Hóa đơn
            cursor.execute("INSERT INTO HoaDon (tong_tien, ma_nhan_vien, ma_khach_hang, ngay_lap) VALUES (%s,%s,%s,NOW())", (total, ma_nv, ma_kh))
            # 2. Trừ kho
            for item in cart:
                cursor.execute("UPDATE SanPham SET so_luong_ton = so_luong_ton - %s WHERE ma_san_pham = %s", (item['qty'], item['code']))
            # 3. Tăng thành tích NV
            cursor.execute("UPDATE NhanVien SET so_don_da_ban = so_don_da_ban + 1 WHERE ma_nhan_vien = %s", (ma_nv,))
            conn.commit()
            messagebox.showinfo("Thành công", f"Thanh toán {total:,.0f} VNĐ thành công!")
        except Exception as e:
            conn.rollback(); messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

    # --- THỐNG KÊ ---
    def get_stats(self):
        conn = get_db_connection(); cursor = conn.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM SanPham"); stats['p'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM KhachHang"); stats['c'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM NhanVien"); stats['e'] = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(tong_tien),0) FROM HoaDon"); stats['rev'] = cursor.fetchone()[0]
        conn.close(); return stats

db = DataManager()

# =============================================================================
# 3. GIAO DIỆN NGƯỜI DÙNG (MODERN APP)
# =============================================================================
class ModernApp:
    def __init__(self, root, user_data, logout_callback=None):
        self.root = root
        self.logout_callback = logout_callback
        self.style = tb.Style(theme='superhero')
        
        self.user_info = user_data
        self.is_admin = (user_data['chuc_vu'] == 'Quản lý')
        
        title = "QUẢN TRỊ VIÊN" if self.is_admin else "NHÂN VIÊN"
        self.root.title(f'StockWise - {title}: {user_data["ho_ten"]}')
        self.root.geometry('1280x850')
        
        self.search_var = tk.StringVar()
        self.current_image_path = None
        self.cart_items = []

        self.setup_layout()
        self.show_page('dashboard')

    def setup_layout(self):
        self.sidebar = tb.Frame(self.root, width=250, bootstyle="secondary")
        self.sidebar.pack(side='left', fill='y'); self.sidebar.pack_propagate(False)
        tb.Label(self.sidebar, text="StockWise", font=("Impact", 24), bootstyle="inverse-secondary").pack(pady=30)

        self.btn_refs = {}
        self.create_menu_btn("Tổng quan", "dashboard", "📊")
        self.create_menu_btn("BÁN HÀNG", "sales", "🛒")
        self.create_menu_btn("Sản phẩm", "products", "📦")
        self.create_menu_btn("Khách hàng", "customers", "👥")
        self.create_menu_btn("Nhân sự" if self.is_admin else "Hồ sơ", "employees", "👔")
        
        tb.Button(self.sidebar, text=" Đăng xuất", bootstyle="danger-outline", command=self.perform_logout).pack(side='bottom', fill='x', padx=20, pady=20)

        self.content_area = tb.Frame(self.root, padding=20)
        self.content_area.pack(side='right', fill='both', expand=True)
        self.header = tb.Frame(self.content_area); self.header.pack(fill='x', pady=(0, 20))
        
        role = "ADMIN" if self.is_admin else "STAFF"
        color = "danger" if self.is_admin else "success"
        tb.Label(self.header, text=f"Xin chào, {self.user_info['ho_ten']}", font=("Arial", 14, "bold"), bootstyle="primary").pack(side='left')
        tb.Label(self.header, text=f" [{role}]", font=("Arial", 10, "bold"), bootstyle=color).pack(side='left', padx=5)
        
        self.page_container = tb.Frame(self.content_area); self.page_container.pack(fill='both', expand=True)

    def perform_logout(self):
        self.root.destroy()
        if self.logout_callback: self.logout_callback()

    def create_menu_btn(self, text, key, icon):
        btn = tb.Button(self.sidebar, text=f" {icon}  {text}", bootstyle="secondary", command=lambda k=key: self.show_page(k))
        btn.pack(fill='x', pady=5, padx=10)
        self.btn_refs[key] = btn

    def show_page(self, key):
        for widget in self.page_container.winfo_children(): widget.destroy()
        for k, btn in self.btn_refs.items(): btn.configure(bootstyle="primary" if k == key else "secondary")
        
        if key == 'dashboard': self.build_dashboard()
        elif key == 'sales': self.build_sales()
        elif key == 'products': self.build_products()
        elif key == 'customers': self.build_customers()
        elif key == 'employees': self.build_employees()

    # --- DASHBOARD ---
    def build_dashboard(self):
        tb.Label(self.page_container, text="TỔNG QUAN KINH DOANH", font=("Helvetica", 20, "bold")).pack(anchor='w', pady=(0, 20))
        stats = db.get_stats()
        cards = tb.Frame(self.page_container); cards.pack(fill='x')
        self.create_card(cards, "SẢN PHẨM", f"{stats['products']}", "📦", "info")
        self.create_card(cards, "DOANH THU", f"$ {stats['revenue']:,.0f}", "💰", "success")
        self.create_card(cards, "KHÁCH HÀNG", f"{stats['customers']}", "👥", "warning")
        self.create_card(cards, "ĐƠN HÀNG", f"{stats['orders']}", "🧾", "danger")
        
        graph = tb.Labelframe(self.page_container, text="Biểu đồ", padding=10, bootstyle="secondary"); graph.pack(fill='x', expand=False, pady=20)
        fig = Figure(figsize=(5, 2.5), dpi=100); ax = fig.add_subplot(111)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']; sales = [10, 20, 15, 25, 30]
        fig.patch.set_facecolor('#2b3e50'); ax.set_facecolor('#2b3e50')
        ax.bar(months, sales, color='#5bc0de')
        ax.tick_params(colors='white'); ax.spines['bottom'].set_color('white'); ax.spines['left'].set_color('white'); ax.spines['top'].set_color('none'); ax.spines['right'].set_color('none')
        FigureCanvasTkAgg(fig, master=graph).get_tk_widget().pack(fill='both', expand=True)

    def create_card(self, parent, title, value, icon, style):
        card = tb.Frame(parent, bootstyle=style, padding=15); card.pack(side='left', fill='both', expand=True, padx=10)
        tb.Label(card, text=icon, font=("Segoe UI Emoji", 30), bootstyle=f"{style}-inverse").pack(side='left', padx=(0, 15))
        right = tb.Frame(card, bootstyle=style); right.pack(side='left', fill='x')
        tb.Label(right, text=title, font=("Bold", 10), bootstyle=f"{style}-inverse").pack(anchor='w')
        tb.Label(right, text=value, font=("Bold", 20), bootstyle=f"{style}-inverse").pack(anchor='w')

    # --- BÁN HÀNG ---
    def build_sales(self):
        self.cart_items = []
        f = self.page_container
        left = tb.Frame(f); left.pack(side='left', fill='both', expand=True, padx=(0, 20))
        right = tb.Frame(f, width=400, bootstyle="secondary"); right.pack(side='right', fill='y')

        tb.Label(left, text="TẠO ĐƠN HÀNG MỚI", font=("Bold", 20)).pack(anchor='w', pady=(0, 20))
        info = tb.Labelframe(left, text="Thông tin", padding=15); info.pack(fill='x')
        
        # Data từ DB
        db_cust = db.get_customers(); db_prod = db.get_products()
        c_vals = [f"{c[0]} - {c[1]}" for c in db_cust]
        p_vals = [f"{p[0]} - {p[1]}" for p in db_prod]

        tb.Label(info, text="Khách:").grid(row=0, column=0, pady=10)
        self.cb_c = ttk.Combobox(info, values=c_vals, width=35); self.cb_c.grid(row=0, column=1)
        if c_vals: self.cb_c.current(0)

        tb.Label(info, text="Món:").grid(row=1, column=0, pady=10)
        self.cb_p = ttk.Combobox(info, values=p_vals, width=35); self.cb_p.grid(row=1, column=1)
        self.lbl_p = tb.Label(info, text="Giá: 0 | Tồn: 0", bootstyle="info"); self.lbl_p.grid(row=2, column=1)
        
        def on_p_sel(e):
            idx = self.cb_p.current()
            if idx>=0: p=db_prod[idx]; self.lbl_p.config(text=f"Giá: {p[3]:,.0f} | Tồn: {p[4]}")
        self.cb_p.bind("<<ComboboxSelected>>", on_p_sel)

        tb.Label(info, text="SL:").grid(row=3, column=0, pady=10)
        self.spin = tb.Spinbox(info, from_=1, to=999, width=10); self.spin.grid(row=3, column=1); self.spin.set(1)
        
        def add():
            idx = self.cb_p.current()
            if idx<0: return
            p = db_prod[idx]; qty = int(self.spin.get())
            if qty > p[4]: messagebox.showwarning("Lỗi", "Hết hàng!"); return
            total = p[3]*qty
            self.cart_items.append({'code':p[0], 'name':p[1], 'qty':qty, 'price':p[3], 'total':total})
            refresh_cart()
        
        tb.Button(info, text="THÊM ⬇", bootstyle="success", command=add).grid(row=4, column=1, sticky='e', pady=10)

        # Giỏ hàng
        self.cart_tree = ttk.Treeview(right, columns=('n','q','t'), show='headings', height=15)
        self.cart_tree.heading('n', text='Tên'); self.cart_tree.column('n', width=120)
        self.cart_tree.heading('q', text='SL'); self.cart_tree.column('q', width=40)
        self.cart_tree.heading('t', text='Tiền'); self.cart_tree.column('t', width=100)
        self.cart_tree.pack(fill='both', expand=True, padx=10)
        self.lbl_tot = tb.Label(right, text="TỔNG: 0", font=("Bold", 20), bootstyle="warning-inverse"); self.lbl_tot.pack(pady=20)

        def refresh_cart():
            for r in self.cart_tree.get_children(): self.cart_tree.delete(r)
            g = 0
            for i in self.cart_items: 
                self.cart_tree.insert('', 'end', values=(i['name'], i['qty'], f"{i['total']:,.0f}"))
                g+=i['total']
            self.lbl_tot.config(text=f"TỔNG: {g:,.0f}")

        def pay():
            if not self.cart_items: return
            c_idx = self.cb_c.current()
            cust_id = db_cust[c_idx][0] if c_idx>=0 else None
            total = sum(i['total'] for i in self.cart_items)
            db.save_order(self.cart_items, total, self.user_info['ma_nhan_vien'], cust_id)
            self.cart_items=[]; refresh_cart(); self.build_sales() # Reload để cập nhật tồn kho

        tb.Button(right, text="THANH TOÁN", bootstyle="success", width=20, command=pay).pack(pady=5)

    # --- SẢN PHẨM ---
    def build_products(self):
        f = self.page_container; tb.Label(f, text="QUẢN LÝ SẢN PHẨM", font=("Bold", 20)).pack(anchor='w', pady=(0, 20))
        content = tb.Frame(f); content.pack(fill='both', expand=True)
        left = ttk.Frame(content, width=400); left.pack(side='left', fill='y', padx=10)
        right = ttk.Frame(content); right.pack(side='right', fill='both', expand=True, padx=10)

        form = tb.Labelframe(left, text='Thông tin', padding=10); form.pack(fill='x')
        ttk.Label(form, text='Mã:').grid(row=0,column=0,pady=5); self.p_code=tb.Entry(form, width=30); self.p_code.grid(row=0,column=1)
        ttk.Label(form, text='Tên:').grid(row=1,column=0,pady=5); self.p_name=tb.Entry(form, width=30); self.p_name.grid(row=1,column=1)
        ttk.Label(form, text='Loại:').grid(row=2,column=0,pady=5); self.p_cat=tb.Entry(form, width=30); self.p_cat.grid(row=2,column=1)
        ttk.Label(form, text='Giá:').grid(row=3,column=0,pady=5); self.p_price=tb.Entry(form, width=30); self.p_price.grid(row=3,column=1)
        ttk.Label(form, text='Tồn:').grid(row=4,column=0,pady=5); self.p_stock=tb.Entry(form, width=30); self.p_stock.grid(row=4,column=1)
        tb.Button(form, text='Ảnh...', command=self.ch_img).grid(row=5,column=1)
        
        btns = ttk.Frame(left); btns.pack(fill='x', pady=10)
        def cp(cmd): 
            if self.is_admin: cmd()
            else: messagebox.showerror("Từ chối", "Chỉ Admin mới được sửa!")
        tb.Button(btns, text='Thêm', bootstyle='success', command=lambda:cp(self.add_p)).pack(side='left', padx=2)
        tb.Button(btns, text='Sửa', bootstyle='warning', command=lambda:cp(self.edit_p)).pack(side='left', padx=2)
        tb.Button(btns, text='Xóa', bootstyle='danger', command=lambda:cp(self.del_p)).pack(side='left', padx=2)

        cols = ('code','name','cat','price','stock','img')
        self.tree = ttk.Treeview(right, columns=cols, show='headings'); self.tree.pack(fill='both', expand=True)
        self.tree.heading('code', text='MÃ'); self.tree.column('code', width=50)
        self.tree.heading('name', text='TÊN'); self.tree.column('name', width=150)
        self.tree.heading('cat', text='LOẠI'); self.tree.column('cat', width=80)
        self.tree.heading('price', text='GIÁ'); self.tree.column('price', width=80)
        self.tree.heading('stock', text='TỒN'); self.tree.column('stock', width=50)
        self.tree.column('img', width=0, stretch=False)
        self.tree.bind('<<TreeviewSelect>>', self.on_p_sel); self.refresh_p()

    def ch_img(self): 
        f = filedialog.askopenfilename()
        if f: self.current_image_path = f
    def add_p(self): db.add_product((self.p_code.get(), self.p_name.get(), self.p_cat.get(), float(self.p_price.get()), int(self.p_stock.get()), self.current_image_path or '')); self.refresh_p()
    def edit_p(self): db.update_product((self.p_name.get(), self.p_cat.get(), float(self.p_price.get()), int(self.p_stock.get()), self.current_image_path or '', self.p_code.get())); self.refresh_p()
    def del_p(self): 
        if self.tree.selection() and messagebox.askyesno('Xóa','Chắc chưa?'): db.delete_product(self.tree.item(self.tree.selection()[0])['values'][0]); self.refresh_p()
    def refresh_p(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for p in db.get_products(): self.tree.insert('', 'end', values=p)
    def on_p_sel(self, e):
        sel=self.tree.selection()
        if sel:
            v=self.tree.item(sel[0])['values']
            self.p_code.delete(0,'end'); self.p_code.insert(0,v[0])
            self.p_name.delete(0,'end'); self.p_name.insert(0,v[1])
            self.p_cat.delete(0,'end'); self.p_cat.insert(0,v[2])
            self.p_price.delete(0,'end'); self.p_price.insert(0,v[3])
            self.p_stock.delete(0,'end'); self.p_stock.insert(0,v[4])

    # --- KHÁCH HÀNG & NHÂN VIÊN (TƯƠNG TỰ) ---
    def build_customers(self):
        f = self.page_container; tb.Label(f, text="QUẢN LÝ KHÁCH HÀNG", font=("Bold", 20)).pack(pady=20)
        # (Để code ngắn gọn, phần này logic y hệt sản phẩm, bạn tự làm tương tự hoặc dùng bản trước nếu cần chi tiết)
        # Gọi db.get_customers() để đổ dữ liệu ra bảng
        cols = ('id','name','phone','addr')
        tree = ttk.Treeview(f, columns=cols, show='headings'); tree.pack(fill='both', expand=True)
        tree.heading('id', text='MÃ'); tree.heading('name', text='TÊN'); tree.heading('phone', text='SĐT'); tree.heading('addr', text='ĐỊA CHỈ')
        for c in db.get_customers(): tree.insert('', 'end', values=c)

    def build_employees(self):
        f = self.page_container
        if self.is_admin:
            tb.Label(f, text="QUẢN LÝ NHÂN VIÊN", font=("Bold", 20), bootstyle="danger").pack(pady=20)
            cols = ('id','name','role','date','salary')
            tree = ttk.Treeview(f, columns=cols, show='headings'); tree.pack(fill='both', expand=True)
            tree.heading('id', text='MÃ'); tree.heading('name', text='TÊN'); tree.heading('role', text='CHỨC VỤ')
            tree.heading('date', text='NGÀY VÀO'); tree.heading('salary', text='LƯƠNG')
            for e in db.get_employees(): 
                d = list(e[:5]); d[4] = f"{e[4]:,.0f}"; tree.insert('', 'end', values=d)
            
            # Nút xóa nhân viên
            def del_e():
                if tree.selection() and messagebox.askyesno('Xóa','Chắc chưa?'): 
                    db.delete_employee(tree.item(tree.selection()[0])['values'][0])
                    for w in f.winfo_children(): w.destroy()
                    self.build_employees()
            tb.Button(f, text="Xóa Nhân Viên được chọn", bootstyle="danger", command=del_e).pack(pady=10)
        else:
            tb.Label(f, text="HỒ SƠ CÁ NHÂN", font=("Bold", 20), bootstyle="success").pack(pady=20)
            # Tìm thông tin mình
            me = next((e for e in db.get_employees() if e[0] == self.user_info['ma_nhan_vien']), None)
            if me:
                tb.Label(f, text=f"Họ tên: {me[1]}", font=("Arial", 18)).pack()
                tb.Label(f, text=f"Chức vụ: {me[2]}", font=("Arial", 18)).pack()
                tb.Label(f, text=f"Doanh số (đơn đã bán): {me[5]}", font=("Bold", 24), bootstyle="success").pack(pady=20)

# =============================================================================
# 4. ĐĂNG NHẬP & ĐĂNG KÝ
# =============================================================================
class LoginWindow(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero"); self.title('Đăng nhập SQL'); self.geometry('450x550')
        frame = tb.Frame(self, padding=30); frame.place(relx=0.5, rely=0.5, anchor='center')
        tb.Label(frame, text='STOCKWISE', font=('Impact', 28), bootstyle="primary").pack(pady=10)
        tb.Label(frame, text='Tài khoản:').pack(anchor='w'); self.u = tb.Entry(frame, width=32); self.u.pack(pady=5)
        tb.Label(frame, text='Mật khẩu:').pack(anchor='w'); self.p = tb.Entry(frame, width=32, show='*'); self.p.pack(pady=5)
        tb.Button(frame, text='Đăng nhập', bootstyle='success', command=self.login).pack(fill='x', pady=20)
        tb.Button(frame, text='Đăng ký tài khoản', bootstyle='info-outline', command=self.reg).pack(fill='x')

    def login(self):
        user_info = db.check_login(self.u.get().strip(), self.p.get().strip())
        if user_info:
            self.withdraw()
            def show(): self.deiconify(); self.u.delete(0,'end'); self.p.delete(0,'end')
            ModernApp(tb.Toplevel(self), user_data=user_info, logout_callback=show)
        else: messagebox.showerror('Lỗi', 'Sai thông tin!')

    def reg(self):
        r=tb.Toplevel(self); r.geometry("350x550"); r.title("Đăng ký")
        pnl = tb.Frame(r, padding=20); pnl.pack(fill='both', expand=True)
        tb.Label(pnl, text="ĐĂNG KÝ", font=("Bold", 14), bootstyle="info").pack(pady=10)
        tb.Label(pnl, text="Tài khoản:").pack(anchor='w'); u=tb.Entry(pnl); u.pack(fill='x')
        tb.Label(pnl, text="Mật khẩu:").pack(anchor='w'); p=tb.Entry(pnl); p.pack(fill='x')
        tb.Label(pnl, text="Họ tên:").pack(anchor='w'); n=tb.Entry(pnl); n.pack(fill='x')
        def save():
            if db.register_user(u.get(), p.get(), n.get(), "", ""):
                messagebox.showinfo("OK", "Đăng ký thành công!"); r.destroy()
            else: messagebox.showerror("Lỗi", "Tên đăng nhập tồn tại")
        tb.Button(pnl, text="Đăng ký ngay", command=save, bootstyle="success").pack(pady=20, fill='x')

if __name__ == '__main__':
    print("--- ĐANG KHỞI ĐỘNG ỨNG DỤNG... ---") # In ra để biết code đang chạy
    try:
        app = LoginWindow()
        app.mainloop()
    except Exception as e:
        print(f"LỖI KHỞI ĐỘNG: {e}")
        input("Nhấn Enter để thoát...")