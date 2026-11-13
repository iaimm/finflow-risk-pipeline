import os


os.environ.setdefault(
    "FINFLOW_JWT_SECRET_KEY",
    "test-only-secret-key-with-at-least-32-characters",
)
os.environ.setdefault(
    "FINFLOW_DEMO_ADMIN_PASSWORD",
    "admin-test-password",
)
os.environ.setdefault(
    "FINFLOW_DEMO_VIEWER_PASSWORD",
    "viewer-test-password",
)
os.environ.setdefault(
    "FINFLOW_ACCESS_TOKEN_EXPIRE_MINUTES",
    "30",
)