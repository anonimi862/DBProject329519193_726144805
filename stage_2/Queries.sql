-- שאילתא 1: מציאת המחסנים עם הכי הרבה חלקים שונים ומספר העובדים בכל מחסן
-- השאילתא מחזירה מידע על מחסנים, כמות סוגי החלקים, סך כל החלקים, ומספר העובדים
SELECT 
    w.warehouse_id,
    w.location,
    COUNT(DISTINCT wp.part_id) as different_parts_count,
    SUM(wp.wQuantity) as total_parts_quantity,
    COUNT(DISTINCT wa.employee_id) as employee_count
FROM Warehouse w
LEFT JOIN WarehouseParts wp ON w.warehouse_id = wp.warehouse_id
LEFT JOIN WorksAt wa ON w.warehouse_id = wa.warehouse_id
GROUP BY w.warehouse_id, w.location
HAVING COUNT(DISTINCT wp.part_id) > 5
ORDER BY different_parts_count DESC, total_parts_quantity DESC;

-- שאילתא 2: מציאת עובדים שלא עברו הכשרה בשנה האחרונה עם פרטי המחסן שלהם
-- השאילתא מזהה עובדים שזקוקים להכשרה ומציגה היכן הם עובדים
SELECT 
    e.employee_id,
    e.name as employee_name,
    e.role,
    e.last_training,
    DATEDIFF(CURDATE(), e.last_training) as days_since_training,
    w.location as warehouse_location,
    w.warehouse_id
FROM employee e
INNER JOIN WorksAt wa ON e.employee_id = wa.employee_id
INNER JOIN Warehouse w ON wa.warehouse_id = w.warehouse_id
WHERE e.last_training < DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
ORDER BY days_since_training DESC;

-- שאילתא 3: ניתוח הזמנות לפי חודש ושנה עם סך העלויות
-- השאילתא מציגה סטטיסטיקות של הזמנות מקובצות לפי תקופות זמן
SELECT 
    YEAR(o.order_date) as order_year,
    MONTH(o.order_date) as order_month,
    COUNT(o.order_id) as total_orders,
    SUM(o.amount) as total_units_ordered,
    SUM(o.amount * sp.price) as total_cost,
    AVG(DATEDIFF(o.arrival_date, o.order_date)) as avg_delivery_days
FROM myorder o
INNER JOIN SupplierParts sp ON o.supplier_id = sp.supplier_id AND o.part_id = sp.part_id
WHERE o.order_date >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
GROUP BY YEAR(o.order_date), MONTH(o.order_date)
ORDER BY order_year DESC, order_month DESC;

-- שאילתא 4: מציאת החלקים הפופולריים ביותר עם מידע על ספקים ומחירים
-- השאילתא משתמשת בתת-שאילתא למציאת החלקים המוזמנים ביותר
SELECT 
    p.part_id,
    p.name as part_name,
    p.last_update,
    popular_parts.total_ordered,
    COUNT(DISTINCT sp.supplier_id) as supplier_count,
    MIN(sp.price) as min_price,
    MAX(sp.price) as max_price,
    AVG(sp.price) as avg_price
FROM Part p
INNER JOIN (
    SELECT part_id, SUM(amount) as total_ordered
    FROM myorder
    WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
    GROUP BY part_id
    HAVING SUM(amount) > 100
) popular_parts ON p.part_id = popular_parts.part_id
LEFT JOIN SupplierParts sp ON p.part_id = sp.part_id
GROUP BY p.part_id, p.name, p.last_update, popular_parts.total_ordered
ORDER BY popular_parts.total_ordered DESC;

-- שאילתא 5: ניתוח רכבות לפי מחסן עם בדיקת תחזוקה קרובה
-- השאילתא מציגה רכבות שזקוקות לבדיקה בחודש הקרוב
SELECT 
    t.train_id,
    t.model,
    t.year,
    t.last_check,
    t.next_check,
    DATEDIFF(t.next_check, CURDATE()) as days_until_check,
    w.location as warehouse_location,
    w.capacity as warehouse_capacity,
    (SELECT COUNT(*) FROM Train t2 WHERE t2.warehouse_id = w.warehouse_id) as trains_in_warehouse
FROM Train t
INNER JOIN Warehouse w ON t.warehouse_id = w.warehouse_id
WHERE t.next_check <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
ORDER BY days_until_check ASC;

-- שאילתא 6: ניתוח לקוחות ואחסון במחסנים עם חישוב תקופת אחסון
-- השאילתא מציגה לקוחות פעילים וכמה זמן הם משתמשים בשירותי האחסון
SELECT 
    c.costumer_id,
    c.email,
    c.phone,
    DATEDIFF(CURDATE(), c.registration_date) as days_as_customer,
    COUNT(cws.warehouse_id) as warehouses_used,
    MIN(cws.start_date) as earliest_storage,
    MAX(cws.end_date) as latest_storage,
    SUM(DATEDIFF(COALESCE(cws.end_date, CURDATE()), cws.start_date)) as total_storage_days
FROM Costumer c
LEFT JOIN CostumerWarehousStorage cws ON c.costumer_id = cws.costumer_id
WHERE c.registration_date >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
GROUP BY c.costumer_id, c.email, c.phone, c.registration_date
HAVING warehouses_used > 0
ORDER BY total_storage_days DESC;

-- שאילתא 7: דו"ח מלאי מפורט לפי מחסן עם השוואה לקיבולת
-- השאילתא מציגה ניצול קיבולת המחסנים ומזהה מחסנים עמוסים
SELECT 
    w.warehouse_id,
    w.location,
    w.capacity,
    YEAR(w.open_date) as open_year,
    warehouse_inventory.total_items,
    warehouse_inventory.unique_parts,
    ROUND((warehouse_inventory.total_items / w.capacity) * 100, 2) as capacity_usage_percent,
    warehouse_value.total_value
FROM Warehouse w
LEFT JOIN (
    SELECT 
        warehouse_id,
        SUM(wQuantity) as total_items,
        COUNT(DISTINCT part_id) as unique_parts
    FROM WarehouseParts
    GROUP BY warehouse_id
) warehouse_inventory ON w.warehouse_id = warehouse_inventory.warehouse_id
LEFT JOIN (
    SELECT 
        wp.warehouse_id,
        SUM(wp.wQuantity * sp.price) as total_value
    FROM WarehouseParts wp
    INNER JOIN (
        SELECT part_id, AVG(price) as price
        FROM SupplierParts
        GROUP BY part_id
    ) sp ON wp.part_id = sp.part_id
    GROUP BY wp.warehouse_id
) warehouse_value ON w.warehouse_id = warehouse_value.warehouse_id
WHERE warehouse_inventory.total_items IS NOT NULL
ORDER BY capacity_usage_percent DESC;

-- שאילתא 8: ניתוח ספקים עם ביצועי משלוחים וטווח מחירים
-- השאילתא משתמשת בכמה רמות של JOIN ותת-שאילתות לניתוח מקיף
SELECT 
    s.supplier_id,
    s.name as supplier_name,
    s.phone,
    supplier_stats.parts_supplied,
    supplier_stats.min_price,
    supplier_stats.max_price,
    supplier_stats.avg_price,
    delivery_stats.total_orders,
    delivery_stats.avg_delivery_time,
    delivery_stats.on_time_percentage
FROM supplier s
INNER JOIN (
    SELECT 
        supplier_id,
        COUNT(DISTINCT part_id) as parts_supplied,
        MIN(price) as min_price,
        MAX(price) as max_price,
        AVG(price) as avg_price
    FROM SupplierParts
    GROUP BY supplier_id
) supplier_stats ON s.supplier_id = supplier_stats.supplier_id
LEFT JOIN (
    SELECT 
        supplier_id,
        COUNT(order_id) as total_orders,
        AVG(DATEDIFF(arrival_date, order_date)) as avg_delivery_time,
        ROUND(
            SUM(CASE WHEN arrival_date <= DATE_ADD(order_date, INTERVAL 7 DAY) THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
            2
        ) as on_time_percentage
    FROM myorder
    WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    GROUP BY supplier_id
) delivery_stats ON s.supplier_id = delivery_stats.supplier_id
WHERE supplier_stats.parts_supplied > 3
ORDER BY delivery_stats.on_time_percentage DESC NULLS LAST;

-- DELETE 1: מחיקת הזמנות ישנות שהגיעו לפני יותר משנתיים
-- השאילתא מוחקת רשומות היסטוריות כדי לשמור על ביצועי המערכת
DELETE FROM myorder
WHERE arrival_date < DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
AND order_id NOT IN (
    SELECT DISTINCT order_id 
    FROM (SELECT order_id FROM myorder WHERE amount > 1000) AS large_orders
);

-- DELETE 2: מחיקת חלקים שלא עודכנו ואין להם מלאי בשום מחסן
-- השאילתא מנקה חלקים לא פעילים מהמערכת
DELETE FROM Part
WHERE part_id IN (
    SELECT p.part_id
    FROM (
        SELECT part_id
        FROM Part
        WHERE last_update < DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
    ) p
    LEFT JOIN WarehouseParts wp ON p.part_id = wp.part_id
    WHERE wp.part_id IS NULL
);

-- DELETE 3: מחיקת רשומות אחסון של לקוחות שהסתיימו לפני יותר משנה
-- השאילתא מוחקת היסטוריית אחסון ישנה
DELETE FROM CostumerWarehousStorage
WHERE end_date < DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
AND costumer_id NOT IN (
    SELECT DISTINCT costumer_id
    FROM CostumerWarehousStorage
    WHERE end_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    OR end_date IS NULL
);

-- UPDATE 1: עדכון תאריך הבדיקה הבאה לרכבות שעברו בדיקה
-- השאילתא מעדכנת את תאריך הבדיקה הבאה ל-6 חודשים קדימה
UPDATE Train
SET 
    last_check = CURDATE(),
    next_check = DATE_ADD(CURDATE(), INTERVAL 6 MONTH)
WHERE train_id IN (
    SELECT train_id FROM (
        SELECT train_id 
        FROM Train 
        WHERE next_check <= CURDATE()
    ) AS trains_to_update
);

-- UPDATE 2: עדכון כמויות במחסן לאחר קבלת הזמנות שהגיעו
-- השאילתא מעדכנת את המלאי במחסנים עבור הזמנות שהגיעו היום
UPDATE WarehouseParts wp
INNER JOIN (
    SELECT 
        warehouse_id, 
        part_id, 
        SUM(amount) as total_amount
    FROM myorder
    WHERE arrival_date = CURDATE()
    GROUP BY warehouse_id, part_id
) arrived_orders ON wp.warehouse_id = arrived_orders.warehouse_id 
                AND wp.part_id = arrived_orders.part_id
SET 
    wp.wQuantity = wp.wQuantity + arrived_orders.total_amount,
    wp.last_updated = CURDATE();

-- UPDATE 3: עדכון תאריך הכשרה אחרונה לעובדים שסיימו הכשרה
-- השאילתא מעדכנת עובדים בתפקידים ספציפיים שעברו הכשרה
UPDATE employee
SET last_training = CURDATE()
WHERE employee_id IN (
    SELECT e.employee_id FROM (
        SELECT employee_id 
        FROM employee 
        WHERE role IN ('Warehouse Manager', 'Forklift Operator')
        AND last_training < DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    ) e
);