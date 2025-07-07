import tkinter as tk
from tkinter import ttk, messagebox

class LoginScreen:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.parent, padding="50")
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        title_label = ttk.Label(main_frame, text="Warehouse Management System", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=30)
        
        # Login form
        ttk.Label(main_frame, text="Host:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.host_entry = ttk.Entry(main_frame, width=30)
        self.host_entry.grid(row=1, column=1, padx=5, pady=5)
        self.host_entry.insert(0, "localhost")
        
        ttk.Label(main_frame, text="Database:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.db_entry = ttk.Entry(main_frame, width=30)
        self.db_entry.grid(row=2, column=1, padx=5, pady=5)
        self.db_entry.insert(0, "warehouse_db")
        
        ttk.Label(main_frame, text="Username:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.user_entry = ttk.Entry(main_frame, width=30)
        self.user_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Password:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.pass_entry = ttk.Entry(main_frame, width=30, show="*")
        self.pass_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # Login button
        login_btn = ttk.Button(main_frame, text="Login", command=self.login,
                              style='Action.TButton')
        login_btn.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Bind Enter key
        self.parent.bind('<Return>', lambda e: self.login())
        
    def login(self):
        host = self.host_entry.get()
        database = self.db_entry.get()
        user = self.user_entry.get()
        password = self.pass_entry.get()
        
        if not all([host, database, user, password]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        if self.app.connect_to_database(host, database, user, password):
            self.app.current_user = user
            self.app.show_main_menu()