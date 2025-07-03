-- תוכנית ראשית 1: ניתוח מקיף של מחסנים
-- התוכנית מפעילה פונקציה ופרוצדורה לניתוח ואופטימיזציה של מחסנים

DO $$
DECLARE
    -- Variables for function results
    v_warehouse_rec RECORD;
    v_total_value DECIMAL(12,2) := 0;
    v_total_employees INT := 0;
    v_low_capacity_warehouses INT := 0;
    
    -- Cursor for warehouse analysis
    warehouse_cursor CURSOR FOR
        SELECT warehouse_id, location 
        FROM warehouses 
        ORDER BY capacity DESC;
    
BEGIN
    RAISE NOTICE '======================================';
    RAISE NOTICE 'WAREHOUSE ANALYSIS PROGRAM';
    RAISE NOTICE 'Start Time: %', CURRENT_TIMESTAMP;
    RAISE NOTICE '======================================';
    
    -- Step 1: Analyze each warehouse using the function
    FOR v_warehouse_rec IN warehouse_cursor LOOP
        RAISE NOTICE '';
        RAISE NOTICE 'Analyzing warehouse: %', v_warehouse_rec.location;
        
        -- Call the analysis function
        FOR v_warehouse_rec IN 
            SELECT * FROM AnalyzeWarehouseOperations(v_warehouse_rec.warehouse_id)
        LOOP
            RAISE NOTICE '  - Total Parts Value: $%', v_warehouse_rec.total_parts_value;
            RAISE NOTICE '  - Unique Parts: %', v_warehouse_rec.unique_parts;
            RAISE NOTICE '  - Total Quantity: %', v_warehouse_rec.total_quantity;
            RAISE NOTICE '  - Employees: %', v_warehouse_rec.employee_count;
            RAISE NOTICE '  - Trains: %', v_warehouse_rec.train_count;
            RAISE NOTICE '  - Active Customers: %', v_warehouse_rec.active_customers;
            RAISE NOTICE '  - Pending Orders: %', v_warehouse_rec.pending_orders;
            RAISE NOTICE '  - Capacity Usage: %%', v_warehouse_rec.capacity_usage;
            
            -- Accumulate totals
            v_total_value := v_total_value + v_warehouse_rec.total_parts_value;
            v_total_employees := v_total_employees + v_warehouse_rec.employee_count;
            
            -- Check for low capacity
            IF v_warehouse_rec.capacity_usage > 80 THEN
                v_low_capacity_warehouses := v_low_capacity_warehouses + 1;
                RAISE WARNING '  ! High capacity usage detected!';
            END IF;
        END LOOP;
    END LOOP;
    
    -- Step 2: Summary statistics
    RAISE NOTICE '';
    RAISE NOTICE '======================================';
    RAISE NOTICE 'SUMMARY STATISTICS';
    RAISE NOTICE '======================================';
    RAISE NOTICE 'Total Inventory Value: $%', v_total_value;
    RAISE NOTICE 'Total Employees: %', v_total_employees;
    RAISE NOTICE 'Warehouses Near Capacity: %', v_low_capacity_warehouses;
    
    -- Step 3: Process pending orders
    RAISE NOTICE '';
    RAISE NOTICE '======================================';
    RAISE NOTICE 'PROCESSING PENDING ORDERS';
    RAISE NOTICE '======================================';
    
    -- Call the procedure to process orders
    BEGIN
        CALL ProcessPendingOrders(CURRENT_DATE, 50);
        RAISE NOTICE 'Order processing completed successfully';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Error during order processing: %', SQLERRM;
    END;
    
    -- Step 4: Check for critical inventory levels
    RAISE NOTICE '';
    RAISE NOTICE '======================================';
    RAISE NOTICE 'CRITICAL INVENTORY CHECK';
    RAISE NOTICE '======================================';
    
    FOR v_warehouse_rec IN 
        SELECT 
            w.location,
            p.name as part_name,
            wp.warehouse_quantity
        FROM warehouseparts wp
        INNER JOIN warehouses w ON wp.warehouse_id = w.warehouse_id
        INNER JOIN part p ON wp.part_id = p.part_id
        WHERE wp.warehouse_quantity < 20
        ORDER BY wp.warehouse_quantity ASC
        LIMIT 10
    LOOP
        RAISE WARNING 'Low stock: % has only % units of %',
            v_warehouse_rec.location,
            v_warehouse_rec.warehouse_quantity,
            v_warehouse_rec.part_name;
    END LOOP;
    
    RAISE NOTICE '';
    RAISE NOTICE '======================================';
    RAISE NOTICE 'PROGRAM COMPLETED';
    RAISE NOTICE 'End Time: %', CURRENT_TIMESTAMP;
    RAISE NOTICE '======================================';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Program error: %', SQLERRM;
        RAISE;
END;
$$;