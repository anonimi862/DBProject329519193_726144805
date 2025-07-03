-- אילוץ 1: הוספת בדיקה על קיבולת המחסן - חייבת להיות חיובית ולא יותר מ-1,000,000
ALTER TABLE Warehouse
ADD CONSTRAINT chk_warehouse_capacity 
CHECK (capacity > 0 AND capacity <= 1000000);

-- אילוץ 2: הוספת ערך ברירת מחדל לתאריך רישום של לקוח
ALTER TABLE Costumer
ALTER COLUMN registration_date SET DEFAULT (CURDATE());

-- אילוץ 3: הוספת בדיקה על מחיר החלק - חייב להיות חיובי
ALTER TABLE SupplierParts
ADD CONSTRAINT chk_positive_price 
CHECK (price > 0);

-- אילוץ 4: הוספת בדיקה על כמות בהזמנה - חייבת להיות חיובית
ALTER TABLE myorder
ADD CONSTRAINT chk_order_amount 
CHECK (amount > 0);

-- אילוץ 5: הוספת בדיקה שתאריך הגעה חייב להיות אחרי תאריך הזמנה
ALTER TABLE myorder
ADD CONSTRAINT chk_order_dates 
CHECK (arrival_date >= order_date);

-- אילוץ 6: הוספת בדיקה על שנת ייצור הרכבת - לא יכולה להיות בעתיד
ALTER TABLE Train
ADD CONSTRAINT chk_train_year 
CHECK (year <= YEAR(CURDATE()));

-- אילוץ 7: הוספת בדיקה שתאריך סיום אחסון חייב להיות אחרי תאריך התחלה
ALTER TABLE CostumerWarehousStorage
ADD CONSTRAINT chk_storage_dates 
CHECK (end_date IS NULL OR end_date >= start_date);

-- אילוץ 8: הוספת ערך ברירת מחדל לכמות במחסן
ALTER TABLE WarehouseParts
ALTER COLUMN wQuantity SET DEFAULT 0;

-- אילוץ 9: הוספת בדיקה על פורמט מספר טלפון
ALTER TABLE supplier
ADD CONSTRAINT chk_supplier_phone 
CHECK (phone REGEXP '^[0-9]{9,15}$');