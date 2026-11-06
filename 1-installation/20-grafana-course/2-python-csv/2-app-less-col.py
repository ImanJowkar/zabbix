import csv, os, random, time, threading
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

FILE = "sales.csv"
CITIES = ["Tehran", "Shiraz", "Tabriz"]
PRICES = {"Book": 10, "Pen": 2, "Bag": 25}

def generate():
    new_file = not os.path.exists(FILE)
    with open(FILE, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["time", "city", "product", "quantity", "price"])
        while True:
            product = random.choice(list(PRICES))
            w.writerow([
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                random.choice(CITIES),
                product,
                random.randint(1, 5),
                PRICES[product],
            ])
            f.flush()
            time.sleep(2)

threading.Thread(target=generate, daemon=True).start()
print("Serving on http://0.0.0.0:8000/sales.csv")
ThreadingHTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler).serve_forever()