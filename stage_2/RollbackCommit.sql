-- דוגמה 1: הדגמת ROLLBACK

-- התחלת טרנזקציה
START TRANSACTION;

-- הצגת המצב הנוכחי
SELECT * FROM Part WHERE part_id IN (1, 2, 3);

-- ביצוע עדכון
UPDATE Part 
SET name = CONCAT(name, ' - UPDATED'), 
    last_update = CURDATE()
WHERE part_id IN (1, 2, 3);

-- הצגת המצב אחרי העדכון
SELECT * FROM Part WHERE part_id IN (1, 2, 3);

-- ביטול השינויים
ROLLBACK;

-- הצגת המצב אחרי ROLLBACK - השינויים בוטלו
SELECT * FROM Part WHERE part_id IN (1, 2, 3);

-- דוגמה 2: הדגמת COMMIT

-- התחלת טרנזקציה חדשה
START TRANSACTION;

-- הצגת המצב הנוכחי
SELECT * FROM employee WHERE employee_id IN (1, 2, 3);

-- ביצוע עדכון
UPDATE employee 
SET last_training = CURDATE()
WHERE employee_id IN (1, 2, 3);

-- הצגת המצב אחרי העדכון
SELECT * FROM employee WHERE employee_id IN (1, 2, 3);

-- שמירת השינויים
COMMIT;

-- הצגת המצב אחרי COMMIT - השינויים נשמרו
SELECT * FROM employee WHERE employee_id IN (1, 2, 3);