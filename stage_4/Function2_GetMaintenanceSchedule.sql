-- פונקציה 2: החזרת לוח זמנים לתחזוקת רכבות ומטוסים
-- הפונקציה מחזירה REF CURSOR עם כל הכלים הזקוקים לתחזוקה

CREATE OR REPLACE FUNCTION GetMaintenanceSchedule(
    p_days_ahead INT DEFAULT 30,
    p_location VARCHAR(100) DEFAULT NULL
)
RETURNS refcursor
LANGUAGE plpgsql
AS $$
DECLARE
    -- Ref cursor to return
    maintenance_cursor refcursor;
    
    -- Variables for statistics
    v_train_count INT := 0;
    v_plane_count INT := 0;
    v_urgent_count INT := 0;
    
    -- Record for counting
    maint_rec RECORD;
    
BEGIN
    -- Validate input
    IF p_days_ahead < 0 THEN
        RAISE EXCEPTION 'Days ahead must be positive';
    END IF;
    
    -- Count items needing maintenance using implicit cursor
    FOR maint_rec IN 
        SELECT 
            'TRAIN' as vehicle_type,
            next_check
        FROM trains t
        INNER JOIN warehouses w ON t.warehouse_id = w.warehouse_id
        WHERE t.next_check <= CURRENT_DATE + INTERVAL '1 day' * p_days_ahead
        AND (p_location IS NULL OR w.location = p_location)
        
        UNION ALL
        
        SELECT 
            'PLANE' as vehicle_type,
            last_maintenance + INTERVAL '6 months' as next_check
        FROM Plane p
        INNER JOIN Hangar h ON p.Hangar_id = h.Hangar_id
        WHERE last_maintenance + INTERVAL '6 months' <= CURRENT_DATE + INTERVAL '1 day' * p_days_ahead
        AND (p_location IS NULL OR h.Location = p_location)
    LOOP
        IF maint_rec.vehicle_type = 'TRAIN' THEN
            v_train_count := v_train_count + 1;
        ELSE
            v_plane_count := v_plane_count + 1;
        END IF;
        
        IF maint_rec.next_check <= CURRENT_DATE + INTERVAL '7 days' THEN
            v_urgent_count := v_urgent_count + 1;
        END IF;
    END LOOP;
    
    -- Log summary
    RAISE NOTICE 'Maintenance Schedule Summary: % trains, % planes, % urgent', 
        v_train_count, v_plane_count, v_urgent_count;
    
    -- Open and return cursor with detailed schedule
    OPEN maintenance_cursor FOR
        SELECT 
            'TRAIN' as vehicle_type,
            t.train_id as vehicle_id,
            t.model,
            t.year,
            t.last_check,
            t.next_check,
            EXTRACT(DAY FROM (t.next_check - CURRENT_DATE)) as days_until_maintenance,
            w.location,
            COUNT(wa.employee_id) as available_staff,
            CASE 
                WHEN t.next_check <= CURRENT_DATE THEN 'OVERDUE'
                WHEN t.next_check <= CURRENT_DATE + INTERVAL '7 days' THEN 'URGENT'
                WHEN t.next_check <= CURRENT_DATE + INTERVAL '14 days' THEN 'SOON'
                ELSE 'SCHEDULED'
            END as priority
        FROM trains t
        INNER JOIN warehouses w ON t.warehouse_id = w.warehouse_id
        LEFT JOIN WorksAt wa ON w.warehouse_id = wa.warehouse_id
        WHERE t.next_check <= CURRENT_DATE + INTERVAL '1 day' * p_days_ahead
        AND (p_location IS NULL OR w.location = p_location)
        GROUP BY t.train_id, t.model, t.year, t.last_check, t.next_check, w.location
        
        UNION ALL
        
        SELECT 
            'PLANE' as vehicle_type,
            p.Plane_id as vehicle_id,
            p.Model,
            EXTRACT(YEAR FROM p.ProductionDate)::INT as year,
            p.last_maintenance as last_check,
            p.last_maintenance + INTERVAL '6 months' as next_check,
            EXTRACT(DAY FROM (p.last_maintenance + INTERVAL '6 months' - CURRENT_DATE)) as days_until_maintenance,
            h.Location as location,
            COUNT(DISTINCT pi.Pilot_id) as available_staff,
            CASE 
                WHEN p.last_maintenance + INTERVAL '6 months' <= CURRENT_DATE THEN 'OVERDUE'
                WHEN p.last_maintenance + INTERVAL '6 months' <= CURRENT_DATE + INTERVAL '7 days' THEN 'URGENT'
                WHEN p.last_maintenance + INTERVAL '6 months' <= CURRENT_DATE + INTERVAL '14 days' THEN 'SOON'
                ELSE 'SCHEDULED'
            END as priority
        FROM Plane p
        INNER JOIN Hangar h ON p.Hangar_id = h.Hangar_id
        LEFT JOIN Operated_by ob ON p.Plane_id = ob.Plane_id
        LEFT JOIN Pilot pi ON ob.Operator_id = pi.Operator_id
        WHERE p.last_maintenance + INTERVAL '6 months' <= CURRENT_DATE + INTERVAL '1 day' * p_days_ahead
        AND (p_location IS NULL OR h.Location = p_location)
        GROUP BY p.Plane_id, p.Model, p.ProductionDate, p.last_maintenance, h.Location
        
        ORDER BY priority DESC, days_until_maintenance ASC;
    
    RETURN maintenance_cursor;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in GetMaintenanceSchedule: %', SQLERRM;
        RAISE;
END;
$$;