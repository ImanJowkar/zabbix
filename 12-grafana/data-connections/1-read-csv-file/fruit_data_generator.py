import csv
import random
import time
import os

fruits = ["Apple", "Banana", "Orange", "Grapes", "Pineapple"]
data_dir = "/app/data"
os.makedirs(data_dir, exist_ok=True)
file_name = os.path.join(data_dir, "fruit_data.csv")

fruit_data = {fruit: random.randint(1, 100) for fruit in fruits}

def write_to_csv(file_name, fruit_data):
    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Fruit", "Count"])
        for fruit, count in fruit_data.items():
            writer.writerow([fruit, count])

write_to_csv(file_name, fruit_data)

while True:
    for fruit in fruit_data:
        fruit_data[fruit] = max(0, fruit_data[fruit] + random.randint(-10, 10))

    write_to_csv(file_name, fruit_data)
    print(f"Updated fruit counts written to {file_name}: {fruit_data}")

    time.sleep(10)