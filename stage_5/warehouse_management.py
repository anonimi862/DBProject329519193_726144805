import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

class WarehouseManagement:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        self.load_warehouses()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="Warehouse Management", 
                 style='Title.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="Back to Menu", 
                  command=self.app.show_main_menu).pack(side='right')
        
        # Main content with notebook for tabs
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Create tabs
        self.create_warehouse_tab()
        self.create_warehouse_parts_tab()
        self.create_employees_tab()
        
    def create_warehouse_tab(self):
        # Warehouse tab
        warehouse_frame = ttk.Frame(self.notebook)
        self.notebook.add(warehouse_frame, text="Warehouses")
        
        # Toolbar
        toolbar = ttk.Frame(warehouse_frame)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(toolbar, text="Add Warehouse", 
                  command=self.add_warehouse).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Edit Warehouse", 
                  command=self.edit_warehouse).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Delete Warehouse", 
                  command=self.delete_warehouse).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Refresh", 
                  command=self.load_warehouses).pack(side='left', padx=5)
        
        # Treeview for warehouses
        columns = ('ID', 'Location', 'Capacity', 'Open Date', 'Current Load', 'Usage %')
        self.warehouse_tree = ttk.Treeview(warehouse_frame, columns=columns, 
                                         show='tree headings', height=15)
        
        # Configure columns
        self.warehouse_tree.column('#0', width=0, stretch=False)
        self.warehouse_tree.column('ID', width=50)
        self.warehouse_tree.column('Location', width=150)
        self.warehouse_tree.column('Capacity', width=100)
        self.warehouse_tree.column('Open Date', width=100)
        self.warehouse_tree.column('Current Load', width=100)
        self.warehouse_tree.column('Usage %', width=80)
        
        # Set headings
        for col in columns:
            self.warehouse_tree.heading(col, text=col)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(warehouse_frame, orient='vertical', 
                                command=self.warehouse_tree.yview)
        self.warehouse_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.warehouse_tree.pack(side='left', expand=True, fill='both', padx=(10,0))
        scrollbar.pack(side='right', fill='y')
        
    def create_warehouse_parts_tab(self):
        # Warehouse Parts tab
        parts_frame = ttk.Frame(self.notebook)
        self.notebook.add(parts_frame, text="Warehouse Inventory")
        
        # Filter frame
        filter_frame = ttk.Frame(parts_frame)
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Select Warehouse:").pack(side='left', padx=5)
        self.warehouse_combo = ttk.Combobox(filter_frame, width=30)
        self.warehouse_combo.pack(side='left', padx=5)
        self.warehouse_combo.bind('<<ComboboxSelected>>', self.load_warehouse_parts)
        
        ttk.Button(filter_frame, text="Update Quantity", 
                  command=self.update_part_quantity).pack(side='left', padx=5)
        ttk.Button(filter_frame, text="Add Part", 
                  command=self.add_part_to_warehouse).pack(side='left', padx=5)
        ttk.Button(filter_frame, text="Remove Part", 
                  command=self.remove_part_from_warehouse).pack(side='left', padx=5)
        
        # Parts treeview
        columns = ('Part ID', 'Part Name', 'Quantity', 'Last Updated', 'Value')
        self.parts_tree = ttk.Treeview(parts_frame, columns=columns, 
                                     show='tree headings', height=15)
        
        # Configure columns
        self.parts_tree.column('#0', width=0, stretch=False)
        for col in columns:
            self.parts_tree.heading(col, text=col)
            self.parts_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parts_frame, orient='vertical', 
                                command=self.parts_tree.yview)
        self.parts_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.parts_tree.pack(side='left', expand=True, fill='both', padx=(10,0))
        scrollbar.pack(side='right', fill='y')
        
    def create_employees_tab(self):
        # Employees tab
        emp_frame = ttk.Frame(self.notebook)
        self.notebook.add(emp_frame, text="Warehouse Employees")
        
        # Filter frame
        filter_frame = ttk.Frame(emp_frame)
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Select Warehouse:").pack(side='left', padx=5)
        self.emp_warehouse_combo = ttk.Combobox(filter_frame, width=30)
        self.emp_warehouse_combo.pack(side='left', padx=5)
        self.emp_warehouse_combo.bind('<<ComboboxSelected>>', self.load_warehouse_employees)
        
        ttk.Button(filter_frame, text="Assign Employee", 
                  command=self.assign_employee).pack(side='left', padx=5)
        ttk.Button(filter_frame, text="Remove Assignment", 
                  command=self.remove_employee).pack(side='left', padx=5)
        
        # Employees treeview
        columns = ('Employee ID', 'Name', 'Role', 'Start Date', 'Last Training')
        self.emp_tree = ttk.Treeview(emp_frame, columns=columns, 
                                   show='tree headings', height=15)
        
        # Configure columns
        self.emp_tree.column('#0', width=0, stretch=False)
        for col in columns:
            self.emp_tree.heading(col, text=col)
            self.emp_tree.column(col, width=120)
        
                # Scrollbar
        scrollbar = ttk.Scrollbar(emp_frame, orient='vertical', 
                                command=self.emp_tree.yview)
        self.emp_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.emp_tree.pack(side='left', expand=True, fill='both', padx=(10,0))
        scrollbar.pack(side='right', fill='y')
    
    def load_warehouses(self):
        """Load warehouses from database"""
        try:
            cursor = self.app.conn.cursor()
            
            # Clear existing items
            for item in self.warehouse_tree.get_children():
                self.warehouse_tree.delete(item)
            
            # Query warehouses with current load
            query = """
                SELECT 
                    w.warehouse_id,
                    w.location,
                    w.capacity,
                    w.open_date,
                    COALESCE(SUM(wp.warehouse_quantity), 0) as current_load,
                    ROUND(COALESCE(SUM(wp.warehouse_quantity), 0)::DECIMAL / w.capacity * 100, 2) as usage_percent
                FROM warehouses w
                LEFT JOIN warehouseparts wp ON w.warehouse_id = wp.warehouse_id
                GROUP BY w.warehouse_id, w.location, w.capacity, w.open_date
                ORDER BY w.warehouse_id
            """
            
            cursor.execute(query)
            warehouses = cursor.fetchall()
            
            # Insert into treeview
            for warehouse in warehouses:
                # Format usage percentage with color
                usage = warehouse[5]
                tag = 'normal'
                if usage > 80:
                    tag = 'high'
                elif usage > 60:
                    tag = 'medium'
                
                self.warehouse_tree.insert('', 'end', values=warehouse, tags=(tag,))
            
            # Configure tags for colors
            self.warehouse_tree.tag_configure('high', foreground='red')
            self.warehouse_tree.tag_configure('medium', foreground='orange')
            
            # Update comboboxes
            self.update_warehouse_combos(warehouses)
            
            cursor.close()
            
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"Failed to load warehouses:\n{str(e)}")
    
    def update_warehouse_combos(self, warehouses):
        """Update warehouse comboboxes"""
        warehouse_list = [f"{w[0]} - {w[1]}" for w in warehouses]
        self.warehouse_combo['values'] = warehouse_list
        self.emp_warehouse_combo['values'] = warehouse_list
        
        if warehouse_list:
            self.warehouse_combo.set(warehouse_list[0])
            self.emp_warehouse_combo.set(warehouse_list[0])
    
    def add_warehouse(self):
        """Add new warehouse dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Warehouse")
        dialog.geometry("400x300")
        
        # Form fields
        fields = [
            ("Location:", "location"),
            ("Capacity:", "capacity"),
            ("Open Date (YYYY-MM-DD):", "open_date")
        ]
        
        entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry
        
        def save_warehouse():
            try:
                cursor = self.app.conn.cursor()
                
                # Get next warehouse_id
                cursor.execute("SELECT COALESCE(MAX(warehouse_id), 0) + 1 FROM warehouses")
                warehouse_id = cursor.fetchone()[0]
                
                # Insert warehouse
                cursor.execute("""
                    INSERT INTO warehouses (warehouse_id, location, capacity, open_date)
                    VALUES (%s, %s, %s, %s)
                """, (warehouse_id, entries['location'].get(), 
                      int(entries['capacity'].get()), entries['open_date'].get()))
                
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Warehouse added successfully!")
                dialog.destroy()
                self.load_warehouses()
                
            except Exception as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to add warehouse:\n{str(e)}")
        
        ttk.Button(dialog, text="Save", command=save_warehouse).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def edit_warehouse(self):
        """Edit selected warehouse"""
        selection = self.warehouse_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a warehouse to edit")
            return
        
        item = self.warehouse_tree.item(selection[0])
        values = item['values']
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Warehouse")
        dialog.geometry("400x300")
        
        # Form fields
        fields = [
            ("Location:", "location", values[1]),
            ("Capacity:", "capacity", values[2])
        ]
        
        entries = {}
        for i, (label, field, value) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            entry = ttk.Entry(dialog, width=30)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry
        
        def update_warehouse():
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("""
                    UPDATE warehouses 
                    SET location = %s, capacity = %s
                    WHERE warehouse_id = %s
                """, (entries['location'].get(), int(entries['capacity'].get()), values[0]))
                
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Warehouse updated successfully!")
                dialog.destroy()
                self.load_warehouses()
                
            except Exception as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to update warehouse:\n{str(e)}")
        
        ttk.Button(dialog, text="Update", command=update_warehouse).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def delete_warehouse(self):
        """Delete selected warehouse"""
        selection = self.warehouse_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a warehouse to delete")
            return
        
        item = self.warehouse_tree.item(selection[0])
        warehouse_id = item['values'][0]
        location = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete warehouse '{location}'?"):
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("DELETE FROM warehouses WHERE warehouse_id = %s", (warehouse_id,))
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Warehouse deleted successfully!")
                self.load_warehouses()
                
            except psycopg2.Error as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to delete warehouse:\n{str(e)}")
    
    def load_warehouse_parts(self, event=None):
        """Load parts for selected warehouse"""
        if not self.warehouse_combo.get():
            return
        
        warehouse_id = int(self.warehouse_combo.get().split(' - ')[0])
        
        try:
            cursor = self.app.conn.cursor()
            
            # Clear existing items
            for item in self.parts_tree.get_children():
                self.parts_tree.delete(item)
            
            # Query parts in warehouse
            cursor.execute("""
                SELECT 
                    wp.part_id,
                    p.name,
                    wp.warehouse_quantity,
                    wp.last_updated,
                    ROUND(wp.warehouse_quantity * COALESCE(AVG(sp.price), 0), 2) as value
                FROM warehouseparts wp
                INNER JOIN part p ON wp.part_id = p.part_id
                LEFT JOIN supplierparts sp ON p.part_id = sp.part_id
                WHERE wp.warehouse_id = %s
                GROUP BY wp.part_id, p.name, wp.warehouse_quantity, wp.last_updated
                ORDER BY p.name
            """, (warehouse_id,))
            
            parts = cursor.fetchall()
            
            # Insert into treeview
            for part in parts:
                self.parts_tree.insert('', 'end', values=part)
            
            cursor.close()
            
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"Failed to load parts:\n{str(e)}")
    
    def load_warehouse_employees(self, event=None):
        """Load employees for selected warehouse"""
        if not self.emp_warehouse_combo.get():
            return
        
        warehouse_id = int(self.emp_warehouse_combo.get().split(' - ')[0])
        
        try:
            cursor = self.app.conn.cursor()
            
            # Clear existing items
            for item in self.emp_tree.get_children():
                self.emp_tree.delete(item)
            
            # Query employees in warehouse
            cursor.execute("""
                SELECT 
                    e.employee_id,
                    e.name,
                    e.role,
                    e.start_date,
                    e.last_training
                FROM employees e
                INNER JOIN worksat wa ON e.employee_id = wa.employee_id
                WHERE wa.warehouse_id = %s
                ORDER BY e.name
            """, (warehouse_id,))
            
            employees = cursor.fetchall()
            
            # Insert into treeview
            for emp in employees:
                self.emp_tree.insert('', 'end', values=emp)
            
            cursor.close()
            
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"Failed to load employees:\n{str(e)}")
    
    def update_part_quantity(self):
        """Update quantity of selected part"""
        selection = self.parts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a part to update")
            return
        
        item = self.parts_tree.item(selection[0])
        part_id = item['values'][0]
        part_name = item['values'][1]
        current_qty = item['values'][2]
        
        # Create dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Update Part Quantity")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text=f"Part: {part_name}").pack(pady=10)
        ttk.Label(dialog, text=f"Current Quantity: {current_qty}").pack()
        
        ttk.Label(dialog, text="New Quantity:").pack(pady=5)
        qty_entry = ttk.Entry(dialog, width=20)
        qty_entry.pack()
        qty_entry.insert(0, current_qty)
        
        def update():
            try:
                warehouse_id = int(self.warehouse_combo.get().split(' - ')[0])
                new_qty = int(qty_entry.get())
                
                cursor = self.app.conn.cursor()
                cursor.execute("""
                    UPDATE warehouseparts
                    SET warehouse_quantity = %s, last_updated = CURRENT_DATE
                    WHERE warehouse_id = %s AND part_id = %s
                """, (new_qty, warehouse_id, part_id))
                
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Quantity updated successfully!")
                dialog.destroy()
                self.load_warehouse_parts()
                self.load_warehouses()  # Refresh warehouse capacity
                
            except Exception as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to update quantity:\n{str(e)}")
        
        ttk.Button(dialog, text="Update", command=update).pack(pady=10)