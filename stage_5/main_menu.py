import tkinter as tk
from tkinter import ttk

class MainMenu:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text="Main Menu", style='Title.TLabel')
        title_label.pack(side='left')
        
        logout_btn = ttk.Button(header_frame, text="Logout", command=self.app.logout)
        logout_btn.pack(side='right')
        
        user_label = ttk.Label(header_frame, text=f"User: {self.app.current_user}")
        user_label.pack(side='right', padx=20)
        
        # Main content
        content_frame = ttk.Frame(self.parent, padding="40")
        content_frame.pack(expand=True, fill='both')
        
        # Create menu buttons
        buttons = [
            ("Warehouse Management", self.app.show_warehouse_management, 
             "Manage warehouses, view capacity, and employee assignments"),
            ("Parts Management", self.app.show_parts_management,
             "Manage parts inventory, suppliers, and pricing"),
            ("Orders Management", self.app.show_orders_management,
             "Process orders, track deliveries, and manage suppliers"),
            ("Run Queries", self.app.show_queries_screen,
             "Execute predefined queries and view reports"),
            ("Run Procedures", self.app.show_procedures_screen,
             "Execute system procedures and functions")
        ]
        
        for i, (text, command, description) in enumerate(buttons):
            btn_frame = ttk.Frame(content_frame)
            btn_frame.grid(row=i//2, column=i%2, padx=20, pady=20, sticky='ew')
            
            btn = ttk.Button(btn_frame, text=text, command=command,
                           style='Action.TButton', width=25)
            btn.pack(pady=5)
            
            desc_label = ttk.Label(btn_frame, text=description, 
                                 wraplength=200, justify='center')
            desc_label.pack()
        
        # Configure grid weights
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)