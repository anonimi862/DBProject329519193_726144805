import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

class PartsManagement:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        self.load_parts()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="Parts Management", 
                 style='Title.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="Back to Menu", 
                  command=self.app.show_main_menu).pack(side='right')
        
        # Toolbar
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill='x', padx=20, pady=5)
        
        ttk.Button(toolbar, text="Add Part", command=self.add_part).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Edit Part", command=self.edit_part).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Delete Part", command=self.delete_part).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Manage Suppliers", command=self.manage_suppliers).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Refresh", command=self.load_parts).pack(side='left', padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_parts())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)
        
        # Parts treeview
        tree_frame = ttk.Frame(self.parent)
        tree_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        columns = ('ID', 'Name', 'Last Update', 'Suppliers', 'Min Price', 'Max Price', 'Total Stock')
        self.parts_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=20)
        
        # Configure columns
        self.parts_tree.column('#0', width=0, stretch=False)
        self.parts_tree.column('ID', width=60)
        self.parts_tree.column('Name', width=200)
        self.parts_tree.column('Last Update', width=100)
        self.parts_tree.column('Suppliers', width=80)
        self.parts_tree.column('Min Price', width=80)
        self.parts_tree.column('Max Price', width=80)
        self.parts_tree.column('Total Stock', width=100)
        
        # Set headings
        for col in columns:
            self.parts_tree.heading(col, text=col)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.parts_tree.yview)
        self.parts_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.parts_tree.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
        
        # Double click to edit
        self.parts_tree.bind('<Double-Button-1>', lambda e: self.edit_part())
    
    def load_parts(self):
        """Load parts from database"""
        try:
            cursor = self.app.conn.cursor()
            
                       cursor.execute("""
                SELECT 
                    p.part_id,
                    p.name,
                    p.last_update,
                    COUNT(DISTINCT sp.supplier_id) as supplier_count,
                    MIN(sp.price) as min_price,
                    MAX(sp.price) as max_price,
                    COALESCE(SUM(wp.warehouse_quantity), 0) as total_stock
                FROM part p
                LEFT JOIN supplierparts sp ON p.part_id = sp.part_id
                LEFT JOIN warehouseparts wp ON p.part_id = wp.part_id
                GROUP BY p.part_id, p.name, p.last_update
                ORDER BY p.name
            """)
            
            self.all_parts = cursor.fetchall()
            cursor.close()
            
            self.display_parts(self.all_parts)
            
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"Failed to load parts:\n{str(e)}")
    
    def display_parts(self, parts):
        """Display parts in treeview"""
        # Clear existing items
        for item in self.parts_tree.get_children():
            self.parts_tree.delete(item)
        
        # Insert parts
        for part in parts:
            formatted_part = list(part)
            # Format prices
            if formatted_part[4] is not None:
                formatted_part[4] = f"${formatted_part[4]:.2f}"
            else:
                formatted_part[4] = "N/A"
                
            if formatted_part[5] is not None:
                formatted_part[5] = f"${formatted_part[5]:.2f}"
            else:
                formatted_part[5] = "N/A"
            
            self.parts_tree.insert('', 'end', values=formatted_part)
    
    def filter_parts(self):
        """Filter parts based on search"""
        search_term = self.search_var.get().lower()
        if not search_term:
            self.display_parts(self.all_parts)
        else:
            filtered_parts = [p for p in self.all_parts if search_term in str(p[1]).lower()]
            self.display_parts(filtered_parts)
    
    def add_part(self):
        """Add new part dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Part")
        dialog.geometry("400x200")
        
        # Form fields
        ttk.Label(dialog, text="Part Name:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        def save_part():
            name = name_entry.get()
            if not name:
                messagebox.showwarning("Invalid Input", "Please enter a part name")
                return
            
            try:
                cursor = self.app.conn.cursor()
                
                # Get next part_id
                cursor.execute("SELECT COALESCE(MAX(part_id), 0) + 1 FROM part")
                part_id = cursor.fetchone()[0]
                
                # Insert part
                cursor.execute("""
                    INSERT INTO part (part_id, name, last_update)
                    VALUES (%s, %s, CURRENT_DATE)
                """, (part_id, name))
                
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Part added successfully!")
                dialog.destroy()
                self.load_parts()
                
            except Exception as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to add part:\n{str(e)}")
        
        ttk.Button(dialog, text="Save", command=save_part).grid(row=1, column=0, columnspan=2, pady=20)
    
    def edit_part(self):
        """Edit selected part"""
        selection = self.parts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a part to edit")
            return
        
        item = self.parts_tree.item(selection[0])
        part_id = item['values'][0]
        current_name = item['values'][1]
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Part")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Part Name:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.insert(0, current_name)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        def update_part():
            new_name = name_entry.get()
            if not new_name:
                messagebox.showwarning("Invalid Input", "Please enter a part name")
                return
            
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("""
                    UPDATE part 
                    SET name = %s, last_update = CURRENT_DATE
                    WHERE part_id = %s
                """, (new_name, part_id))
                
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Part updated successfully!")
                dialog.destroy()
                self.load_parts()
                
            except Exception as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to update part:\n{str(e)}")
        
        ttk.Button(dialog, text="Update", command=update_part).grid(row=1, column=0, columnspan=2, pady=20)
    
    def delete_part(self):
        """Delete selected part"""
        selection = self.parts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a part to delete")
            return
        
        item = self.parts_tree.item(selection[0])
        part_id = item['values'][0]
        part_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete part '{part_name}'?\n\nThis will also remove all related supplier and warehouse records."):
            try:
                cursor = self.app.conn.cursor()
                
                # Delete related records first
                cursor.execute("DELETE FROM warehouseparts WHERE part_id = %s", (part_id,))
                cursor.execute("DELETE FROM supplierparts WHERE part_id = %s", (part_id,))
                cursor.execute("DELETE FROM myorder WHERE part_id = %s", (part_id,))
                cursor.execute("DELETE FROM part WHERE part_id = %s", (part_id,))
                
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Part deleted successfully!")
                self.load_parts()
                
            except psycopg2.Error as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to delete part:\n{str(e)}")
    
    def manage_suppliers(self):
        """Manage suppliers for selected part"""
        selection = self.parts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a part to manage suppliers")
            return
        
        item = self.parts_tree.item(selection[0])
        part_id = item['values'][0]
        part_name = item['values'][1]
        
        # Create supplier management dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Manage Suppliers for {part_name}")
        dialog.geometry("600x400")
        
        # Current suppliers frame
        current_frame = ttk.LabelFrame(dialog, text="Current Suppliers", padding="10")
        current_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Suppliers listbox
        columns = ('Supplier ID', 'Name', 'Price', 'Quantity')
        suppliers_tree = ttk.Treeview(current_frame, columns=columns, show='tree headings', height=8)
        
        for col in columns:
            suppliers_tree.heading(col, text=col)
            suppliers_tree.column(col, width=120)
        suppliers_tree.column('#0', width=0, stretch=False)
        
        suppliers_tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(current_frame, orient='vertical', command=suppliers_tree.yview)
        suppliers_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        def load_suppliers():
            """Load suppliers for this part"""
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("""
                    SELECT 
                        s.supplier_id,
                        s.name,
                        sp.price,
                        sp.supplier_uantity
                    FROM suppliers s
                    INNER JOIN supplierparts sp ON s.supplier_id = sp.supplier_id
                    WHERE sp.part_id = %s
                    ORDER BY s.name
                """, (part_id,))
                
                suppliers = cursor.fetchall()
                cursor.close()
                
                # Clear and populate tree
                for item in suppliers_tree.get_children():
                    suppliers_tree.delete(item)
                
                for supplier in suppliers:
                    formatted = list(supplier)
                    formatted[2] = f"${formatted[2]:.2f}"
                    suppliers_tree.insert('', 'end', values=formatted)
                
            except psycopg2.Error as e:
                messagebox.showerror("Error", f"Failed to load suppliers:\n{str(e)}")
        
        # Add supplier frame
        add_frame = ttk.LabelFrame(dialog, text="Add/Update Supplier", padding="10")
        add_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(add_frame, text="Supplier:").grid(row=0, column=0, padx=5, pady=5)
        supplier_combo = ttk.Combobox(add_frame, width=25)
        supplier_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Price:").grid(row=0, column=2, padx=5, pady=5)
        price_entry = ttk.Entry(add_frame, width=10)
        price_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Quantity:").grid(row=0, column=4, padx=5, pady=5)
        qty_entry = ttk.Entry(add_frame, width=10)
        qty_entry.grid(row=0, column=5, padx=5, pady=5)
        
        def load_all_suppliers():
            """Load all suppliers for combobox"""
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("SELECT supplier_id, name FROM suppliers ORDER BY name")
                all_suppliers = cursor.fetchall()
                cursor.close()
                
                supplier_combo['values'] = [f"{s[0]} - {s[1]}" for s in all_suppliers]
                
            except psycopg2.Error as e:
                messagebox.showerror("Error", f"Failed to load suppliers:\n{str(e)}")
        
        def add_supplier():
            """Add or update supplier for part"""
            if not supplier_combo.get() or not price_entry.get() or not qty_entry.get():
                messagebox.showwarning("Invalid Input", "Please fill all fields")
                return
                        try:
                supplier_id = int(supplier_combo.get().split(' - ')[0])
                price = float(price_entry.get())
                quantity = int(qty_entry.get())
                
                cursor = self.app.conn.cursor()
                
                # Insert or update
                cursor.execute("""
                    INSERT INTO supplierparts (supplier_id, part_id, price, supplier_uantity)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (supplier_id, part_id) 
                    DO UPDATE SET price = %s, supplier_uantity = %s
                """, (supplier_id, part_id, price, quantity, price, quantity))
                
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Supplier updated successfully!")
                load_suppliers()
                self.load_parts()  # Refresh main view
                
            except Exception as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to update supplier:\n{str(e)}")
        
        def remove_supplier():
            """Remove selected supplier"""
            selection = suppliers_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a supplier to remove")
                return
            
            item = suppliers_tree.item(selection[0])
            supplier_id = item['values'][0]
            
            if messagebox.askyesno("Confirm", "Remove this supplier from the part?"):
                try:
                    cursor = self.app.conn.cursor()
                    cursor.execute("""
                        DELETE FROM supplierparts 
                        WHERE supplier_id = %s AND part_id = %s
                    """, (supplier_id, part_id))
                    
                    self.app.conn.commit()
                    cursor.close()
                    
                    messagebox.showinfo("Success", "Supplier removed successfully!")
                    load_suppliers()
                    self.load_parts()
                    
                except psycopg2.Error as e:
                    self.app.conn.rollback()
                    messagebox.showerror("Error", f"Failed to remove supplier:\n{str(e)}")
        
        ttk.Button(add_frame, text="Add/Update", command=add_supplier).grid(row=1, column=0, columnspan=3, pady=5)
        ttk.Button(add_frame, text="Remove Selected", command=remove_supplier).grid(row=1, column=3, columnspan=3, pady=5)
        
        # Load data
        load_all_suppliers()
        load_suppliers()