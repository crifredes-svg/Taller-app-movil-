import os


os.environ.setdefault("DB_HOST", "127.0.0.1")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("JWT_SECRET", "test-secret-key-with-at-least-32-bytes")