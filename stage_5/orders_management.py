import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime, date, timedelta

class OrdersManagement:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        self.load_orders()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="Orders Management", 
                 style='Title.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="Back to Menu", 
                  command=self.app.show_main_menu).pack(side='right')
        
        # Toolbar
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill='x', padx=20, pady=5)
        
        ttk.Button(toolbar, text="New Order", command=self.new_order).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Edit Order", command=self.edit_order).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Delete Order", command=self.delete_order).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Mark as Arrived", command=self.mark_arrived).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Refresh", command=self.load_orders).pack(side='left', padx=5)
        
        # Filter frame
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(filter_frame, text="Filter:").pack(side='left', padx=5)
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["All", "Pending", "Arrived", "Overdue"], width=15)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filter())
        filter_combo.pack(side='left', padx=5)
        
        # Orders treeview
        tree_frame = ttk.Frame(self.parent)
        tree_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        columns = ('Order ID', 'Part', 'Supplier', 'Warehouse', 'Amount', 'Order Date', 'Arrival Date', 'Status')
        self.orders_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=20)
        
        # Configure columns
        self.orders_tree.column('#0', width=0, stretch=False)
        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.orders_tree.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
        
        # Double click to edit
        self.orders_tree.bind('<Double-Button-1>', lambda e: self.edit_order())
        
        # Status bar
        self.status_label = ttk.Label(self.parent, text="")
        self.status_label.pack(fill='x', padx=20, pady=5)
    
    def load_orders(self):
        """Load orders from database"""
        try:
            cursor = self.app.conn.cursor()
            
            cursor.execute("""
                SELECT 
                    o.order_id,
                    p.name as part_name,
                    s.name as supplier_name,
                    w.location as warehouse_location,
                    o.amount,
                    o.order_date,
                    o.arrival_date,
                    CASE 
                        WHEN o.arrival_date <= CURRENT_DATE THEN 'Arrived'
                        WHEN o.arrival_date < CURRENT_DATE + INTERVAL '3 days' THEN 'Due Soon'
                        ELSE 'Pending'
                    END as status
                FROM myorder o
                INNER JOIN part p ON o.part_id = p.part_id
                INNER JOIN suppliers s ON o.supplier_id = s.supplier_id
                INNER JOIN warehouses w ON o.warehouse_id = w.warehouse_id
                ORDER BY o.order_date DESC
            """)
            
            self.all_orders = cursor.fetchall()
            cursor.close()
            
            self.apply_filter()
            self.update_status()
            
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"Failed to load orders:\n{str(e)}")
    
    def apply_filter(self):
        """Apply filter to orders display"""
        filter_value = self.filter_var.get()
        
        if filter_value == "All":
            filtered_orders = self.all_orders
        elif filter_value == "Pending":
            filtered_orders = [o for o in self.all_orders if o[7] in ['Pending', 'Due Soon']]
        elif filter_value == "Arrived":
            filtered_orders = [o for o in self.all_orders if o[7] == 'Arrived']
        elif filter_value == "Overdue":
            today = date.today()
            filtered_orders = [o for o in self.all_orders if o[6] < today and o[7] != 'Arrived']
        else:
            filtered_orders = self.all_orders
        
        self.display_orders(filtered_orders)
    
    def display_orders(self, orders):
        """Display orders in treeview"""
        # Clear existing items
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        # Insert orders
        for order in orders:
            # Determine tag based on status
            tag = 'normal'
            if order[7] == 'Due Soon':
                tag = 'warning'
            elif order[6] < date.today() and order[7] != 'Arrived':
                tag = 'overdue'
            
            self.orders_tree.insert('', 'end', values=order, tags=(tag,))
        
        # Configure tags
        self.orders_tree.tag_configure('warning', foreground='orange')
        self.orders_tree.tag_configure('overdue', foreground='red')
    
    def update_status(self):
        """Update status bar"""
        total = len(self.all_orders)
        pending = len([o for o in self.all_orders if o[7] in ['Pending', 'Due Soon']])
        overdue = len([o for o in self.all_orders if o[6] < date.today() and o[7] != 'Arrived'])
        
        self.status_label.config(text=f"Total Orders: {total} | Pending: {pending} | Overdue: {overdue}")
    
    def new_order(self):
        """Create new order dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("New Order")
        dialog.geometry("500x400")
        
        # Form fields
        fields_frame = ttk.Frame(dialog, padding="10")
        fields_frame.pack(fill='both', expand=True)
        
        # Part selection
        ttk.Label(fields_frame, text="Part:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        part_combo = ttk.Combobox(fields_frame, width=30)
        part_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Supplier selection
        ttk.Label(fields_frame, text="Supplier:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        supplier_combo = ttk.Combobox(fields_frame, width=30, state='readonly')
        supplier_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Warehouse selection
        ttk.Label(fields_frame, text="Warehouse:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        warehouse_combo = ttk.Combobox(fields_frame, width=30)
        warehouse_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # Amount
        ttk.Label(fields_frame, text="Amount:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        amount_spinbox = ttk.Spinbox(fields_frame, from_=1, to=10000, width=10)
        amount_spinbox.set(100)
        amount_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        # Order date
        ttk.Label(fields_frame, text="Order Date:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
                order_date_entry = ttk.Entry(fields_frame, width=15)
        order_date_entry.insert(0, str(date.today()))
        order_date_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        
        # Arrival date
        ttk.Label(fields_frame, text="Expected Arrival:").grid(row=5, column=0, padx=5, pady=5, sticky='e')
        arrival_date_entry = ttk.Entry(fields_frame, width=15)
        arrival_date_entry.insert(0, str(date.today() + timedelta(days=7)))
        arrival_date_entry.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        
        # Price info label
        price_label = ttk.Label(fields_frame, text="", foreground='blue')
        price_label.grid(row=6, column=0, columnspan=2, pady=10)
        
        def load_parts():
            """Load parts for selection"""
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("SELECT part_id, name FROM part ORDER BY name")
                parts = cursor.fetchall()
                cursor.close()
                
                part_combo['values'] = [f"{p[0]} - {p[1]}" for p in parts]
                
            except psycopg2.Error as e:
                messagebox.showerror("Error", f"Failed to load parts:\n{str(e)}")
        
        def load_warehouses():
            """Load warehouses for selection"""
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("SELECT warehouse_id, location FROM warehouses ORDER BY location")
                warehouses = cursor.fetchall()
                cursor.close()
                
                warehouse_combo['values'] = [f"{w[0]} - {w[1]}" for w in warehouses]
                
            except psycopg2.Error as e:
                messagebox.showerror("Error", f"Failed to load warehouses:\n{str(e)}")
        
        def on_part_selected(event):
            """Load suppliers for selected part"""
            if not part_combo.get():
                return
            
            part_id = int(part_combo.get().split(' - ')[0])
            
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("""
                    SELECT s.supplier_id, s.name, sp.price
                    FROM suppliers s
                    INNER JOIN supplierparts sp ON s.supplier_id = sp.supplier_id
                    WHERE sp.part_id = %s
                    ORDER BY sp.price
                """, (part_id,))
                
                suppliers = cursor.fetchall()
                cursor.close()
                
                if suppliers:
                    supplier_combo['values'] = [f"{s[0]} - {s[1]} (${s[2]:.2f})" for s in suppliers]
                    supplier_combo.set(supplier_combo['values'][0])  # Select cheapest
                    update_price_info()
                else:
                    supplier_combo['values'] = []
                    supplier_combo.set('')
                    price_label.config(text="No suppliers available for this part")
                
            except psycopg2.Error as e:
                messagebox.showerror("Error", f"Failed to load suppliers:\n{str(e)}")
        
        def update_price_info():
            """Update price information display"""
            if supplier_combo.get() and amount_spinbox.get():
                try:
                    price_str = supplier_combo.get().split('($')[1].split(')')[0]
                    price = float(price_str)
                    amount = int(amount_spinbox.get())
                    total = price * amount
                    price_label.config(text=f"Unit Price: ${price:.2f} | Total Cost: ${total:.2f}")
                except:
                    price_label.config(text="")
        
        def save_order():
            """Save the new order"""
            if not all([part_combo.get(), supplier_combo.get(), warehouse_combo.get()]):
                messagebox.showwarning("Invalid Input", "Please fill all fields")
                return
            
            try:
                part_id = int(part_combo.get().split(' - ')[0])
                supplier_id = int(supplier_combo.get().split(' - ')[0])
                warehouse_id = int(warehouse_combo.get().split(' - ')[0])
                amount = int(amount_spinbox.get())
                order_date = order_date_entry.get()
                arrival_date = arrival_date_entry.get()
                
                cursor = self.app.conn.cursor()
                
                # Get next order_id
                cursor.execute("SELECT COALESCE(MAX(order_id), 0) + 1 FROM myorder")
                order_id = cursor.fetchone()[0]
                
                # Insert order
                cursor.execute("""
                    INSERT INTO myorder (order_id, part_id, supplier_id, warehouse_id, 
                                       amount, order_date, arrival_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (order_id, part_id, supplier_id, warehouse_id, amount, order_date, arrival_date))
                
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", f"Order {order_id} created successfully!")
                dialog.destroy()
                self.load_orders()
                
            except Exception as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to create order:\n{str(e)}")
        
        # Bind events
        part_combo.bind('<<ComboboxSelected>>', on_part_selected)
        amount_spinbox.config(command=update_price_info)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save Order", command=save_order).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='right', padx=5)
        
        # Load initial data
        load_parts()
        load_warehouses()
    
    def edit_order(self):
        """Edit selected order"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order to edit")
            return
        
        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]
        
        # Create edit dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Edit Order {order_id}")
        dialog.geometry("400x300")
        
        # Get current order details
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("""
                SELECT amount, order_date, arrival_date
                FROM myorder
                WHERE order_id = %s
            """, (order_id,))
            
            order_data = cursor.fetchone()
            cursor.close()
            
            if not order_data:
                messagebox.showerror("Error", "Order not found")
                dialog.destroy()
                return
            
        except psycopg2.Error as e:
            messagebox.showerror("Error", f"Failed to load order:\n{str(e)}")
            dialog.destroy()
            return
        
        # Form fields
        ttk.Label(dialog, text="Amount:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        amount_entry = ttk.Entry(dialog, width=20)
        amount_entry.insert(0, order_data[0])
        amount_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Order Date:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        order_date_entry = ttk.Entry(dialog, width=20)
        order_date_entry.insert(0, order_data[1])
        order_date_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Arrival Date:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        arrival_date_entry = ttk.Entry(dialog, width=20)
        arrival_date_entry.insert(0, order_data[2])
        arrival_date_entry.grid(row=2, column=1, padx=10, pady=5)
        
        def update_order():
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("""
                    UPDATE myorder
                    SET amount = %s, order_date = %s, arrival_date = %s
                    WHERE order_id = %s
                """, (int(amount_entry.get()), order_date_entry.get(), 
                      arrival_date_entry.get(), order_id))
                
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Order updated successfully!")
                dialog.destroy()
                self.load_orders()
                
            except Exception as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to update order:\n{str(e)}")
        
        ttk.Button(dialog, text="Update", command=update_order).grid(row=3, column=0, columnspan=2, pady=20)
    
    def delete_order(self):
        """Delete selected order"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order to delete")
            return
        
        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete order {order_id}?"):
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("DELETE FROM myorder WHERE order_id = %s", (order_id,))
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Order deleted successfully!")
                self.load_orders()
                
            except psycopg2.Error as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to delete order:\n{str(e)}")
    
    def mark_arrived(self):
        """Mark selected order as arrived"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order to mark as arrived")
            return
        
        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Mark order {order_id} as arrived today?\n\nThis will update the warehouse inventory."):
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("""
                    UPDATE myorder
                    SET arrival_date = CURRENT_DATE
                    WHERE order_id = %s
                """, (order_id,))
                
                self.app.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Order marked as arrived and inventory updated!")
                self.load_orders()
                
            except psycopg2.Error as e:
                self.app.conn.rollback()
                messagebox.showerror("Error", f"Failed to update order:\n{str(e)}")