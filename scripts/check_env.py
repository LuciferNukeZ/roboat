#!/usr/bin/env python3
"""
scripts/check_env.py
~~~~~~~~~~~~~~~~~~~~
Verify your roboat environment is set up correctly.
Run: python scripts/check_env.py
"""

import sys
import importlib

REQUIRED_PYTHON = (3, 8)
CHECKS = []


def check(label):
    def decorator(fn):
        CHECKS.append((label, fn))
        return fn
    return decorator


def ok(msg):   print(f"  \033[92m✔\033[0m  {msg}")
def fail(msg): print(f"  \033[91m✖\033[0m  {msg}")
def warn(msg): print(f"  \033[93m⚠\033[0m  {msg}")


@check("Python version")
def check_python():
    if sys.version_info >= REQUIRED_PYTHON:
        ok(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True
    fail(f"Python {sys.version_info.major}.{sys.version_info.minor} — need 3.8+")
    return False


@check("roboat installed")
def check_roboat():
    try:
        import roboat
        ok(f"roboat {roboat.__version__}")
        return True
    except ImportError:
        fail("roboat not found — run: pip install -e .")
        return False


@check("requests installed")
def check_requests():
    try:
        import requests
        ok(f"requests {requests.__version__}")
        return True
    except ImportError:
        fail("requests not found — run: pip install requests")
        return False


@check("aiohttp installed (optional)")
def check_aiohttp():
    try:
        import aiohttp
        ok(f"aiohttp {aiohttp.__version__}")
        return True
    except ImportError:
        warn("aiohttp not installed — async client unavailable")
        warn("Install with: pip install 'roboat[async]'")
        return True  # optional — not a failure


@check("sqlite3 available")
def check_sqlite():
    try:
        import sqlite3
        ok(f"sqlite3 {sqlite3.sqlite_version}")
        return True
    except ImportError:
        fail("sqlite3 not available — database layer will not work")
        return False


@check("roboat imports cleanly")
def check_imports():
    try:
        from roboat import (
            RoboatClient, ClientBuilder, RoboatSession,
            SessionDatabase, EventPoller, OAuthManager,
        )
        ok("All core imports successful")
        return True
    except Exception as e:
        fail(f"Import error: {e}")
        return False


@check("roboat client instantiates")
def check_client():
    try:
        from roboat import RoboatClient
        client = RoboatClient()
        assert not client.is_authenticated
        ok(f"RoboatClient instantiated — {client!r}")
        return True
    except Exception as e:
        fail(f"Client error: {e}")
        return False


@check("Database layer works")
def check_database():
    try:
        import tempfile, os
        from roboat import SessionDatabase
        with tempfile.TemporaryDirectory() as d:
            db = SessionDatabase.create("test_check", directory=d)
            db.set("ping", "pong")
            assert db.get("ping") == "pong"
            db.close()
        ok("Database read/write works")
        return True
    except Exception as e:
        fail(f"Database error: {e}")
        return False


def main():
    print()
    print("  roboat — Environment Check")
    print("  " + "─" * 40)
    print()

    passed = 0
    failed = 0

    for label, fn in CHECKS:
        print(f"  {label}")
        try:
            result = fn()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            fail(f"Unexpected error: {e}")
            failed += 1
        print()

    print("  " + "─" * 40)
    color = "\033[92m" if failed == 0 else "\033[91m"
    print(f"  {color}{passed} passed, {failed} failed\033[0m")
    print()

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
