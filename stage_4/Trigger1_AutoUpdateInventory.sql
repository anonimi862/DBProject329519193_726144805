        -- Update or insert inventory
        INSERT INTO warehouseparts (part_id, warehouse_id, warehouse_quantity, last_updated)
        VALUES (NEW.part_id, NEW.warehouse_id, NEW.amount, CURRENT_DATE)
        ON CONFLICT (part_id, warehouse_id) 
        DO UPDATE SET 
            warehouse_quantity = warehouseparts.warehouse_quantity + NEW.amount,
            last_updated = CURRENT_DATE;
        
        -- Update part last_update
        UPDATE part
        SET last_update = CURRENT_DATE
        WHERE part_id = NEW.part_id;
        
        -- Log the update
        RAISE NOTICE 'Inventory updated: Added % units of % from supplier % to warehouse %',
            NEW.amount, v_part_name, v_supplier_name, NEW.warehouse_id;
        
        -- Check if reorder is needed for other warehouses
        PERFORM 1
        FROM warehouseparts wp
        INNER JOIN warehouses w ON wp.warehouse_id = w.warehouse_id
        WHERE wp.part_id = NEW.part_id
        AND wp.warehouse_quantity < 50
        AND wp.warehouse_id != NEW.warehouse_id;
        
        IF FOUND THEN
            RAISE NOTICE 'Warning: Other warehouses have low stock of %', v_part_name;
        END IF;
    END IF;
    
    -- For new orders, validate supplier has the part
    IF TG_OP = 'INSERT' THEN
        IF NOT EXISTS (
            SELECT 1 FROM SupplierParts 
            WHERE supplier_id = NEW.supplier_id 
            AND part_id = NEW.part_id
        ) THEN
            RAISE EXCEPTION 'Supplier % does not supply part %', NEW.supplier_id, NEW.part_id;
        END IF;
    END IF;
    
    RETURN NEW;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in auto_update_inventory: %', SQLERRM;
        RAISE;
END;
$$;

-- Create the trigger
DROP TRIGGER IF EXISTS trg_auto_update_inventory ON myorder;
CREATE TRIGGER trg_auto_update_inventory
BEFORE INSERT OR UPDATE ON myorder
FOR EACH ROW
EXECUTE FUNCTION auto_update_inventory();