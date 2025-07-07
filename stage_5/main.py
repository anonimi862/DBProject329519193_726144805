import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime, date
import sys
import os

# Import all screen modules
from screens.login_screen import LoginScreen
from screens.main_menu import MainMenu
from screens.warehouse_management import WarehouseManagement
from screens.parts_management import PartsManagement
from screens.orders_management import OrdersManagement
from screens.queries_screen import QueriesScreen
from screens.procedures_screen import ProceduresScreen

class WarehouseManagementSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Warehouse Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Database connection
        self.conn = None
        self.current_user = None
        
        # Style configuration
        self.setup_styles()
        
        # Start with login screen
        self.show_login()
        
    def setup_styles(self):
        """Configure ttk styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 24, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
        
    def connect_to_database(self, host, database, user, password):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            return True
        except psycopg2.Error as e:
            messagebox.showerror("Connection Error", f"Failed to connect to database:\n{str(e)}")
            return False
    
    def show_login(self):
        """Display login screen"""
        self.clear_window()
        LoginScreen(self.root, self)
    
    def show_main_menu(self):
        """Display main menu"""
        self.clear_window()
        MainMenu(self.root, self)
    
    def show_warehouse_management(self):
        """Display warehouse management screen"""
        self.clear_window()
        WarehouseManagement(self.root, self)
    
    def show_parts_management(self):
        """Display parts management screen"""
        self.clear_window()
        PartsManagement(self.root, self)
    
    def show_orders_management(self):
        """Display orders management screen"""
        self.clear_window()
        OrdersManagement(self.root, self)
    
    def show_queries_screen(self):
        """Display queries screen"""
        self.clear_window()
        QueriesScreen(self.root, self)
    
    def show_procedures_screen(self):
        """Display procedures screen"""
        self.clear_window()
        ProceduresScreen(self.root, self)
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def logout(self):
        """Logout and return to login screen"""
        if self.conn:
            self.conn.close()
        self.current_user = None
        self.show_login()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = WarehouseManagementSystem()
    app.run()