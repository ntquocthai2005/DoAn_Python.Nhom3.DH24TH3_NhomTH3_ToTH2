import sys
import csv # <--- Thư viện để xuất Excel
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime

# =============================================================================
# 0. HÀM CĂN GIỮA MÀN HÌNH
# =============================================================================
def center_window(win, w, h):
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = int((screen_w / 2) - (w / 2))
    y = int((screen_h / 2) - (h / 2))
    win.geometry(f'{w}x{h}+{x}+{y}')

# =============================================================================
# 1. KHO DỮ LIỆU ẢO (RAM)
# =============================================================================
class DataStore:
    def __init__(self):
        self.accounts = {'admin': '123', 'thinh': '1'}
        
        # Sản phẩm: Mã, Tên, Danh mục, Giá, Tồn, Ảnh
        self.products = [
            ('SP01', 'Laptop Gaming Dell', 'Laptop', 25000000.0, 10, ''),
            ('SP02', 'Chuột Logitech G304', 'Phụ kiện', 850000.0, 50, ''),
            ('SP03', 'iPhone 15 Pro Max', 'Điện thoại', 34000000.0, 5, ''),
            ('SP04', 'Màn hình LG 27 inch', 'Màn hình', 4500000.0, 12, '')
        ]
        
        # Khách hàng: Mã, Tên, SĐT, Địa chỉ
        self.customers = [
            ('KH01', 'Khách vãng lai', '0000000000', 'N/A'),
            ('KH02', 'Nguyễn Văn An', '0909123456', 'Hà Nội'),
            ('KH03', 'Trần Thị Bình', '0988777666', 'TP.HCM'),
            ('KH04', 'Lê Văn Cường', '0912345678', 'Đà Nẵng')
        ]
        
        # Nhân viên
        self.employees = [
            ('NV01', 'Admin Quản Lý', 'Quản lý', '2020-01-01', 20000000.0, 0),
            ('NV02', 'Phạm Nhân Viên', 'Sale', '2023-05-15', 8000000.0, 0)
        ]
        
        self.orders = []

store = DataStore()

# =============================================================================
# 2. GIAO DIỆN CHÍNH
# =============================================================================
class ModernApp:
    def __init__(self, root, current_user="Admin", logout_callback=None):
        self.root = root
        self.logout_callback = logout_callback
        self.style = tb.Style(theme='superhero')
        
        self.current_user_name = current_user
        self.is_admin = (current_user == 'admin')
        
        # Check lại quyền admin
        for e in store.employees:
            if e[1] == current_user and e[2] == 'Quản lý':
                self.is_admin = True; break

        title_role = "QUẢN TRỊ VIÊN" if self.is_admin else "NHÂN VIÊN"
        self.root.title(f'StockWise - {title_role}: {current_user}')
        
        center_window(self.root, 1280, 850)
        
        self.search_var = tk.StringVar()
        self.cart_items = []
        self.current_image_path = None 

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
        
        emp_title = "Quản lý Nhân viên" if self.is_admin else "Hồ sơ cá nhân"
        self.create_menu_btn(emp_title, "employees", "👔")
        
        tb.Button(self.sidebar, text=" Đăng xuất", bootstyle="danger-outline", command=self.perform_logout).pack(side='bottom', fill='x', padx=20, pady=20)

        self.content_area = tb.Frame(self.root, padding=20)
        self.content_area.pack(side='right', fill='both', expand=True)

        self.header = tb.Frame(self.content_area)
        self.header.pack(fill='x', pady=(0, 20))
        
        role = "ADMIN" if self.is_admin else "STAFF"
        color = "danger" if self.is_admin else "success"
        tb.Label(self.header, text=f"Xin chào, {self.current_user_name}", font=("Arial", 14, "bold"), bootstyle="primary").pack(side='left')
        tb.Label(self.header, text=f" [{role}]", font=("Arial", 10, "bold"), bootstyle=color).pack(side='left', padx=5)
        
        search_fr = tb.Frame(self.header); search_fr.pack(side='right')
        tb.Entry(search_fr, textvariable=self.search_var, width=30).pack(side='left', padx=5)
        tb.Button(search_fr, text="🔍", bootstyle="info", width=4, command=self.search_focused).pack(side='left')

        self.page_container = tb.Frame(self.content_area)
        self.page_container.pack(fill='both', expand=True)

    def perform_logout(self):
        self.root.destroy()
        if self.logout_callback: self.logout_callback()

    def create_menu_btn(self, text, key, icon):
        btn = tb.Button(self.sidebar, text=f" {icon}  {text}", bootstyle="secondary", command=lambda k=key: self.show_page(k))
        btn.pack(fill='x', pady=5, padx=10)
        self.btn_refs[key] = btn

    def show_page(self, key):
        for widget in self.page_container.winfo_children(): widget.destroy()
        for k, btn in self.btn_refs.items():
            btn.configure(bootstyle="primary" if k == key else "secondary")

        if key == 'dashboard': self.build_dashboard()
        elif key == 'sales': self.build_sales()
        elif key == 'products': self.build_products()
        elif key == 'customers': self.build_customers() 
        elif key == 'employees': self.build_employees()

    # --- 1. BÁN HÀNG ---
    def build_sales(self):
        self.cart_items = [] 
        f = self.page_container
        left = tb.Frame(f); left.pack(side='left', fill='both', expand=True, padx=(0, 20))
        right = tb.Frame(f, width=400, bootstyle="secondary"); right.pack(side='right', fill='y')

        tb.Label(left, text="TẠO ĐƠN HÀNG MỚI", font=("Bold", 20)).pack(anchor='w', pady=(0, 20))
        
        info_frame = tb.Labelframe(left, text="Thông tin", padding=15); info_frame.pack(fill='x', pady=5)
        
        tb.Label(info_frame, text="Khách hàng:").grid(row=0, column=0, sticky='w', pady=10)
        c_vals = [f"{c[0]} - {c[1]}" for c in store.customers]
        self.cb_cust = ttk.Combobox(info_frame, values=c_vals, width=35); self.cb_cust.grid(row=0, column=1, padx=10)
        if c_vals: self.cb_cust.current(0)

        tb.Label(info_frame, text="Sản phẩm:").grid(row=1, column=0, sticky='w', pady=10)
        p_vals = [f"{p[0]} - {p[1]}" for p in store.products]
        self.cb_prod = ttk.Combobox(info_frame, values=p_vals, width=35); self.cb_prod.grid(row=1, column=1, padx=10)
        self.cb_prod.bind("<<ComboboxSelected>>", self.on_prod_select)

        self.lbl_info = tb.Label(info_frame, text="Giá: 0 | Tồn: 0", bootstyle="info")
        self.lbl_info.grid(row=2, column=1, sticky='w', padx=10, pady=5)

        tb.Label(info_frame, text="Số lượng:").grid(row=3, column=0, sticky='w', pady=10)
        self.spin_qty = tb.Spinbox(info_frame, from_=1, to=999, width=10); self.spin_qty.grid(row=3, column=1, sticky='w', padx=10)
        self.spin_qty.set(1)

        tb.Button(info_frame, text="THÊM VÀO GIỎ ⬇", bootstyle="success", command=self.add_to_cart).grid(row=4, column=1, sticky='e', pady=10)

        tb.Label(right, text="GIỎ HÀNG", font=("Bold", 18), bootstyle="inverse-secondary").pack(pady=20)
        cols = ('name', 'qty', 'total')
        self.cart_tree = ttk.Treeview(right, columns=cols, show='headings', height=15)
        self.cart_tree.heading('name', text='Tên SP'); self.cart_tree.column('name', width=120)
        self.cart_tree.heading('qty', text='SL'); self.cart_tree.column('qty', width=40)
        self.cart_tree.heading('total', text='Thành tiền'); self.cart_tree.column('total', width=100)
        self.cart_tree.pack(fill='both', expand=True, padx=10)

        self.lbl_total = tb.Label(right, text="TỔNG: 0 VNĐ", font=("Bold", 22), bootstyle="warning-inverse")
        self.lbl_total.pack(pady=20)
        
        tb.Button(right, text="THANH TOÁN", bootstyle="success", width=25, command=self.checkout).pack(pady=5)
        tb.Button(right, text="Hủy đơn", bootstyle="danger-outline", width=25, command=self.clear_cart).pack(pady=5)

    def on_prod_select(self, event):
        idx = self.cb_prod.current()
        if idx >= 0:
            p = store.products[idx]
            self.lbl_info.config(text=f"Giá: {p[3]:,.0f} | Tồn: {p[4]}")

    def add_to_cart(self):
        idx = self.cb_prod.current()
        if idx < 0: return
        qty = int(self.spin_qty.get())
        p = store.products[idx]
        if qty > p[4]: messagebox.showwarning("Hết hàng", f"Kho chỉ còn {p[4]}!"); return
        total = p[3] * qty
        self.cart_items.append({'name': p[1], 'qty': qty, 'price': p[3], 'total': total, 'idx': idx})
        self.refresh_cart()

    def refresh_cart(self):
        for r in self.cart_tree.get_children(): self.cart_tree.delete(r)
        grand = 0
        for i in self.cart_items:
            self.cart_tree.insert('', 'end', values=(i['name'], i['qty'], f"{i['total']:,.0f}"))
            grand += i['total']
        self.lbl_total.config(text=f"TỔNG: {grand:,.0f} VNĐ")

    def clear_cart(self): self.cart_items = []; self.refresh_cart()

    def checkout(self):
        if not self.cart_items: return
        grand = 0
        for item in self.cart_items:
            idx = item['idx']
            p = store.products[idx]
            new_stock = p[4] - item['qty']
            store.products[idx] = (p[0], p[1], p[2], p[3], new_stock, p[5])
            grand += item['total']
        
        store.orders.append({'date': datetime.now().strftime("%Y-%m-%d"), 'total': grand, 'by': self.current_user_name})
        
        for i, emp in enumerate(store.employees):
            if emp[1] == self.current_user_name:
                store.employees[i] = (emp[0], emp[1], emp[2], emp[3], emp[4], emp[5] + 1)

        messagebox.showinfo("Thành công", f"Đã thanh toán {grand:,.0f} VNĐ"); self.clear_cart(); self.on_prod_select(None)

    # --- 2. DASHBOARD ---
    def build_dashboard(self):
        tb.Label(self.page_container, text="TỔNG QUAN KINH DOANH", font=("Helvetica", 20, "bold")).pack(anchor='w', pady=(0, 20))
        rev = sum(o['total'] for o in store.orders)
        cards = tb.Frame(self.page_container); cards.pack(fill='x')
        self.create_card(cards, "SẢN PHẨM", f"{len(store.products)}", "📦", "info")
        self.create_card(cards, "DOANH THU", f"$ {rev:,.0f}", "💰", "success")
        self.create_card(cards, "KHÁCH HÀNG", f"{len(store.customers)}", "👥", "warning")
        self.create_card(cards, "ĐƠN HÀNG", f"{len(store.orders)}", "🧾", "danger")
        
        graph = tb.Labelframe(self.page_container, text="Biểu đồ", padding=10, bootstyle="secondary"); graph.pack(fill='x', expand=False, pady=20)
        self.draw_chart(graph)

    def create_card(self, parent, title, value, icon, style):
        card = tb.Frame(parent, bootstyle=style, padding=15); card.pack(side='left', fill='both', expand=True, padx=10)
        tb.Label(card, text=icon, font=("Segoe UI Emoji", 30), bootstyle=f"{style}-inverse").pack(side='left', padx=(0, 15))
        right = tb.Frame(card, bootstyle=style); right.pack(side='left', fill='x')
        tb.Label(right, text=title, font=("Bold", 10), bootstyle=f"{style}-inverse").pack(anchor='w')
        tb.Label(right, text=value, font=("Bold", 20), bootstyle=f"{style}-inverse").pack(anchor='w')

    def draw_chart(self, parent):
        fig = Figure(figsize=(7, 4.7), dpi=100); ax = fig.add_subplot(111)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']; sales = [15, 22, 18, 25, 30]
        fig.patch.set_facecolor('#2b3e50')
        ax.pie(sales, labels=months, autopct='%1.1f%%', textprops={'color':"w"})
        FigureCanvasTkAgg(fig, master=parent).get_tk_widget().pack(fill='both', expand=True)

    def search_focused(self):
        query = self.search_var.get().strip().lower()
        if not query: messagebox.showinfo("TB", "Nhập từ khóa!"); return
        for widget in self.page_container.winfo_children(): widget.destroy()
        
        head = tb.Frame(self.page_container); head.pack(fill='x', pady=10)
        tb.Button(head, text="⬅ Quay lại", bootstyle="outline-secondary", command=lambda: self.show_page('dashboard')).pack(side='left')
        
        found = None
        for p in store.products:
            if query in p[0].lower() or query in p[1].lower(): found = p; break
        
        if found:
            card = tb.Frame(self.page_container, bootstyle="secondary", padding=30); card.pack(fill='both', expand=True, padx=50, pady=20)
            left = tb.Frame(card, bootstyle="secondary"); left.pack(side='left', fill='y', padx=40)
            try:
                load = Image.open(found[5]).resize((250, 250)) if found[5] else None
                if load: render = ImageTk.PhotoImage(load); lbl = tb.Label(left, image=render); lbl.image=render; lbl.pack()
                else: tb.Label(left, text="NO IMAGE", font=("Bold", 14)).pack(pady=80)
            except: tb.Label(left, text="Error", font=("Bold", 14)).pack(pady=80)
            right = tb.Frame(card, bootstyle="secondary"); right.pack(side='left', fill='both', expand=True)
            tb.Label(right, text=found[1], font=("Bold", 26), bootstyle="warning-inverse").pack(anchor='w')
            tb.Label(right, text=f"Giá: {found[3]:,.0f} VNĐ", font=("Bold", 18), bootstyle="success-inverse").pack(anchor='w', pady=10)
            tb.Label(right, text=f"Tồn kho: {found[4]}", font=("Bold", 18), bootstyle="danger-inverse").pack(anchor='w')
        else: tb.Label(self.page_container, text="Không tìm thấy!", font=("Bold", 20)).pack(pady=50)

    # ================= 3. QUẢN LÝ SẢN PHẨM =================
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
        tb.Button(form, text='Chọn ảnh', command=self.choose_img).grid(row=5,column=1,pady=5)
        self.p_preview = ttk.Label(form, text="No Image"); self.p_preview.grid(row=6,column=0,columnspan=2)

        btns = ttk.Frame(left); btns.pack(fill='x', pady=10)
        def cp(cmd): 
            if self.is_admin: cmd()
            else: messagebox.showerror("Từ chối", "Chỉ Admin mới được sửa!")
        tb.Button(btns, text='Thêm', bootstyle='success', command=lambda: cp(self.add_p)).pack(side='left', padx=2, expand=True)
        tb.Button(btns, text='Sửa', bootstyle='warning', command=lambda: cp(self.edit_p)).pack(side='left', padx=2, expand=True)
        tb.Button(btns, text='Xóa', bootstyle='danger', command=lambda: cp(self.del_p)).pack(side='left', padx=2, expand=True)
        tb.Button(btns, text='Reset', bootstyle='info', command=self.reset_p).pack(side='left', padx=2, expand=True)

        cols = ('code','name','cat','price','stock','img')
        self.tree = ttk.Treeview(right, columns=cols, show='headings'); self.tree.pack(fill='both', expand=True)
        self.tree.heading('code', text='MÃ'); self.tree.column('code', width=50)
        self.tree.heading('name', text='TÊN SP'); self.tree.column('name', width=150)
        self.tree.heading('cat', text='LOẠI'); self.tree.column('cat', width=80)
        self.tree.heading('price', text='GIÁ'); self.tree.column('price', width=80)
        self.tree.heading('stock', text='TỒN'); self.tree.column('stock', width=50)
        self.tree.column('img', width=0, stretch=False)
        self.tree.bind('<<TreeviewSelect>>', self.on_select_p); self.refresh_p()

    def choose_img(self):
        path = filedialog.askopenfilename()
        if path:
            self.current_image_path = path
            try: img = Image.open(path).resize((100,100)); self.tkimg = ImageTk.PhotoImage(img); self.p_preview.config(image=self.tkimg, text="")
            except: pass
    def add_p(self): store.products.append((self.p_code.get(), self.p_name.get(), self.p_cat.get(), float(self.p_price.get() or 0), int(self.p_stock.get() or 0), self.current_image_path)); self.refresh_p(); self.reset_p()
    def edit_p(self): sel=self.tree.selection(); idx=self.tree.index(sel[0]); store.products[idx]=(self.p_code.get(), self.p_name.get(), self.p_cat.get(), float(self.p_price.get() or 0), int(self.p_stock.get() or 0), self.current_image_path); self.refresh_p()
    def del_p(self): 
        sel=self.tree.selection()
        if sel and messagebox.askyesno('Xác nhận', 'Bạn có chắc chắn muốn xóa sản phẩm này không?'): del store.products[self.tree.index(sel[0])]; self.refresh_p()
    def reset_p(self):
        for w in (self.p_code, self.p_name, self.p_cat, self.p_price, self.p_stock): w.delete(0, 'end')
        self.p_preview.config(image='', text="No Image"); self.current_image_path=None
    def refresh_p(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for p in store.products: 
            d = list(p); d[3] = f"{p[3]:,.0f}"
            self.tree.insert('', 'end', values=d)
    def on_select_p(self, event):
        sel=self.tree.selection(); val=self.tree.item(sel[0])['values']
        self.p_code.delete(0,'end'); self.p_code.insert(0,val[0])
        self.p_name.delete(0,'end'); self.p_name.insert(0,val[1])
        self.p_cat.delete(0,'end'); self.p_cat.insert(0,val[2])
        self.p_price.delete(0,'end'); self.p_price.insert(0,str(val[3]).replace(',', ''))
        self.p_stock.delete(0,'end'); self.p_stock.insert(0,val[4])
        if len(val)>5 and val[5]:
            try: img=Image.open(val[5]).resize((100,100)); self.tkimg=ImageTk.PhotoImage(img); self.p_preview.config(image=self.tkimg, text="")
            except: pass

    # ================= 4. KHÁCH HÀNG (CÓ XUẤT EXCEL) =================
    def build_customers(self):
        f = self.page_container; tb.Label(f, text="QUẢN LÝ KHÁCH HÀNG", font=("Bold", 20)).pack(anchor='w', pady=(0, 20))
        content = tb.Frame(f); content.pack(fill='both', expand=True)
        left = ttk.Frame(content, width=400); left.pack(side='left', fill='y', padx=10)
        right = ttk.Frame(content); right.pack(side='right', fill='both', expand=True, padx=10)

        form = tb.Labelframe(left, text='Thông tin', padding=10); form.pack(fill='x')
        ttk.Label(form, text='Mã KH:').grid(row=0,column=0,pady=5); self.c_id = tb.Entry(form, width=30); self.c_id.grid(row=0,column=1)
        ttk.Label(form, text='Tên:').grid(row=1,column=0,pady=5); self.c_name = tb.Entry(form, width=30); self.c_name.grid(row=1,column=1)
        ttk.Label(form, text='SĐT:').grid(row=2,column=0,pady=5); self.c_phone = tb.Entry(form, width=30); self.c_phone.grid(row=2,column=1)
        ttk.Label(form, text='Địa chỉ:').grid(row=3,column=0,pady=5); self.c_addr = tb.Entry(form, width=30); self.c_addr.grid(row=3,column=1)

        btns = ttk.Frame(left); btns.pack(fill='x', pady=20)
        
        # --- NÚT XUẤT EXCEL ---
        def export_excel():
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")])
            if not path: return
            try:
                with open(path, mode='w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Mã KH", "Họ Tên", "SĐT", "Địa Chỉ"])
                    for c in store.customers: writer.writerow(c)
                messagebox.showinfo("Thành công", "Đã xuất file Excel!")
            except Exception as e: messagebox.showerror("Lỗi", str(e))
        
        tb.Button(btns, text='Xuất Excel', bootstyle='success', command=export_excel).pack(fill='x', pady=5)
        # ----------------------

        def cp(cmd): 
            if self.is_admin: cmd()
            else: messagebox.showerror("Từ chối", "Chỉ Admin mới được sửa!")
        tb.Button(btns, text='Thêm', bootstyle='primary', command=lambda: cp(self.add_c)).pack(side='left', padx=2, expand=True)
        tb.Button(btns, text='Sửa', bootstyle='warning', command=lambda: cp(self.edit_c)).pack(side='left', padx=2, expand=True)
        tb.Button(btns, text='Xóa', bootstyle='danger', command=lambda: cp(self.del_c)).pack(side='left', padx=2, expand=True)
        tb.Button(btns, text='Reset', bootstyle='info', command=self.reset_c).pack(side='left', padx=2, expand=True)

        cols = ('id', 'name', 'phone', 'addr')
        self.c_tree = ttk.Treeview(right, columns=cols, show='headings'); self.c_tree.pack(fill='both', expand=True)
        self.c_tree.heading('id', text='MÃ KH'); self.c_tree.column('id', width=70)
        self.c_tree.heading('name', text='HỌ TÊN'); self.c_tree.column('name', width=150)
        self.c_tree.heading('phone', text='SĐT'); self.c_tree.column('phone', width=100)
        self.c_tree.heading('addr', text='ĐỊA CHỈ'); self.c_tree.column('addr', width=150)
        self.c_tree.bind('<<TreeviewSelect>>', self.on_select_c); self.refresh_c()

    def add_c(self): store.customers.append((self.c_id.get(), self.c_name.get(), self.c_phone.get(), self.c_addr.get())); self.refresh_c(); self.reset_c()
    def edit_c(self): sel=self.c_tree.selection(); idx=self.c_tree.index(sel[0]); store.customers[idx]=(self.c_id.get(), self.c_name.get(), self.c_phone.get(), self.c_addr.get()); self.refresh_c()
    def del_c(self): 
        sel=self.c_tree.selection()
        if sel and messagebox.askyesno('Xác nhận', 'Bạn có chắc chắn muốn xóa khách hàng này không?'): del store.customers[self.c_tree.index(sel[0])]; self.refresh_c()
    def reset_c(self): self.c_id.delete(0,'end'); self.c_name.delete(0,'end'); self.c_phone.delete(0,'end'); self.c_addr.delete(0,'end')
    def refresh_c(self):
        for r in self.c_tree.get_children(): self.c_tree.delete(r)
        for c in store.customers: self.c_tree.insert('', 'end', values=c)
    def on_select_c(self, event):
        sel=self.c_tree.selection(); val=self.c_tree.item(sel[0])['values']
        self.c_id.delete(0,'end'); self.c_id.insert(0,val[0])
        self.c_name.delete(0,'end'); self.c_name.insert(0,val[1])
        self.c_phone.delete(0,'end'); self.c_phone.insert(0,str(val[2]))
        self.c_addr.delete(0,'end'); self.c_addr.insert(0,val[3])

    # ================= 5. NHÂN VIÊN =================
    def build_employees(self):
        f = self.page_container
        if self.is_admin:
            tb.Label(f, text="QUẢN LÝ NHÂN VIÊN (Admin)", font=("Bold", 20), bootstyle="danger").pack(anchor='w', pady=(0, 20))
            content = tb.Frame(f); content.pack(fill='both', expand=True)
            left = ttk.Frame(content, width=400); left.pack(side='left', fill='y', padx=10)
            right = ttk.Frame(content); right.pack(side='right', fill='both', expand=True, padx=10)

            form = tb.Labelframe(left, text='Thông tin', padding=10); form.pack(fill='x')
            ttk.Label(form, text='Mã NV:').grid(row=0,column=0,pady=5); self.e_id = tb.Entry(form, width=30); self.e_id.grid(row=0,column=1)
            ttk.Label(form, text='Họ tên:').grid(row=1,column=0,pady=5); self.e_name = tb.Entry(form, width=30); self.e_name.grid(row=1,column=1)
            ttk.Label(form, text='Chức vụ:').grid(row=2,column=0,pady=5); self.e_role = ttk.Combobox(form, values=['Quản lý','Sale'], width=28); self.e_role.grid(row=2,column=1); self.e_role.current(1)
            ttk.Label(form, text='Lương:').grid(row=4,column=0,pady=5); self.e_salary = tb.Entry(form, width=30); self.e_salary.grid(row=4,column=1)

            btns = ttk.Frame(left); btns.pack(fill='x', pady=20)
            tb.Button(btns, text='Thêm & Tạo TK', bootstyle='success', command=self.add_e).pack(side='left', padx=2, expand=True)
            tb.Button(btns, text='Sửa', bootstyle='warning', command=self.edit_e).pack(side='left', padx=2, expand=True)
            tb.Button(btns, text='Xóa', bootstyle='danger', command=self.del_e).pack(side='left', padx=2, expand=True)
            tb.Button(btns, text='Reset', bootstyle='info', command=self.reset_e).pack(side='left', padx=2, expand=True)

            cols = ('id', 'name', 'role', 'date', 'salary')
            self.e_tree = ttk.Treeview(right, columns=cols, show='headings'); self.e_tree.pack(fill='both', expand=True)
            self.e_tree.heading('id', text='MÃ'); self.e_tree.column('id', width=70)
            self.e_tree.heading('name', text='TÊN'); self.e_tree.column('name', width=150)
            self.e_tree.heading('role', text='CHỨC VỤ'); self.e_tree.column('role', width=100)
            self.e_tree.heading('date', text='NGÀY VÀO'); self.e_tree.column('date', width=100)
            self.e_tree.heading('salary', text='LƯƠNG'); self.e_tree.column('salary', width=120)
            for e in store.employees: d = list(e[:5]); d[4] = f"{e[4]:,.0f}"; self.e_tree.insert('', 'end', values=d)
            self.e_tree.bind('<<TreeviewSelect>>', self.on_select_e)
        else:
            tb.Label(f, text="HỒ SƠ CÁ NHÂN", font=("Bold", 20), bootstyle="success").pack(anchor='w', pady=(0, 20))
            me = next((e for e in store.employees if e[1] == self.current_user_name), None)
            if me:
                card = tb.Frame(f, bootstyle="secondary", padding=40); card.pack(fill='both', expand=True, padx=50)
                tb.Label(card, text=f"Xin chào: {me[1]}", font=("Bold", 24), bootstyle="inverse-secondary").pack(pady=10)
                tb.Label(card, text=f"Chức vụ: {me[2]}", font=("Arial", 18), bootstyle="inverse-secondary").pack()
                tb.Label(card, text=f"Lương: {me[4]:,.0f} VNĐ", font=("Arial", 18), bootstyle="inverse-secondary").pack()
                tb.Label(card, text=f"Số đơn đã bán: {me[5]}", font=("Bold", 18), bootstyle="success").pack(pady=20)

    def add_e(self):
        try: s=float(self.e_salary.get())
        except: s=0.0
        nm=self.e_name.get()
        store.employees.append((self.e_id.get(), nm, self.e_role.get(), datetime.now().strftime("%Y-%m-%d"), s, 0))
        store.accounts[nm]='1'
        # Fix lỗi chồng bảng
        for widget in self.page_container.winfo_children(): widget.destroy()
        self.build_employees()
        messagebox.showinfo("OK", f"Đã tạo user: {nm}\nPass: 1")

    def del_e(self):
        sel=self.e_tree.selection()
        if sel and messagebox.askyesno('Xác nhận', 'Bạn có chắc chắn muốn xóa nhân viên này không?'): 
            emp_name = store.employees[self.e_tree.index(sel[0])][1]
            if emp_name in store.accounts: del store.accounts[emp_name]
            del store.employees[self.e_tree.index(sel[0])]
            for widget in self.page_container.winfo_children(): widget.destroy()
            self.build_employees()
            messagebox.showinfo("Thành công", "Đã xóa nhân viên!")

    def edit_e(self):
        sel = self.e_tree.selection()
        if not sel: 
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn nhân viên cần sửa!")
            return
        idx = self.e_tree.index(sel[0])
        old_data = store.employees[idx]; old_name = old_data[1]; new_name = self.e_name.get().strip()
        try: salary = float(self.e_salary.get())
        except: salary = 0.0
        store.employees[idx] = (self.e_id.get(), new_name, self.e_role.get(), old_data[3], salary, old_data[5])
        if old_name != new_name and old_name in store.accounts:
            current_pass = store.accounts[old_name]; del store.accounts[old_name]; store.accounts[new_name] = current_pass
        for widget in self.page_container.winfo_children(): widget.destroy()
        self.build_employees()
        messagebox.showinfo("Thành công", f"Đã cập nhật!\nTài khoản mới: {new_name}")

    def reset_e(self):
        self.e_id.delete(0,'end'); self.e_name.delete(0,'end'); self.e_salary.delete(0,'end')

    def on_select_e(self, event):
        sel = self.e_tree.selection()
        if not sel: return
        val = self.e_tree.item(sel[0])['values']
        self.e_id.delete(0,'end'); self.e_id.insert(0, val[0])
        self.e_name.delete(0,'end'); self.e_name.insert(0, val[1])
        self.e_role.set(val[2])
        s_str = str(val[4]).replace(',', '')
        self.e_salary.delete(0,'end'); self.e_salary.insert(0, s_str)

# ------------------------ LOGIN ------------------------
class LoginWindow(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero"); self.title('Đăng nhập'); self.geometry('400x500')
        
        # Căn giữa
        w, h = 400, 500
        ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (ws/2)-(w/2), (hs/2)-(h/2)
        self.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

        tb.Label(self, text='STOCKWISE', font=('Impact', 28), bootstyle="primary").pack(pady=30)
        tb.Label(self, text='Tài khoản:').pack(anchor='w'); self.u = tb.Entry(self); self.u.pack(pady=5); self.u.focus()
        tb.Label(self, text='Mật khẩu:').pack(anchor='w'); self.p = tb.Entry(self, show="*"); self.p.pack(pady=5)
        tb.Button(self, text='Đăng nhập', bootstyle='success', command=self.login).pack(fill='x', pady=20)
        tb.Button(self, text='Đăng ký tài khoản', bootstyle='info-outline', command=self.reg).pack(fill='x')

    def login(self):
        u=self.u.get().strip(); p=self.p.get().strip()
        if u in store.accounts and store.accounts[u]==p:
            self.withdraw()
            def show(): self.deiconify(); self.u.delete(0,'end'); self.p.delete(0,'end'); self.u.focus()
            ModernApp(tb.Toplevel(self), current_user=u, logout_callback=show)
        else: messagebox.showerror('Lỗi', 'Sai thông tin!')

    def reg(self):
        r=tb.Toplevel(self); r.geometry("350x550"); r.title("Đăng ký")
        
        w, h = 350, 550
        ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (ws/2)-(w/2), (hs/2)-(h/2)
        r.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

        pnl = tb.Frame(r, padding=20); pnl.pack(fill='both', expand=True)
        tb.Label(pnl, text="ĐĂNG KÝ", font=("Bold", 14), bootstyle="info").pack(pady=10)
        tb.Label(pnl, text="Tài khoản:").pack(anchor='w'); u=tb.Entry(pnl); u.pack(fill='x')
        tb.Label(pnl, text="Mật khẩu:").pack(anchor='w'); p=tb.Entry(pnl); p.pack(fill='x')
        tb.Separator(pnl).pack(fill='x', pady=10)
        tb.Label(pnl, text="Họ tên:").pack(anchor='w'); n=tb.Entry(pnl); n.pack(fill='x')
        
        tb.Separator(pnl).pack(fill='x', pady=10)
        tb.Label(pnl, text="XÁC NHẬN ADMIN:", bootstyle="danger").pack(anchor='w')
        ad=tb.Entry(pnl, show="*"); ad.pack(fill='x')
        
        def save():
            if ad.get() != '123': messagebox.showerror("Lỗi", "Sai mật khẩu Admin!"); return
            uv=u.get().strip(); pv=p.get().strip(); nv=n.get().strip()
            if not uv or not pv or not nv: messagebox.showwarning("Lỗi", "Nhập đủ!"); return
            store.accounts[uv]=pv
            nid=f"NV{len(store.employees)+1:02d}"
            store.employees.append((nid, nv, 'Nhân viên', datetime.now().strftime("%Y-%m-%d"), 5000000.0, 0))
            messagebox.showinfo("Thành công", f"Đã đăng ký!\nMã NV: {nid}"); r.destroy()
            
        tb.Button(pnl, text="Đăng ký ngay", command=save, bootstyle="success").pack(pady=20, fill='x')

if __name__ == '__main__':
    app = LoginWindow()
    app.mainloop()