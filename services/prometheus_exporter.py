from prometheus_client import Counter, Histogram, Gauge, start_http_server
import threading, time

# Prometheus Exporter
class PrometheusMetricsExporter:
    """Export cache metrics to Prometheus"""

    def __init__(self, port=8000):
        self.port = port
        self._server_started = False

        # Define metrics
        self.cache_hits = Counter('cache_hits_total', 'Total cache hits',
                                  ['pattern', 'scenario'])
        self.cache_misses = Counter('cache_misses_total', 'Total cache misses',
                                    ['pattern', 'scenario'])
        self.cache_evictions = Counter('cache_evictions_total', 'Total cache evictions',
                                       ['scenario'])

        self.cache_latency = Histogram('cache_read_latency_seconds', 'Cache read latency',
                                       ['pattern', 'scenario'])
        self.db_latency = Histogram('db_read_latency_seconds', 'Database read latency',
                                    ['pattern', 'scenario'])

        self.hit_rate = Gauge('cache_hit_rate_percent', 'Current cache hit rate',
                              ['pattern', 'scenario'])
        self.memory_usage = Gauge('cache_memory_usage_bytes', 'Cache memory usage',
                                  ['scenario'])

    def start(self):
        """Start Prometheus HTTP server in background thread"""
        if not self._server_started:
            def run_server():
                start_http_server(self.port)

            thread = threading.Thread(target=run_server, daemon=True)
            thread.start()
            self._server_started = True
            print(f"✓ Prometheus metrics server started on http://localhost:{self.port}")
            time.sleep(1)  # Give server time to start

    def record_hit(self, pattern: str, scenario: str, latency_seconds: float):
        self.cache_hits.labels(pattern=pattern, scenario=scenario).inc()
        self.cache_latency.labels(pattern=pattern, scenario=scenario).observe(latency_seconds)

    def record_miss(self, pattern: str, scenario: str,
                    cache_latency_seconds: float,
                    db_latency_seconds: float):
        self.cache_misses.labels(pattern=pattern, scenario=scenario).inc()
        self.cache_latency.labels(pattern=pattern, scenario=scenario).observe(cache_latency_seconds)
        self.db_latency.labels(pattern=pattern, scenario=scenario).observe(db_latency_seconds)

    def record_eviction(self, scenario: str):
        self.cache_evictions.labels(scenario=scenario).inc()

    def update_hit_rate(self, pattern: str, scenario: str, hit_rate: float):
        self.hit_rate.labels(pattern=pattern, scenario=scenario).set(hit_rate)

    def update_memory_usage(self, scenario: str, bytes_used: int):
        self.memory_usage.labels(scenario=scenario).set(bytes_used)

# SINGLETON 
exporter = PrometheusMetricsExporter(port=8000)