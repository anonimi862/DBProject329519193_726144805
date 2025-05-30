
# ניהול מחסן רכבות - דוח שלב א

 שמות המגישות:

רועי שטיין
דביר ליפ

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

## שלב ב – שאילתות ועדכונים

### שאילתות SELECT

#### 1. רשימת כל החלקים עם שם הספק, כמות במחסן, ומחסן

**תיאור:** מציגה לכל חלק את שם הספק שמספק אותו, כמה ממנו יש בכל מחסן, ומה מיקומו של המחסן.

```sql
SELECT p.name AS part_name, s.name AS supplier_name, wp.wQuantity, w.location AS warehouse_location
FROM Part p
JOIN SupplierParts sp ON p.part_id = sp.part_id
JOIN supplier s ON sp.supplier_id = s.supplier_id
JOIN WarehouseParts wp ON p.part_id = wp.part_id
JOIN Warehouse w ON wp.warehouse_id = w.warehouse_id;
```

* **צילום הרצה:**
  ![](images/select1_run.png)

* **צילום תוצאה (5 שורות):**
  ![](images/select1_result.png)

#### 2. לקוחות שנרשמו בשנת 2024

**תיאור:** מחזירה את כל הלקוחות שנרשמו למערכת בשנת 2024.

```sql
SELECT costumer_id, phone, email, registration_date
FROM Costumer
WHERE EXTRACT(YEAR FROM registration_date) = 2024;
```

* **צילום הרצה:**
  ![](images/select2_run.png)

* **צילום תוצאה:**
  ![](images/select2_result.png)

(וכך הלאה עבור 6 השאילתות הבאות…)

---

### שאילתות DELETE

#### 1. מחיקת הזמנות לפני 2020

**תיאור:** מוחקת מהטבלה כל הזמנה שהוזנה לפני ה־1 בינואר 2020.

```sql
DELETE FROM myorder WHERE order_date < '2020-01-01';
```

* **צילום בסיס הנתונים לפני:**
  ![](images/delete1_before.png)

* **צילום הרצה:**
  ![](images/delete1_run.png)

* **צילום בסיס הנתונים אחרי:**
  ![](images/delete1_after.png)

(וכן לשתי השאילתות הנוספות)

---

### שאילתות UPDATE

#### 1. עדכון מחיר חלק מסוים אצל ספק מסוים

**תיאור:** מעלה ב־10% את המחיר של חלק מסוים אצל ספק מסוים.

```sql
UPDATE SupplierParts
SET price = price * 1.10
WHERE part_id = 1 AND supplier_id = 1;
```

* **צילום לפני העדכון:**
  ![](images/update1_before.png)

* **צילום הרצה:**
  ![](images/update1_run.png)

* **צילום אחרי העדכון:**
  ![](images/update1_after.png)

(וכן לשני העדכונים הנוספים)

---

### אילוצים (Constraints)

#### 1. CHECK על טבלת עובדים

**תיאור:** מוודא ששנת ההתחלה של העובד לא בעתיד.

```sql
ALTER TABLE employee
ADD CONSTRAINT chk_start_date CHECK (start_date <= CURRENT_DATE);
```

* **ניסיון הכנסת תאריך עתידי:**

  ```sql
  INSERT INTO employee (employee_id, name, role, start_date)
  VALUES (999, 'שגיאה', 'בדיקה', '2099-01-01');
  ```

* **צילום שגיאת הרצה:**
  ![](images/constraint1_error.png)

(וכן לשני האילוצים הנוספים)

---

### Rollback ו־Commit

#### דוגמה עם ROLLBACK

**תיאור:** עדכון זמני בקיבולת מחסן וביטולו.

```sql
BEGIN;
UPDATE Warehouse SET capacity = capacity + 1000 WHERE warehouse_id = 1;
SELECT * FROM Warehouse WHERE warehouse_id = 1;
ROLLBACK;
SELECT * FROM Warehouse WHERE warehouse_id = 1;
```

* **לפני העדכון:**
  ![](images/rollback_before.png)

* **אחרי עדכון (לפני rollback):**
  ![](images/rollback_mid.png)

* **אחרי rollback:**
  ![](images/rollback_after.png)

#### דוגמה עם COMMIT

**תיאור:** עדכון קיבולת למחסן ושמירה קבועה של העדכון.

```sql
BEGIN;
UPDATE Warehouse SET capacity = capacity + 300 WHERE warehouse_id = 2;
COMMIT;
```

* **לפני העדכון:**
  ![](images/commit_before.png)

* **אחרי commit:**
  ![](images/commit_after.png)

---

אם תרצה שאכין עבורך שלד עם קישורי תמונות מדויקים (או אפילו דף README.md מלא עם פקודות `git add` וכו') – אשמח להכין.

