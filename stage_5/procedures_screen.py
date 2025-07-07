import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import psycopg2
from datetime import date

class ProceduresScreen:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="Run Procedures & Functions", 
                 style='Title.TLabel').pack(side='left')
        ttk.Button(header_frame, text="Back to Menu", 
                  command=self.app.show_main_menu).pack(side='right')
        
        # Main content with notebook
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Create tabs
        self.create_functions_tab()
        self.create_procedures_tab()
        
    def create_functions_tab(self):
        functions_frame = ttk.Frame(self.notebook)
        self.notebook.add(functions_frame, text="Functions")
        
        # Function 1: Analyze Warehouse Operations
        func1_frame = ttk.LabelFrame(functions_frame, text="Analyze Warehouse Operations", padding="10")
        func1_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(func1_frame, text="Select Warehouse:").grid(row=0, column=0, padx=5, pady=5)
        self.warehouse_combo = ttk.Combobox(func1_frame, width=30)
        self.warehouse_combo.grid(row=0, column=1, padx=5, pady=5)
        self.load_warehouses()
        
        ttk.Button(func1_frame, text="Analyze", command=self.analyze_warehouse,
                  style='Action.TButton').grid(row=0, column=2, padx=5, pady=5)
        
        # Function 2: Get Maintenance Schedule
        func2_frame = ttk.LabelFrame(functions_frame, text="Get Maintenance Schedule", padding="10")
        func2_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(func2_frame, text="Days Ahead:").grid(row=0, column=0, padx=5, pady=5)
        self.days_ahead = ttk.Spinbox(func2_frame, from_=1, to=365, width=10)
        self.days_ahead.set(30)
        self.days_ahead.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(func2_frame, text="Location (optional):").grid(row=0, column=2, padx=5, pady=5)
        self.location_entry = ttk.Entry(func2_frame, width=20)
        self.location_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(func2_frame, text="Get Schedule", command=self.get_maintenance_schedule,
                  style='Action.TButton').grid(row=0, column=4, padx=5, pady=5)
                # Results area
        results_frame = ttk.LabelFrame(functions_frame, text="Function Results", padding="10")
        results_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.func_results = scrolledtext.ScrolledText(results_frame, height=15, width=80)
        self.func_results.pack(expand=True, fill='both')
        
    def create_procedures_tab(self):
        procedures_frame = ttk.Frame(self.notebook)
        self.notebook.add(procedures_frame, text="Procedures")
        
        # Procedure 1: Process Pending Orders
        proc1_frame = ttk.LabelFrame(procedures_frame, text="Process Pending Orders", padding="10")
        proc1_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(proc1_frame, text="Process Date:").grid(row=0, column=0, padx=5, pady=5)
        self.process_date = ttk.Entry(proc1_frame, width=15)
        self.process_date.insert(0, str(date.today()))
        self.process_date.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(proc1_frame, text="Max Orders:").grid(row=0, column=2, padx=5, pady=5)
        self.max_orders = ttk.Spinbox(proc1_frame, from_=1, to=1000, width=10)
        self.max_orders.set(100)
        self.max_orders.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(proc1_frame, text="Process Orders", command=self.process_orders,
                  style='Action.TButton').grid(row=0, column=4, padx=5, pady=5)
        
        # Procedure 2: Optimize Fleet Assignment
        proc2_frame = ttk.LabelFrame(procedures_frame, text="Optimize Fleet Assignment", padding="10")
        proc2_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(proc2_frame, text="Select Operator:").grid(row=0, column=0, padx=5, pady=5)
        self.operator_combo = ttk.Combobox(proc2_frame, width=30)
        self.operator_combo.grid(row=0, column=1, padx=5, pady=5)
        self.load_operators()
        
        self.rebalance_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(proc2_frame, text="Rebalance Assignments", 
                       variable=self.rebalance_var).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(proc2_frame, text="Optimize", command=self.optimize_fleet,
                  style='Action.TButton').grid(row=0, column=3, padx=5, pady=5)
        
        # Results area
        results_frame = ttk.LabelFrame(procedures_frame, text="Procedure Output", padding="10")
        results_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.proc_results = scrolledtext.ScrolledText(results_frame, height=15, width=80)
        self.proc_results.pack(expand=True, fill='both')
        
    def load_warehouses(self):
        """Load warehouses for combobox"""
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT warehouse_id, location FROM warehouses ORDER BY warehouse_id")
            warehouses = cursor.fetchall()
            cursor.close()
            
            warehouse_list = [f"{w[0]} - {w[1]}" for w in warehouses]
            self.warehouse_combo['values'] = warehouse_list
            if warehouse_list:
                self.warehouse_combo.set(warehouse_list[0])
                
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"Failed to load warehouses:\n{str(e)}")
    
    def load_operators(self):
        """Load operators for combobox"""
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT operator_id, name FROM operator ORDER BY operator_id")
            operators = cursor.fetchall()
            cursor.close()
            
            operator_list = ["All Operators"] + [f"{o[0]} - {o[1]}" for o in operators]
            self.operator_combo['values'] = operator_list
            self.operator_combo.set(operator_list[0])
                
        except psycopg2.Error as e:
            # If operator table doesn't exist, just set empty
            self.operator_combo['values'] = ["No operators found"]
            self.operator_combo.set("No operators found")
    
    def analyze_warehouse(self):
        """Call AnalyzeWarehouseOperations function"""
        if not self.warehouse_combo.get():
            messagebox.showwarning("No Selection", "Please select a warehouse")
            return
        
        warehouse_id = int(self.warehouse_combo.get().split(' - ')[0])
        
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT * FROM AnalyzeWarehouseOperations(%s)", (warehouse_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                output = f"""
Warehouse Analysis Results:
========================
Warehouse ID: {result[0]}
Location: {result[1]}
Total Parts Value: ${result[2]:,.2f}
Unique Parts: {result[3]}
Total Quantity: {result[4]:,}
Employee Count: {result[5]}
Train Count: {result[6]}
Active Customers: {result[7]}
Pending Orders: {result[8]}
Capacity Usage: {result[9]}%

Analysis completed successfully!
"""
                self.func_results.delete(1.0, tk.END)
                self.func_results.insert(1.0, output)
            else:
                self.func_results.delete(1.0, tk.END)
                self.func_results.insert(1.0, "No results returned from function.")
                
        except psycopg2.Error as e:
            messagebox.showerror("Function Error", f"Failed to execute function:\n{str(e)}")
    
    def get_maintenance_schedule(self):
        """Call GetMaintenanceSchedule function"""
        try:
            days = int(self.days_ahead.get())
            location = self.location_entry.get() or None
            
            cursor = self.app.conn.cursor()
            
            # Call function that returns refcursor
            cursor.execute("SELECT GetMaintenanceSchedule(%s, %s)", (days, location))
            cursor_name = cursor.fetchone()[0]
            
            # Fetch from the returned cursor
            cursor.execute(f"FETCH ALL FROM \"{cursor_name}\"")
            results = cursor.fetchall()
            
            output = f"Maintenance Schedule (Next {days} days)\n"
            output += "=" * 50 + "\n\n"
            
            if results:
                for row in results:
                    output += f"Type: {row[0]}\n"
                    output += f"ID: {row[1]}, Model: {row[2]}, Year: {row[3]}\n"
                    output += f"Last Check: {row[4]}, Next Check: {row[5]}\n"
                    output += f"Days Until: {row[6]}, Location: {row[7]}\n"
                    output += f"Available Staff: {row[8]}, Priority: {row[9]}\n"
                    output += "-" * 30 + "\n"
            else:
                output += "No maintenance required in the specified period.\n"
            
            cursor.close()
            
            self.func_results.delete(1.0, tk.END)
            self.func_results.insert(1.0, output)
            
        except Exception as e:
            messagebox.showerror("Function Error", f"Failed to execute function:\n{str(e)}")
    
    def process_orders(self):
        """Call ProcessPendingOrders procedure"""
        try:
            process_date = self.process_date.get()
            max_orders = int(self.max_orders.get())
            
            cursor = self.app.conn.cursor()
            
            # Capture notices
            self.app.conn.notices = []
            
            cursor.execute("CALL ProcessPendingOrders(%s, %s)", (process_date, max_orders))
            self.app.conn.commit()
            
            # Get notices
            output = "Process Pending Orders - Execution Log\n"
            output += "=" * 50 + "\n\n"
            
            for notice in self.app.conn.notices:
                output += notice.replace("NOTICE: ", "") + "\n"
            
            cursor.close()
            
            self.proc_results.delete(1.0, tk.END)
            self.proc_results.insert(1.0, output)
            
        except psycopg2.Error as e:
            self.app.conn.rollback()
            messagebox.showerror("Procedure Error", f"Failed to execute procedure:\n{str(e)}")
    
    def optimize_fleet(self):
        """Call OptimizeFleetAssignment procedure"""
        try:
            operator_id = None
            if self.operator_combo.get() != "All Operators" and "No operators" not in self.operator_combo.get():
                operator_id = int(self.operator_combo.get().split(' - ')[0])
            
            rebalance = self.rebalance_var.get()
            
            cursor = self.app.conn.cursor()
            
            # Capture notices
            self.app.conn.notices = []
            
            cursor.execute("CALL OptimizeFleetAssignment(%s, %s)", (operator_id, rebalance))
            self.app.conn.commit()
            
            # Get notices
            output = "Fleet Optimization - Execution Log\n"
            output += "=" * 50 + "\n\n"
            
            for notice in self.app.conn.notices:
                output += notice.replace("NOTICE: ", "") + "\n"
            
            cursor.close()
            
            self.proc_results.delete(1.0, tk.END)
            self.proc_results.insert(1.0, output)
            
        except psycopg2.Error as e:
            self.app.conn.rollback()
            messagebox.showerror("Procedure Error", f"Failed to execute procedure:\n{str(e)}")