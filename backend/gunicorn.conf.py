import os

# ── Binding ────────────────────────────────────────────────────────────────
bind = f"0.0.0.0:{os.environ.get('FLASK_PORT', '5001')}"

# ── Workers ────────────────────────────────────────────────────────────────
# TaskManager uses an in-memory singleton — must stay at 1 worker process.
# Use gthread (OS threads) for concurrency, the same model as Flask threaded=True.
workers = 1
worker_class = "gthread"
threads = int(os.environ.get("GUNICORN_THREADS", "8"))

# ── Timeouts ───────────────────────────────────────────────────────────────
# LLM graph-build and simulation runs can take several minutes.
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "600"))
graceful_timeout = 30
keepalive = 5

# ── Logging ────────────────────────────────────────────────────────────────
accesslog = "-"   # stdout
errorlog = "-"    # stderr
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(D)sµs'

# ── Reliability ────────────────────────────────────────────────────────────
reload = False
preload_app = False   # keep False so background threads start cleanly per worker
