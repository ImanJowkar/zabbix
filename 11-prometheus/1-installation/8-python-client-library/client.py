# Read Data from prometheus
from prometheus_api_client import PrometheusConnect

prom = PrometheusConnect(url='http://<prom-server-ip>:9090/', disable_ssl=True)
print(prom)
#print(prom.all_metrics())


counters = [pa for pa in prom.all_metrics() if 'sin' in pa]
print(counters)

print(prom.custom_query('sin_function'))