import os
import mysql.connector
import random
import time
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Predefined data
product_names = ["Smartphone", "Laptop", "Headphones", "T-shirt", "Coffee Maker"]
unit_prices = [699.99, 999.99, 199.99, 19.99, 49.99]

# Function to create a database and the Orders table
def create_database_and_table(cursor):
    cursor.execute("CREATE DATABASE IF NOT EXISTS OrdersDB")
    cursor.execute("USE OrdersDB")

    # Create Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(100),
            quantity INT,
            unit_price DECIMAL(10, 2),
            total_price DECIMAL(10, 2),
            order_date DATETIME
        )
    ''')

# Function to insert a random order into the table
def insert_random_order(cursor):
    product_name = random.choice(product_names)
    unit_price = random.choice(unit_prices)
    quantity = random.randint(1, 5)  # Random quantity between 1 and 5
    total_price = unit_price * quantity
    order_date = datetime.now()  # Current order date

    cursor.execute('''
        INSERT INTO Orders (product_name, quantity, unit_price, total_price, order_date)
        VALUES (%s, %s, %s, %s, %s)
    ''', (product_name, quantity, unit_price, total_price, order_date))

# Main function
def main():
    try:
        # Read database credentials from environment variables
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')  # Get the database port
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')

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