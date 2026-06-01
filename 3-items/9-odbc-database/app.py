import os
import mysql.connector
import random
import time
from datetime import datetime, timedelta


# Predefined data
product_names = ["Smartphone", "Laptop", "Headphones", "T-shirt", "Coffee Maker"]
unit_prices = [699.99, 999.99, 199.99, 19.99, 49.99]
shop = ['aliexpress', 'amazon', 'digikala', 'alibaba']

# Function to create a database and the Orders table
def create_database_and_table(cursor):
    cursor.execute("CREATE DATABASE IF NOT EXISTS OrdersDB")
    cursor.execute("USE OrdersDB")

    # Create Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(100),
            shop_name VARCHAR(100),
            quantity INT,
            unit_price DECIMAL(10, 2),
            total_price DECIMAL(10, 2),
            order_date DATETIME
        )
    ''')

# Function to insert a random order into the table
def insert_random_order(cursor):
    product_name = random.choice(product_names)
    shop_name = random.choice(shop)
    unit_price = random.choice(unit_prices)
    quantity = random.randint(1, 5)  # Random quantity between 1 and 5
    total_price = unit_price * quantity
    order_date = datetime.now()  # Current order date

    cursor.execute('''
        INSERT INTO Orders (product_name, shop_name, quantity, unit_price, total_price, order_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (product_name, shop_name, quantity, unit_price, total_price, order_date))

# Main function
def main():
    try:
        # Read database credentials from environment variables
        db_host = "192.168.85.140"
        db_port = 3306  # Get the database port
        db_user = "iman"
        db_password = "iman"

        # Connect to the MariaDB server
        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()

        # Create database and table
        create_database_and_table(cursor)

        print("Starting to insert orders...")

        # Infinite loop to insert orders one by one
        while True:
            insert_random_order(cursor)
            conn.commit()  # Commit the transaction
            print("Inserted an order at", datetime.now())
            time.sleep(2)  # Wait for 2 seconds before inserting the next order

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except KeyboardInterrupt:
        print("Stopping data insertion.")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()