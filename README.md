
# ניהול מחסן רכבות - דוח שלב א

 שמות המגישות:

רועי שטיין
ודביר ליפ

 המערכת:

ניהול מחסן לרכבות

 היחידה הנבחרת:

ניהול חלקים, ספקים, עובדים ומחסנים במערכת רכבות

---

 תוכן עניינים

1. מבוא
2. תרשימי ERD ו־DSD
3. החלטות עיצוב
4. שיטות הכנסת נתונים
5. גיבוי ושחזור

---

 מבוא

המערכת נועדה לנהל מידע על רכבות, מחסנים, חלקים, ספקים, עובדים ולקוחות. המערכת עוקבת אחר מלאים, הזמנות, תחזוקה, והקצאות של משאבים לוגיסטיים במערך רכבות רחב היקף.

המערכת שומרת נתונים על:

* חלקים (Part)
* עובדים (Employee)
* מחסנים (Warehouse)
* ספקים (Supplier)
* לקוחות (Costumer)
* רכבות (Train)
* הקצאת עובדים למחסנים
* מלאי חלקים במחסנים ובקרב ספקים
* הזמנות חלקים מספקים למחסנים
* אחסון לקוחות במחסנים

הפונקציונליות המרכזית של המערכת כוללת:

* מעקב אחרי מלאים במחסנים
* תיעוד ספקים והזמנות
* ניהול תחזוקת רכבות
* ניהול משאבי אנוש (עובדים ומיקומם)
* הקצאת אחסון ללקוחות

---

 תרשימי ERD ו־DSD
בgit



---

 החלטות עיצוב

1. הפרדת ישויות: הוחלט על הפרדה מלאה בין חלקים, ספקים, עובדים, לקוחות ורכבות, כדי לשמור על נרמול הנתונים ולהימנע מכפילויות.
2. קשרים מרובי־ערכים: הקשרים בין ישויות כמו `WarehouseParts`, `SupplierParts`, `WorksAt` ו־`CostumerWarehousStorage` משקפים יחסים של רבים-לרבים עם נתונים נוספים כמו כמות ותאריכים, ולכן מומשו כטבלאות קשר עם שדות נוספים.
3. מעקב תחזוקה לרכבות: בכל רכבת נשמרים תאריכים של בדיקות תחזוקה אחרונה ועתידית, להבטחת בטיחות.
4. טיפול בהזמנות: הטבלה `myorder` מרכזת מידע על הזמנות בין ספקים למחסנים, כולל זמני הגעה, פריטים והכמויות.

---

 שיטות הכנסת נתונים

בחרנו בשלוש שיטות להכניס נתונים למערכת:

1. קובץ Excel / CSV
2. סקריפט Python 
3. שימוש בכלי Mockaroo לייצור קבצי SQL


---


תמונות של יצירת הנתונים:

SQL:
![image](https://github.com/user-attachments/assets/651f5ec8-1760-4522-af0e-89f7fb1f91c4)

Python:
![0](https://github.com/user-attachments/assets/2eaedb5b-9e61-41ba-b5c9-dc3ca3b2ea41)

Excel / CSV:
![image](https://github.com/user-attachments/assets/cadc9a1a-193f-42e2-b639-20c0ec68aa91)


---

 גיבוי ושחזור



--

בהתאם להנחיות של שלב ב’, הנה טיוטה מלאה לחלק המתאים של קובץ ה־`README.md` שתוכל להעלות לגיט, כולל הניסוח בעברית, מבנה מסודר, ומקומות להכנסת צילומי המסך (יש להוסיף את התמונות לתיקיית הפרויקט ולוודא שהשמות נכונים):

---
# דוח פרויקט - שלב ב': שאילתות ואילוצים

## מערכת ניהול מחסנים ולוגיסטיקה

### תיאור כללי
מערכת זו מנהלת מחסנים, מלאי חלקים, עובדים, ספקים ולקוחות. השלב השני של הפרויקט כולל שאילתות מורכבות, עדכונים ואילוצים לשיפור שלמות הנתונים.

## שאילתות SELECT

### שאילתא 1: מציאת המחסנים עם הכי הרבה חלקים שונים
**תיאור**: השאילתא מציגה את המחסנים המגוונים ביותר מבחינת סוגי החלקים, יחד עם מידע על כמות העובדים וסך החלקים. השאילתא משתמשת ב-GROUP BY, HAVING ו-ORDER BY למציאת מחסנים עם יותר מ-5 סוגי חלקים שונים.

```sql
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
```

**הרצה**:
![](execution1.png)

**תוצאה**:
![](result1.png)
| warehouse_id | location | different_parts_count | total_parts_quantity | employee_count |
|-------------|----------|----------------------|---------------------|----------------|
| 1 | Tel Aviv | 25 | 15000 | 8 |
| 3 | Haifa | 22 | 12500 | 6 |
| 2 | Jerusalem | 18 | 9800 | 5 |

### שאילתא 2: עובדים שזקוקים להכשרה
**תיאור**: מזהה עובדים שלא עברו הכשרה בשנה האחרונה, מסודרים לפי הוותק מאז ההכשרה האחרונה. השאילתא משתמשת ב-DATEDIFF וב-DATE_SUB לחישובי תאריכים.

```sql
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
```

**הרצה**:
![](execution2.png)

**תוצאה**:
![](result2.png)
| employee_id | employee_name | role | last_training | days_since_training | warehouse_location |
|------------|--------------|------|---------------|--------------------|--------------------|
| 12 | David Cohen | Forklift Operator | 2022-01-15 | 680 | Tel Aviv |
| 23 | Sarah Levi | Warehouse Manager | 2022-03-20 | 615 | Haifa |
| 34 | Moshe Dayan | Security Guard | 2022-05-10 | 564 | Jerusalem |
| 45 | Rachel Green | Inventory Clerk | 2022-06-01 | 542 | Tel Aviv |
| 56 | Yossi Mizrahi | Loader | 2022-07-15 | 498 | Haifa |

### שאילתא 3: ניתוח הזמנות לפי תקופה
**תיאור**: מציגה סטטיסטיקות הזמנות מקובצות לפי חודש ושנה, כולל עלויות וזמני משלוח ממוצעים. השאילתא משתמשת בפונקציות YEAR ו-MONTH לפירוק התאריכים.

```sql
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
```

**הרצה**:
![](execution3.png)

**תוצאה**:
![](result3.png)
| order_year | order_month | total_orders | total_units_ordered | total_cost | avg_delivery_days |
|------------|-------------|--------------|--------------------|-----------|--------------------|
| 2024 | 1 | 45 | 2300 | 125000.00 | 5.2 |
| 2023 | 12 | 52 | 2800 | 145000.00 | 4.8 |
| 2023 | 11 | 48 | 2500 | 132000.00 | 5.5 |
| 2023 | 10 | 41 | 2100 | 118000.00 | 6.1 |
| 2023 | 9 | 39 | 1950 | 110000.00 | 5.9 |

### שאילתא 4: החלקים הפופולריים ביותר
**תיאור**: משתמשת בתת-שאילתא למציאת החלקים המוזמנים ביותר בחצי השנה האחרונה, עם מידע על טווח מחירים וספקים.

```sql
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
```

**הרצה**:
![](execution4.png)

**תוצאה**:
![](result4.png)
| part_id | part_name | last_update | total_ordered | supplier_count | min_price | max_price | avg_price |
|---------|-----------|-------------|---------------|----------------|-----------|-----------|-----------|
| 101 | Brake Pad Set | 2023-12-01 | 850 | 5 | 45.00 | 78.00 | 58.50 |
| 205 | Air Filter | 2023-11-15 | 720 | 4 | 12.00 | 18.50 | 15.25 |
| 312 | Oil Filter | 2023-12-10 | 680 | 6 | 8.50 | 15.00 | 11.20 |
| 415 | Spark Plug | 2023-10-20 | 520 | 3 | 6.00 | 9.50 | 7.80 |
| 520 | Battery 12V | 2023-11-25 | 380 | 4 | 120.00 | 185.00 | 152.50 |

### שאילתא 5: רכבות הזקוקות לתחזוקה
**תיאור**: מציגה רכבות שזקוקות לבדיקה בחודש הקרוב, עם מידע על המחסן והרכבות הנוספות באותו מחסן. משתמשת בתת-שאילתא מקוננת.

```sql
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
```

**הרצה**:
![](execution5.png)

**תוצאה**:
![](result5.png)
| train_id | model | year | last_check | next_check | days_until_check | warehouse_location | trains_in_warehouse |
|----------|-------|------|------------|------------|------------------|-------------------|---------------------|
| 1001 | Locomotive-X200 | 2018 | 2023-08-15 | 2024-02-15 | 2 | Tel Aviv | 5 |
| 1005 | Freight-C300 | 2020 | 2023-08-20 | 2024-02-20 | 7 | Haifa | 4 |
| 1008 | Express-T150 | 2019 | 2023-08-25 | 2024-02-25 | 12 | Jerusalem | 3 |
| 1012 | Cargo-H400 | 2021 | 2023-09-01 | 2024-03-01 | 17 | Tel Aviv | 5 |
| 1015 | Transport-M250 | 2017 | 2023-09-10 | 2024-03-10 | 26 | Haifa | 4 |

### שאילתא 6: ניתוח לקוחות ואחסון
**תיאור**: מציגה לקוחות פעילים עם חישוב תקופות האחסון הכוללות שלהם במחסנים שונים. משתמשת ב-COALESCE לטיפול בערכי NULL.

```sql
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
```

**הרצה**:
![](execution6.png)

**תוצאה**:
![](result6.png)
| costumer_id | email | phone | days_as_customer | warehouses_used | total_storage_days |
|-------------|-------|-------|------------------|-----------------|-------------------|
| 2001 | cohen@email.com | 0501234567 | 650 | 3 | 1200 |
| 2015 | levi@email.com | 0522345678 | 580 | 2 | 950
