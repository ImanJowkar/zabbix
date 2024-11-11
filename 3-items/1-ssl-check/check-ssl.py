import socket
import ssl
from datetime import datetime
import sys

def check_ssl_expiration(domain, port=443):
    context = ssl.create_default_context()
    with socket.create_connection((domain, port)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            cert = ssock.getpeercert()


    expires = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
    remaining_days = (expires - datetime.utcnow()).days

    return expires, remaining_days

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python check_ssl_expiration.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]

    try:
        expiration_date, days_left = check_ssl_expiration(domain)
        print(days_left)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)