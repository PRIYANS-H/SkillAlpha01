import os
import shutil
import tempfile

# Settings are read at import time, so the test environment must be in place
# before any `app` module is imported. Environment variables take precedence
# over .env files, which keeps tests off any real database and external APIs.
_TEST_DIR = tempfile.mkdtemp(prefix="skillalpha_tests_")
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_TEST_DIR, 'test.db')}"
os.environ["SUPABASE_JWT_SECRET"] = "test-only-supabase-jwt-secret-0123456789abcdef"
for _key in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY",
             "GROQ_API_KEY", "LLM_API_KEY", "YOUTUBE_DATA_API_KEY"):
    os.environ[_key] = ""


def pytest_sessionfinish(session, exitstatus):
    from app.models.db import engine
    engine.dispose()
    shutil.rmtree(_TEST_DIR, ignore_errors=True)
