-- טריגר 2: תזמון אוטומטי של תחזוקה לרכבות ומטוסים
-- הטריגר מנהל את לוחות הזמנים של התחזוקה ומתריע על בעיות

CREATE OR REPLACE FUNCTION schedule_maintenance()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_maintenance_interval INTERVAL;
    v_location VARCHAR(100);
    v_available_staff INT;
    v_workload INT;
BEGIN
    -- Handle trains maintenance
    IF TG_TABLE_NAME = 'trains' THEN
        -- Calculate maintenance interval based on train age
        IF NEW.year < EXTRACT(YEAR FROM CURRENT_DATE) - 20 THEN
            v_maintenance_interval := INTERVAL '3 months';
        ELSIF NEW.year < EXTRACT(YEAR FROM CURRENT_DATE) - 10 THEN
            v_maintenance_interval := INTERVAL '6 months';
        ELSE
            v_maintenance_interval := INTERVAL '12 months';
        END IF;
        
        -- Auto-update next_check if last_check changed
        IF TG_OP = 'UPDATE' AND NEW.last_check != OLD.last_check THEN
            NEW.next_check := NEW.last_check + v_maintenance_interval;
            
            -- Get warehouse location
            SELECT location INTO v_location
            FROM warehouses
            WHERE warehouse_id = NEW.warehouse_id;
            
            RAISE NOTICE 'Train % maintenance completed at %. Next check: %',
                NEW.train_id, v_location, NEW.next_check;
        END IF;
        
        -- Check for overdue maintenance
        IF NEW.next_check < CURRENT_DATE THEN
            RAISE WARNING 'Train % is OVERDUE for maintenance by % days!',
                NEW.train_id, CURRENT_DATE - NEW.next_check;
        ELSIF NEW.next_check <= CURRENT_DATE + INTERVAL '7 days' THEN
            -- Check staff availability
            SELECT COUNT(*) INTO v_available_staff
            FROM employees e
            INNER JOIN WorksAt wa ON e.employee_id = wa.employee_id
            WHERE wa.warehouse_id = NEW.warehouse_id
            AND e.role IN ('Maintenance Technician', 'Train Engineer');
            
            IF v_available_staff < 2 THEN
                RAISE WARNING 'Insufficient maintenance staff at warehouse % for train %',
                    NEW.warehouse_id, NEW.train_id;
            END IF;
        END IF;
        
    -- Handle planes maintenance
    ELSIF TG_TABLE_NAME = 'Plane' THEN
        -- Check if maintenance is needed based on flight hours
        IF NEW.flight_hours - COALESCE(OLD.flight_hours, 0) > 100 THEN
            -- Check if maintenance is due
            IF NEW.last_maintenance < CURRENT_DATE - INTERVAL '6 months' OR
               NEW.flight_hours > 5000 THEN
                
                NEW.Status := 'MAINTENANCE_REQUIRED';
                
                -- Count planes needing maintenance in same hangar
                SELECT COUNT(*) INTO v_workload
                FROM Plane
                WHERE Hangar_id = NEW.Hangar_id
                AND Status = 'MAINTENANCE_REQUIRED';
                
                IF v_workload > 3 THEN
                    RAISE WARNING 'Hangar % has % planes awaiting maintenance',
                        NEW.Hangar_id, v_workload;
                END IF;
            END IF;
        END IF;
        
        -- Auto-update status based on last maintenance
        IF TG_OP = 'UPDATE' AND NEW.last_maintenance != OLD.last_maintenance THEN
            IF NEW.last_maintenance = CURRENT_DATE THEN
                NEW.Status := 'ACTIVE';
                NEW.flight_hours := 0; -- Reset flight hours after major maintenance
                
                RAISE NOTICE 'Plane % maintenance completed. Status: ACTIVE',
                    NEW.Plane_id;
            END IF;
        END IF;
    END IF;
    
    RETURN NEW;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in schedule_maintenance: %', SQLERRM;
        RAISE;
END;
$$;

-- Create triggers for both tables
DROP TRIGGER IF EXISTS trg_train_maintenance ON trains;
CREATE TRIGGER trg_train_maintenance
BEFORE INSERT OR UPDATE ON trains
FOR EACH ROW
EXECUTE FUNCTION schedule_maintenance();

DROP TRIGGER IF EXISTS trg_plane_maintenance ON Plane;
CREATE TRIGGER trg_plane_maintenance
BEFORE INSERT OR UPDATE ON Plane
FOR EACH ROW
EXECUTE FUNCTION schedule_maintenance();