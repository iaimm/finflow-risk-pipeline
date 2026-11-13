import os


# 以下配置只用于本地自动化测试。
os.environ["FINFLOW_JWT_SECRET_KEY"] = (
    "test-only-secret-key-0123456789abcdef-0123456789abcdef"
)
os.environ["FINFLOW_DEMO_ADMIN_PASSWORD"] = (
    "admin-test-password"
)
os.environ["FINFLOW_DEMO_VIEWER_PASSWORD"] = (
    "viewer-test-password"
)
os.environ["FINFLOW_ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

# os.environ.setdefault(
#     "FINFLOW_JWT_SECRET_KEY",
#     "test-only-secret-key-with-at-least-32-characters",
# )
# os.environ.setdefault(
#     "FINFLOW_DEMO_ADMIN_PASSWORD",
#     "admin-test-password",
# )
# os.environ.setdefault(
#     "FINFLOW_DEMO_VIEWER_PASSWORD",
#     "viewer-test-password",
# )
# os.environ.setdefault(
#     "FINFLOW_ACCESS_TOKEN_EXPIRE_MINUTES",
#     "30",
# )