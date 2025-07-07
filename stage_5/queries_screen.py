import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

class QueriesScreen:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="Run Queries", style='Title.TLabel').pack(side='left')
        ttk.Button(header_frame, text="Back to Menu", 
                  command=self.app.show_main_menu).pack(side='right')
        
        # Main content
        content_frame = ttk.Frame(self.parent, padding="20")
        content_frame.pack(expand=True, fill='both')
        
        # Query selection
        query_frame = ttk.LabelFrame(content_frame, text="Select Query", padding="10")
        query_frame.pack(fill='x', pady=(0, 20))
        
        self.queries = {
            "Warehouses with Most Parts": """
                SELECT 
                    w.warehouse_id,
                    w.location,
                    COUNT(DISTINCT wp.part_id) as different_parts_count,
                    SUM(wp.warehouse_quantity) as total_parts_quantity,
                    COUNT(DISTINCT wa.employee_id) as employee_count
                FROM warehouses w
                LEFT JOIN warehouseparts wp ON w.warehouse_id = wp.warehouse_id
                LEFT JOIN worksat wa ON w.warehouse_id = wa.warehouse_id
                GROUP BY w.warehouse_id, w.location
                HAVING COUNT(DISTINCT wp.part_id) > 0
                ORDER BY different_parts_count DESC, total_parts_quantity DESC
            """,
            "Employees Needing Training": """
                SELECT 
                    e.employee_id,
                    e.name as employee_name,
                    e.role,
                    e.last_training,
                    DATE_PART('day', CURRENT_DATE - e.last_training) as days_since_training,
                    w.location as warehouse_location,
                    w.warehouse_id
                FROM employees e
                INNER JOIN worksat wa ON e.employee_id = wa.employee_id
                INNER JOIN warehouses w ON wa.warehouse_id = w.warehouse_id
                WHERE e.last_training < CURRENT_DATE - INTERVAL '1 year'
                ORDER BY days_since_training DESC
            """,
            "Order Analysis by Month": """
                SELECT 
                    EXTRACT(YEAR FROM o.order_date) as order_year,
                    EXTRACT(MONTH FROM o.order_date) as order_month,
                    COUNT(o.order_id) as total_orders,
                    SUM(o.amount) as total_units_ordered,
                    SUM(o.amount * sp.price) as total_cost
                FROM myorder o
                INNER JOIN supplierparts sp ON o.supplier_id = sp.supplier_id AND o.part_id = sp.part_id
                WHERE o.order_date >= CURRENT_DATE - INTERVAL '2 years'
                GROUP BY EXTRACT(YEAR FROM o.order_date), EXTRACT(MONTH FROM o.order_date)
                ORDER BY order_year DESC, order_month DESC
            """,
            "Low Stock Alert": """
                SELECT 
                    w.location,
                    p.name as part_name,
                    wp.warehouse_quantity,
                    p.part_id,
                    p.last_update
                FROM warehouseparts wp
                INNER JOIN warehouses w ON wp.warehouse_id = w.warehouse_id
                INNER JOIN part p ON wp.part_id = p.part_id
                WHERE wp.warehouse_quantity < 50
                ORDER BY wp.warehouse_quantity ASC
            """,
            "Popular Parts Analysis": """
                SELECT 
                    p.part_id,
                    p.name as part_name,
                    p.last_update,
                    SUM(o.amount) as total_ordered,
                    COUNT(DISTINCT sp.supplier_id) as supplier_count,
                    MIN(sp.price) as min_price,
                    MAX(sp.price) as max_price,
                    AVG(sp.price) as avg_price
                FROM part p
                INNER JOIN myorder o ON p.part_id = o.part_id
                LEFT JOIN supplierparts sp ON p.part_id = sp.part_id
                WHERE o.order_date >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY p.part_id, p.name, p.last_update
                HAVING SUM(o.amount) > 50
                ORDER BY total_ordered DESC
            """
        }
        
        
        # Query dropdown
        ttk.Label(query_frame, text="Choose a query:").grid(row=0, column=0, padx=5, pady=5)
        self.query_combo = ttk.Combobox(query_frame, values=list(self.queries.keys()), width=50)
        self.query_combo.grid(row=0, column=1, padx=5, pady=5)
        self.query_combo.set(list(self.queries.keys())[0])
        
        ttk.Button(query_frame, text="Execute Query", command=self.execute_query,
                  style='Action.TButton').grid(row=0, column=2, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(content_frame, text="Query Results", padding="10")
        results_frame.pack(expand=True, fill='both')
        
        # Results treeview
        self.results_tree = ttk.Treeview(results_frame, show='tree headings', height=20)
        
        # Scrollbars
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Status bar
        self.status_label = ttk.Label(content_frame, text="Ready to execute queries")
        self.status_label.pack(fill='x', pady=(10, 0))
        
    def execute_query(self):
        """Execute selected query and display results"""
        query_name = self.query_combo.get()
        if not query_name or query_name not in self.queries:
            messagebox.showwarning("No Query", "Please select a query to execute")
            return
        
        try:
            self.status_label.config(text="Executing query...")
            self.parent.update()
            
            cursor = self.app.conn.cursor()
            query = self.queries[query_name]
            cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Clear previous results
            self.results_tree.delete(*self.results_tree.get_children())
            
            # Configure columns
            self.results_tree['columns'] = columns
            self.results_tree.column('#0', width=0, stretch=False)
            
            for col in columns:
                self.results_tree.heading(col, text=col)
                self.results_tree.column(col, width=120)
            
            # Insert results
            rows = cursor.fetchall()
            for row in rows:
                # Format values for display
                formatted_row = []
                for val in row:
                    if isinstance(val, float):
                        formatted_row.append(f"{val:.2f}")
                    else:
                        formatted_row.append(str(val))
                self.results_tree.insert('', 'end', values=formatted_row)
            
            cursor.close()
            
            self.status_label.config(text=f"Query executed successfully. {len(rows)} rows returned.")
            
        except psycopg2.Error as e:
            messagebox.showerror("Query Error", f"Failed to execute query:\n{str(e)}")
            self.status_label.config(text="Query execution failed")
            