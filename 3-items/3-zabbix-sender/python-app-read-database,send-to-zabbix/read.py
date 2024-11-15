import os
import mysql.connector
import time
import socket
import json
from zabbix_utils import Sender
from zabbix_utils import ItemValue, Sender


def get_order_statistics():
    try:
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='OrdersDB'  # Specify the database
        )
        cursor = conn.cursor()

        # Query to get the total count of orders grouped by product name
        cursor.execute("""
            SELECT product_name, COUNT(*) as order_count
            FROM Orders
            GROUP BY product_name
        """)

        # Fetch the results and format them as a dictionary
        results = cursor.fetchall()
        order_stats = {product_name: order_count for product_name, order_count in results}

        return order_stats


    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

res = get_order_statistics()
res = json.dumps(res)


items = [
    ItemValue('Zabbix server', 'db.read', res)
    ]
print(res)
sender = Sender('127.0.0.1', 10051)
response = sender.send(items)
print(response)