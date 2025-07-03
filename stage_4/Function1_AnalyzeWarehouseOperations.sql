-- פונקציה 1: ניתוח מקיף של פעילות מחסן
-- הפונקציה מנתחת את פעילות המחסן כולל מלאי, עובדים, רכבות ולקוחות

CREATE OR REPLACE FUNCTION AnalyzeWarehouseOperations(
    p_warehouse_id INT,
    p_start_date DATE DEFAULT NULL
)
RETURNS TABLE(
    warehouse_id INT,
    location VARCHAR(100),
    total_parts_value DECIMAL(12,2),
    unique_parts INT,
    total_quantity INT,
    employee_count INT,
    train_count INT,
    active_customers INT,
    pending_orders INT,
    capacity_usage DECIMAL(5,2)
) 
LANGUAGE plpgsql
AS $$
DECLARE
    -- Explicit cursor for parts analysis
    CURSOR parts_cursor IS
        SELECT 
            p.part_id,
            p.name,
            wp.warehouse_quantity,
            COALESCE(AVG(sp.price), 0) as avg_price
        FROM warehouseparts wp
        INNER JOIN part p ON wp.part_id = p.part_id
        LEFT JOIN SupplierParts sp ON p.part_id = sp.part_id
        WHERE wp.warehouse_id = p_warehouse_id
        GROUP BY p.part_id, p.name, wp.warehouse_quantity;
    
    -- Variables
    v_part_record RECORD;
    v_total_value DECIMAL(12,2) := 0;
    v_unique_parts INT := 0;
    v_total_quantity INT := 0;
    v_warehouse_capacity INT;
    v_location VARCHAR(100);
    v_employee_count INT;
    v_train_count INT;
    v_customer_count INT;
    v_pending_orders INT;
    v_capacity_usage DECIMAL(5,2);
    
BEGIN
    -- Validate warehouse exists
    SELECT w.location, w.capacity 
    INTO v_location, v_warehouse_capacity
    FROM warehouses w
    WHERE w.warehouse_id = p_warehouse_id;
    
    IF v_location IS NULL THEN
        RAISE EXCEPTION 'Warehouse % not found', p_warehouse_id;
    END IF;
    
    -- Set default start date if not provided
    IF p_start_date IS NULL THEN
        p_start_date := CURRENT_DATE - INTERVAL '6 months';
    END IF;
    
    -- Process parts using explicit cursor
    OPEN parts_cursor;
    LOOP
        FETCH parts_cursor INTO v_part_record;
        EXIT WHEN NOT FOUND;
        
        v_total_value := v_total_value + (v_part_record.warehouse_quantity * v_part_record.avg_price);
        v_unique_parts := v_unique_parts + 1;
        v_total_quantity := v_total_quantity + v_part_record.warehouse_quantity;
    END LOOP;
    CLOSE parts_cursor;
    
    -- Count employees using implicit cursor
    v_employee_count := 0;
    FOR emp IN 
        SELECT e.employee_id 
        FROM employees e
        INNER JOIN WorksAt wa ON e.employee_id = wa.employee_id
        WHERE wa.warehouse_id = p_warehouse_id
    LOOP
        v_employee_count := v_employee_count + 1;
    END LOOP;
    
    -- Count trains
    SELECT COUNT(*) INTO v_train_count
    FROM trains t
    WHERE t.warehouse_id = p_warehouse_id;
    
    -- Count active customers
    SELECT COUNT(DISTINCT c.costumer_id) INTO v_customer_count
    FROM costumers c
    INNER JOIN costumer_warehous_storage cws ON c.costumer_id = cws.costumer_id
    WHERE cws.warehouse_id = p_warehouse_id
    AND (cws.end_date IS NULL OR cws.end_date >= CURRENT_DATE);
    
    -- Count pending orders
    SELECT COUNT(*) INTO v_pending_orders
    FROM myorder o
    WHERE o.warehouse_id = p_warehouse_id
    AND o.arrival_date > CURRENT_DATE;
    
    -- Calculate capacity usage
    IF v_warehouse_capacity > 0 THEN
        v_capacity_usage := ROUND((v_total_quantity::DECIMAL / v_warehouse_capacity) * 100, 2);
    ELSE
        v_capacity_usage := 0;
    END IF;
    
    -- Return results
    RETURN QUERY 
    SELECT 
        p_warehouse_id,
        v_location,
        v_total_value,
        v_unique_parts,
        v_total_quantity,
        v_employee_count,
        v_train_count,
        v_customer_count,
        v_pending_orders,
        v_capacity_usage;
        
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in AnalyzeWarehouseOperations: %', SQLERRM;
        RAISE;
END;
$$;