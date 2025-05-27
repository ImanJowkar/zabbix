import prometheus_client as prom
import random
import time
import numpy as np
from ping3 import ping



counter1 = prom.Counter('counter1_func', 'the name of counter1')
counter2 = prom.Counter('counter2_func', 'the name of counter2')


gauge1 = prom.Gauge("sin_function", 'this is sin(x) function')
gauge2 = prom.Gauge("ping_delay_google", 'this is the delay ping between us and google.com')

def ping_server(server_ip):
    response_time = ping(server_ip, unit='ms')
    return response_time



prom.start_http_server(8003)
print("app listen on port 8003")
i=0
while True:
    
    counter1.inc(random.randint(0, 100))
    counter2.inc(random.randint(0, 100))
    gauge1.set(10 * np.sin(random.randint(0, 100)))
    gauge2.set(ping_server('google.com'))
    time.sleep(5)
    i+=5
    if i == 100:
        i = 0