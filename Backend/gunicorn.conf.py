# ==============================================================================
# Gunicorn Production Configuration (Render / Memory Constrained CPU Host)
# ==============================================================================
import os

# Limit workers strictly to 1 to ensure only ONE instance of the AI model / PyTorch
# is ever resident in RAM (prevents OOM on 512MB free/starter tier).
workers = 1

# Use 2 lightweight threads for handling concurrent I/O requests without spawning processes
threads = 2

# Generous timeout for CPU-based deep learning inference on initial cold starts
timeout = 120

# Graceful worker restart timeout
graceful_timeout = 30

# Keep-alive connections
keepalive = 5

# Max requests before worker recycling to prevent any gradual memory leaks
max_requests = 1000
max_requests_jitter = 50

# Log level
loglevel = "info"
