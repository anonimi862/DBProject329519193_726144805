-- פרוצדורה 2: אופטימיזציה של הקצאת צי מטוסים וטייסים
-- הפרוצדורה מאזנת את הקצאת הטייסים למטוסים ומעדכנת סטטוסים

CREATE OR REPLACE PROCEDURE OptimizeFleetAssignment(
    p_operator_id INT DEFAULT NULL,
    p_rebalance BOOLEAN DEFAULT TRUE
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- Record types
    TYPE pilot_workload IS RECORD (
        pilot_id INT,
        pilot_name VARCHAR(100),
        experience INT,
        plane_count INT
    );
    
    TYPE plane_status IS RECORD (
        plane_id INT,
        model VARCHAR(50),
        status VARCHAR(20),
        pilot_count INT,
        flight_hours INT
    );
    
    -- Variables
    v_pilot pilot_workload;
    v_plane plane_status;
    v_reassignment_count INT := 0;
    v_status_update_count INT := 0;
    v_operator_name VARCHAR(100);
    
    -- Cursor for underutilized pilots
    CURSOR pilot_cursor(op_id INT) IS
        SELECT 
            p.Pilot_id,
            p.Name,
            p.Experience,
            COUNT(pp.Plane_id) as plane_count
        FROM Pilot p
        LEFT JOIN Pilot_Plane pp ON p.Pilot_id = pp.Pilot_id
        WHERE (op_id IS NULL OR p.Operator_id = op_id)
        GROUP BY p.Pilot_id, p.Name, p.Experience
        HAVING COUNT(pp.Plane_id) < 2
        ORDER BY p.Experience DESC;
    
BEGIN
    RAISE NOTICE 'Starting fleet optimization process...';
    
    -- Get operator name if specified
    IF p_operator_id IS NOT NULL THEN
        SELECT Name INTO v_operator_name
        FROM Operator
        WHERE Operator_id = p_operator_id;
        
        IF v_operator_name IS NULL THEN
            RAISE EXCEPTION 'Operator % not found', p_operator_id;
        END IF;
        
        RAISE NOTICE 'Optimizing fleet for operator: %', v_operator_name;
    END IF;
    
    -- Step 1: Update plane status based on flight hours
    FOR v_plane IN 
        SELECT 
            p.Plane_id,
            p.Model,
            p.Status,
            p.flight_hours,
            COUNT(pp.Pilot_id) as pilot_count
        FROM Plane p
        LEFT JOIN Pilot_Plane pp ON p.Plane_id = pp.Plane_id
        WHERE p.Status != 'RETIRED'
        GROUP BY p.Plane_id, p.Model, p.Status, p.flight_hours
    LOOP
        -- Update status based on flight hours
        IF v_plane.flight_hours > 20000 THEN
            UPDATE Plane
            SET Status = 'MAINTENANCE_REQUIRED'
            WHERE Plane_id = v_plane.plane_id
            AND Status != 'MAINTENANCE_REQUIRED';
            
            v_status_update_count := v_status_update_count + 1;
            
            RAISE NOTICE 'Plane % requires maintenance (% flight hours)', 
                v_plane.plane_id, v_plane.flight_hours;
        ELSIF v_plane.flight_hours > 15000 AND v_plane.status = 'ACTIVE' THEN
            UPDATE Plane
            SET Status = 'LIMITED_SERVICE'
            WHERE Plane_id = v_plane.plane_id;
            
            v_status_update_count := v_status_update_count + 1;
        END IF;
        
        -- Check pilot assignment
        IF v_plane.pilot_count = 0 AND v_plane.status = 'ACTIVE' THEN
            RAISE WARNING 'Active plane % has no assigned pilots!', v_plane.plane_id;
        END IF;
    END LOOP;
    
    -- Step 2: Rebalance pilot assignments if requested
    IF p_rebalance THEN
        FOR v_pilot IN pilot_cursor(p_operator_id) LOOP
            -- Find planes that need more pilots
            DECLARE
                v_target_plane_id INT;
                v_assignment_date DATE;
            BEGIN
                SELECT p.Plane_id INTO v_target_plane_id
                FROM Plane p
                LEFT JOIN Pilot_Plane pp ON p.Plane_id = pp.Plane_id
                LEFT JOIN Operated_by ob ON p.Plane_id = ob.Plane_id
                WHERE p.Status = 'ACTIVE'
                AND (p_operator_id IS NULL OR ob.Operator_id = p_operator_id)
                GROUP BY p.Plane_id
                HAVING COUNT(pp.Pilot_id) < 3
                ORDER BY COUNT(pp.Pilot_id) ASC
                LIMIT 1;
                
                IF v_target_plane_id IS NOT NULL THEN
                    -- Check if assignment already exists
                    IF NOT EXISTS (
                        SELECT 1 FROM Pilot_Plane 
                        WHERE Pilot_id = v_pilot.pilot_id 
                        AND Plane_id = v_target_plane_id
                    ) THEN
                        -- Create new assignment
                        v_assignment_date := CURRENT_DATE;
                        
                        INSERT INTO Pilot_Plane (Pilot_id, Plane_id, Assignment_date)
                        VALUES (v_pilot.pilot_id, v_target_plane_id, v_assignment_date);
                        
                        v_reassignment_count := v_reassignment_count + 1;
                        
                        RAISE NOTICE 'Assigned pilot % (exp: %) to plane %',
                            v_pilot.pilot_name, v_pilot.experience, v_target_plane_id;
                    END IF;
                END IF;
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING 'Failed to assign pilot %: %', v_pilot.pilot_id, SQLERRM;
            END;
        END LOOP;
    END IF;
    
    -- Step 3: Update fleet statistics for operators
    IF p_operator_id IS NOT NULL THEN
        UPDATE Operator
        SET Fleet_Size = (
            SELECT COUNT(DISTINCT ob.Plane_id)
            FROM Operated_by ob
            INNER JOIN Plane p ON ob.Plane_id = p.Plane_id
            WHERE ob.Operator_id = p_operator_id
            AND p.Status IN ('ACTIVE', 'LIMITED_SERVICE')
        )
        WHERE Operator_id = p_operator_id;
    END IF;
    
    -- Final report
    RAISE NOTICE '======================================';
    RAISE NOTICE 'Fleet Optimization Complete';
    RAISE NOTICE 'Status Updates: %', v_status_update_count;
    RAISE NOTICE 'Pilot Reassignments: %', v_reassignment_count;
    RAISE NOTICE '======================================';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in OptimizeFleetAssignment: %', SQLERRM;
        RAISE;
END;
$$;