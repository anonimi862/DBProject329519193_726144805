        -- תוכנית ראשית 2: ניהול תחזוקת צי כלי רכב
-- התוכנית מפעילה פונקציה ופרוצדורה לניהול תחזוקה ואופטימיזציה

DO $$
DECLARE
    -- Variables
    v_maintenance_cursor refcursor;
    v_maintenance_rec RECORD;
    v_urgent_count INT := 0;
    v_overdue_count INT := 0;
    v_total_vehicles INT := 0;
    
    -- Variables for operator optimization
    v_operator_rec RECORD;
    
BEGIN
    RAISE NOTICE '======================================';
    RAISE NOTICE 'FLEET MAINTENANCE MANAGEMENT PROGRAM';
    RAISE NOTICE 'Start Time: %', CURRENT_TIMESTAMP;
    RAISE NOTICE '======================================';
    
    -- Step 1: Get maintenance schedule using function
    RAISE NOTICE '';
    RAISE NOTICE 'RETRIEVING MAINTENANCE SCHEDULE...';
    RAISE NOTICE '';
    
    -- Call function to get maintenance schedule
    v_maintenance_cursor := GetMaintenanceSchedule(60, NULL);
    
    -- Process maintenance records
    LOOP
        FETCH v_maintenance_cursor INTO v_maintenance_rec;
        EXIT WHEN NOT FOUND;
        
        v_total_vehicles := v_total_vehicles + 1;
        
        
        -- Count urgent and overdue vehicles
        IF v_maintenance_rec.priority = 'OVERDUE' THEN
            v_overdue_count := v_overdue_count + 1;
            RAISE WARNING '!!! % % (ID: %) is OVERDUE by % days!',
                v_maintenance_rec.vehicle_type,
                v_maintenance_rec.model,
                v_maintenance_rec.vehicle_id,
                ABS(v_maintenance_rec.days_until_maintenance);
        ELSIF v_maintenance_rec.priority = 'URGENT' THEN
            v_urgent_count := v_urgent_count + 1;
            RAISE NOTICE '! % % (ID: %) needs maintenance in % days',
                v_maintenance_rec.vehicle_type,
                v_maintenance_rec.model,
                v_maintenance_rec.vehicle_id,
                v_maintenance_rec.days_until_maintenance;
        ELSE
            RAISE NOTICE '  % % (ID: %) - maintenance in % days',
                v_maintenance_rec.vehicle_type,
                v_maintenance_rec.model,
                v_maintenance_rec.vehicle_id,
                v_maintenance_rec.days_until_maintenance;
        END IF;
        
        -- Check staff availability
        IF v_maintenance_rec.available_staff < 2 THEN
            RAISE WARNING '  -> Insufficient staff at %!', v_maintenance_rec.location;
        END IF;
    END LOOP;
    
    CLOSE v_maintenance_cursor;
    
    -- Step 2: Summary of maintenance needs
    RAISE NOTICE '';
    RAISE NOTICE '======================================';
    RAISE NOTICE 'MAINTENANCE SUMMARY';
    RAISE NOTICE '======================================';
    RAISE NOTICE 'Total vehicles needing maintenance: %', v_total_vehicles;
    RAISE NOTICE 'Overdue: %', v_overdue_count;
    RAISE NOTICE 'Urgent (within 7 days): %', v_urgent_count;
    RAISE NOTICE 'Scheduled: %', v_total_vehicles - v_overdue_count - v_urgent_count;
    
    -- Step 3: Optimize fleet assignments for each operator
    RAISE NOTICE '';
    RAISE NOTICE '======================================';
    RAISE NOTICE 'OPTIMIZING FLEET ASSIGNMENTS';
    RAISE NOTICE '======================================';
    
    FOR v_operator_rec IN 
        SELECT Operator_id, Name, Type, Fleet_Size
        FROM Operator
        ORDER BY Fleet_Size DESC
    LOOP
        RAISE NOTICE '';
        RAISE NOTICE 'Processing operator: % (Type: %, Fleet: %)',
            v_operator_rec.Name,
            v_operator_rec.Type,
            v_operator_rec.Fleet_Size;
        
        -- Call optimization procedure
        BEGIN
            CALL OptimizeFleetAssignment(v_operator_rec.Operator_id, TRUE);
            RAISE NOTICE '  -> Optimization completed successfully';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE '  -> Optimization failed: %', SQLERRM;
        END;
    END LOOP;
    
    -- Step 4: Generate maintenance recommendations
    RAISE NOTICE '';
    RAISE NOTICE '======================================';
    RAISE NOTICE 'MAINTENANCE RECOMMENDATIONS';
    RAISE NOTICE '======================================';
    
    -- Check warehouse capacity for maintenance
    FOR v_operator_rec IN 
        SELECT 
            w.warehouse_id,
            w.location,
            COUNT(DISTINCT t.train_id) as trains_needing_maintenance,
            COUNT(DISTINCT e.employee_id) as maintenance_staff
        FROM warehouses w
        LEFT JOIN trains t ON w.warehouse_id = t.warehouse_id 
            AND t.next_check <= CURRENT_DATE + INTERVAL '30 days'
        LEFT JOIN WorksAt wa ON w.warehouse_id = wa.warehouse_id
        LEFT JOIN employees e ON wa.employee_id = e.employee_id 
            AND e.role IN ('Maintenance Technician', 'Train Engineer')
        GROUP BY w.warehouse_id, w.location
        HAVING COUNT(DISTINCT t.train_id) > 0
        ORDER BY COUNT(DISTINCT t.train_id) DESC
    LOOP
        RAISE NOTICE 'Warehouse %:', v_operator_rec.location;
        RAISE NOTICE '  - Trains needing maintenance: %', v_operator_rec.trains_needing_maintenance;
        RAISE NOTICE '  - Available maintenance staff: %', v_operator_rec.maintenance_staff;
        
        IF v_operator_rec.maintenance_staff < v_operator_rec.trains_needing_maintenance THEN
            RAISE WARNING '  -> Consider hiring additional maintenance staff!';
        END IF;
    END LOOP;
    
    -- Step 5: Update maintenance logs
    RAISE NOTICE '';
    RAISE NOTICE 'Updating maintenance logs...';
    
    -- Simulate maintenance completion for some vehicles
    UPDATE trains
    SET last_check = CURRENT_DATE
    WHERE train_id IN (
        SELECT train_id 
        FROM trains 
        WHERE next_check = CURRENT_DATE
        LIMIT 2
    );
    
    UPDATE Plane
    SET last_maintenance = CURRENT_DATE,
        Status = 'ACTIVE'
    WHERE Plane_id IN (
        SELECT Plane_id 
        FROM Plane 
        WHERE Status = 'MAINTENANCE_REQUIRED'
        AND last_maintenance < CURRENT_DATE - INTERVAL '7 days'
        LIMIT 2
    );
    
    RAISE NOTICE '';
    RAISE NOTICE '======================================';
    RAISE NOTICE 'PROGRAM COMPLETED SUCCESSFULLY';
    RAISE NOTICE 'End Time: %', CURRENT_TIMESTAMP;
    RAISE NOTICE '======================================';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Program error: %', SQLERRM;
        RAISE;
END;
$$;