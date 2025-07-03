-- פרוצדורה 1: עיבוד הזמנות ממתינות ועדכון מלאי
-- הפרוצדורה מעבדת הזמנות שהגיעו ומעדכנת את המלאי במחסנים

CREATE OR REPLACE PROCEDURE ProcessPendingOrders(
    p_process_date DATE DEFAULT CURRENT_DATE,
    p_max_orders INT DEFAULT 100
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- Cursor for orders to process
    CURSOR order_cursor IS
        SELECT 
            o.order_id,
            o.part_id,
            o.amount,
            o.warehouse_id,
            o.supplier_id,
            p.name as part_name,
            w.location as warehouse_location,
            w.capacity
        FROM myorder o
        INNER JOIN part p ON o.part_id = p.part_id
        INNER JOIN warehouses w ON o.warehouse_id = w.warehouse_id
        WHERE o.arrival_date = p_process_date
        ORDER BY o.order_id
        LIMIT p_max_orders;
    
    -- Variables
    v_order_rec RECORD;
    v_processed_count INT := 0;
    v_error_count INT := 0;
    v_current_stock INT;
    v_warehouse_total INT;
    v_update_success BOOLEAN;
    
BEGIN
    RAISE NOTICE 'Starting order processing for date: %', p_process_date;
    
    -- Process each order
    FOR v_order_rec IN order_cursor LOOP
        BEGIN
            v_update_success := FALSE;
            
            -- Check current warehouse capacity
            SELECT COALESCE(SUM(warehouse_quantity), 0) 
            INTO v_warehouse_total
            FROM warehouseparts
            WHERE warehouse_id = v_order_rec.warehouse_id;
            
            -- Verify capacity
            IF v_warehouse_total + v_order_rec.amount > v_order_rec.capacity THEN
                RAISE WARNING 'Order % would exceed warehouse % capacity. Skipping.', 
                    v_order_rec.order_id, v_order_rec.warehouse_id;
                v_error_count := v_error_count + 1;
                CONTINUE;
            END IF;
            
            -- Check if part exists in warehouse
            SELECT warehouse_quantity 
            INTO v_current_stock
            FROM warehouseparts
            WHERE part_id = v_order_rec.part_id 
            AND warehouse_id = v_order_rec.warehouse_id;
            
            IF v_current_stock IS NULL THEN
                -- Insert new part into warehouse
                INSERT INTO warehouseparts (
                    part_id, 
                    warehouse_id, 
                    warehouse_quantity, 
                    last_updated
                ) VALUES (
                    v_order_rec.part_id,
                    v_order_rec.warehouse_id,
                    v_order_rec.amount,
                    p_process_date
                );
                
                RAISE NOTICE 'Added new part % to warehouse % with quantity %',
                    v_order_rec.part_name, v_order_rec.warehouse_location, v_order_rec.amount;
            ELSE
                -- Update existing stock
                UPDATE warehouseparts
                SET warehouse_quantity = warehouse_quantity + v_order_rec.amount,
                    last_updated = p_process_date
                WHERE part_id = v_order_rec.part_id 
                AND warehouse_id = v_order_rec.warehouse_id;
                
                RAISE NOTICE 'Updated part % in warehouse % from % to %',
                    v_order_rec.part_name, v_order_rec.warehouse_location, 
                    v_current_stock, v_current_stock + v_order_rec.amount;
            END IF;
            
            -- Update part last_update date
            UPDATE part
            SET last_update = p_process_date
            WHERE part_id = v_order_rec.part_id;
            
            v_processed_count := v_processed_count + 1;
            v_update_success := TRUE;
            
            -- Log successful processing
            IF v_processed_count % 10 = 0 THEN
                RAISE NOTICE 'Processed % orders so far...', v_processed_count;
            END IF;
            
        EXCEPTION
            WHEN OTHERS THEN
                v_error_count := v_error_count + 1;
                RAISE WARNING 'Error processing order %: %', v_order_rec.order_id, SQLERRM;
                -- Continue with next order
        END;
    END LOOP;
    
    -- Update supplier statistics
    UPDATE suppliers s
    SET phone = s.phone -- Dummy update to trigger any supplier triggers
    WHERE supplier_id IN (
        SELECT DISTINCT supplier_id 
        FROM myorder 
        WHERE arrival_date = p_process_date
    );
    
    -- Final report
    RAISE NOTICE '======================================';
    RAISE NOTICE 'Order Processing Complete';
    RAISE NOTICE 'Date: %', p_process_date;
    RAISE NOTICE 'Orders Processed: %', v_processed_count;
    RAISE NOTICE 'Errors: %', v_error_count;
    RAISE NOTICE '======================================';
    
    -- Raise exception if too many errors
    IF v_error_count > p_max_orders * 0.1 THEN
        RAISE EXCEPTION 'Too many errors during processing (% of %)', v_error_count, p_max_orders;
    END IF;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Critical error in ProcessPendingOrders: %', SQLERRM;
        RAISE;
END;
$$;