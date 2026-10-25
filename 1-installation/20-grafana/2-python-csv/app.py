import csv
import random
import time
import os
from datetime import datetime, timezone

CSV_FILE = "sales.csv"

locations = [
    ("Germany", "Berlin", "Europe", 52.5200, 13.4050),
    ("France", "Paris", "Europe", 48.8566, 2.3522),
    ("United Kingdom", "London", "Europe", 51.5074, -0.1278),
    ("United States", "New York", "North America", 40.7128, -74.0060),
    ("Canada", "Toronto", "North America", 43.6532, -79.3832),
    ("Brazil", "Sao Paulo", "South America", -23.5505, -46.6333),
    ("UAE", "Dubai", "Middle East", 25.2048, 55.2708),
    ("Iran", "Tehran", "Middle East", 35.6892, 51.3890),
    ("Japan", "Tokyo", "Asia", 35.6762, 139.6503),
    ("India", "Mumbai", "Asia", 19.0760, 72.8777),
    ("Australia", "Sydney", "Oceania", -33.8688, 151.2093),
    ("South Africa", "Cape Town", "Africa", -33.9249, 18.4241),
]

products = {
    "Electronics": [
        ("Laptop", 1200),
        ("Smartphone", 800),
        ("Headphones", 150),
    ],
    "Fashion": [
        ("Shoes", 120),
        ("T-Shirt", 40),
        ("Jacket", 180),
    ],
    "Home": [
        ("Coffee Maker", 90),
        ("Chair", 160),
        ("Lamp", 60),
    ],
    "Sports": [
        ("Running Shoes", 140),
        ("Fitness Watch", 250),
        ("Yoga Mat", 50),
    ],
}

channels = ["Website", "Mobile App", "Marketplace"]
statuses = ["Completed", "Completed", "Completed", "Pending", "Cancelled"]
payments = ["Credit Card", "PayPal", "Bank Transfer", "Crypto"]
customer_types = ["New", "Returning"]

fields = [
    "timestamp",
    "order_id",
    "country",
    "city",
    "latitude",
    "longitude",
    "region",
    "category",
    "product",
    "sales_channel",
    "quantity",
    "unit_price",
    "discount_percent",
    "revenue",
    "cost",
    "profit",
    "order_status",
    "payment_method",
    "customer_type",
]


def create_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()


def generate_sale():
    country, city, region, lat, lon = random.choice(locations)

    category = random.choice(list(products.keys()))
    product, base_price = random.choice(products[category])

    quantity = random.randint(1, 5)

    unit_price = round(
        base_price * random.uniform(0.90, 1.10),
        2
    )

    discount = random.choice([0, 0, 0, 5, 10, 15, 20])

    gross = quantity * unit_price
    revenue = gross * (1 - discount / 100)

    cost_ratio = random.uniform(0.55, 0.80)
    cost = revenue * cost_ratio
    profit = revenue - cost

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "order_id": random.randint(100000, 999999),
        "country": country,
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "region": region,
        "category": category,
        "product": product,
        "sales_channel": random.choice(channels),
        "quantity": quantity,
        "unit_price": round(unit_price, 2),
        "discount_percent": discount,
        "revenue": round(revenue, 2),
        "cost": round(cost, 2),
        "profit": round(profit, 2),
        "order_status": random.choice(statuses),
        "payment_method": random.choice(payments),
        "customer_type": random.choice(customer_types),
    }


def main():
    create_csv()

    print(f"Generating sales data -> {CSV_FILE}")

    while True:

        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)

            for _ in range(5):
                sale = generate_sale()
                writer.writerow(sale)

                print(
                    sale["timestamp"],
                    sale["country"],
                    sale["product"],
                    sale["revenue"]
                )

        time.sleep(2)


if __name__ == "__main__":
    main()