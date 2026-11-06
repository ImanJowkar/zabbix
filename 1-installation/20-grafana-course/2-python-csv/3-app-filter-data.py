import csv, os, random, time, threading
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

FILE = "sales.csv"
CITIES = ["Tehran", "Shiraz", "Tabriz"]
PRICES = {"Book": 10, "Pen": 2, "Bag": 25}
HEADER = ["time", "city", "product", "quantity", "price"]
lock = threading.Lock()

# ---------- part 1: generate one order every 2 seconds ----------
def generate():
    if not os.path.exists(FILE):
        with open(FILE, "w", newline="") as f:
            csv.writer(f).writerow(HEADER)
    while True:
        product = random.choice(list(PRICES))
        row = [
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            random.choice(CITIES),
            product,
            random.randint(1, 5),
            PRICES[product],
        ]
        with lock, open(FILE, "a", newline="") as f:
            csv.writer(f).writerow(row)
        time.sleep(2)

# ---------- part 2: serve only rows inside Grafana time range ----------
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path != "/sales.csv":
            self.send_error(404)
            return
        q = parse_qs(url.query)
        start = int(q.get("from", ["0"])[0])           # milliseconds
        end = int(q.get("to", [str(10**15)])[0])       # milliseconds

        with lock, open(FILE, newline="") as f:
            rows = list(csv.reader(f))[1:]

        out = [",".join(HEADER)]
        for r in rows:
            ms = datetime.fromisoformat(r[0]).timestamp() * 1000
            if start <= ms <= end:
                out.append(",".join(r))

        body = ("\n".join(out) + "\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/csv")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

threading.Thread(target=generate, daemon=True).start()
print("Serving on http://0.0.0.0:8000/sales.csv")
ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()