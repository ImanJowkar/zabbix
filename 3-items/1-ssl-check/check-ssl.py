import socket
import ssl
from datetime import datetime
import sys

def check_ssl_expiration(domain, port=443, verify_ssl=True):

    context = ssl.create_default_context()

    if not verify_ssl:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    try:

        with socket.create_connection((domain, port)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()


        if 'notAfter' not in cert:
            raise ValueError("Certificate does not contain an expiration date ('notAfter')")


        expires = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
        remaining_days = (expires - datetime.utcnow()).days

        return expires, remaining_days

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python check_ssl_expiration.py <domain_or_ip> [<port>] [--ignore-self-signed]")
        sys.exit(1)


    domain = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 443  
    verify_ssl = "--ignore-self-signed" not in sys.argv 


    try:
        expiration_date, days_left = check_ssl_expiration(domain, port, verify_ssl)
        print(days_left)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
