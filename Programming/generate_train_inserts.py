from datetime import datetime, timedelta
import random

models = ['Model A', 'Model B', 'Model C']
with open("insert_train.sql", "w") as f:
    for i in range(1, 401):
        model = random.choice(models)
        year = random.randint(2010, 2022)
        last_check = datetime(2023, random.randint(1, 12), random.randint(1, 28))
        next_check = last_check + timedelta(days=365)
        f.write(f"INSERT INTO Train VALUES ({i}, '{model}', {year}, TO_DATE('{last_check.date()}', 'YYYY-MM-DD'), TO_DATE('{next_check.date()}', 'YYYY-MM-DD'));")
