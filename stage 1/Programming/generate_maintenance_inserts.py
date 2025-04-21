from datetime import datetime, timedelta
import random

with open("insert_maintenance.sql", "w") as f:
    for i in range(1, 401):
        train_id = random.randint(1, 400)
        station_id = random.randint(1, 400)
        date = datetime(2024, random.randint(1, 12), random.randint(1, 28))
        description = f'Maintenance #{i}'
        f.write(f"INSERT INTO Maintenance VALUES ({i}, {train_id}, {station_id}, TO_DATE('{date.date()}', 'YYYY-MM-DD'), '{description}');\n")
