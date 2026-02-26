"""
Milestone 1: Environment Setup (25 points)
==========================================

This milestone verifies that the student has:
1. Created a valid mqtt_publisher.py script
2. Imported Adafruit IO MQTT library
3. Configured credentials safely (no hardcoded keys!)

These tests analyze code structure.
SECURITY: We verify no API keys are committed.
"""

import os
import ast
import re
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helper: Get repository root
# ---------------------------------------------------------------------------
def get_repo_root():
    """Find the repository root by looking for .github folder."""
    current = Path(__file__).parent.parent
    if (current / ".github").exists():
        return current
    return current


REPO_ROOT = get_repo_root()


# ---------------------------------------------------------------------------
# Test 1.1: Script Exists (5 points)
# ---------------------------------------------------------------------------
def test_mqtt_script_exists():
    """
    Verify that mqtt_publisher.py exists in the repository.

    Expected: mqtt_publisher.py file present

    Suggestion: Create mqtt_publisher.py with your MQTT publishing code.
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    assert script_path.exists(), (
        f"\n\n"
        f"Expected: mqtt_publisher.py file in repository root\n"
        f"Actual: File not found at {script_path}\n\n"
        f"Suggestion: Create mqtt_publisher.py with your Adafruit IO code.\n"
    )


# ---------------------------------------------------------------------------
# Test 1.2: Script Has Valid Python Syntax (5 points)
# ---------------------------------------------------------------------------
def test_mqtt_script_syntax():
    """
    Verify that mqtt_publisher.py has valid Python syntax.

    Expected: Python code that compiles without SyntaxError

    Suggestion: Run 'python3 -m py_compile mqtt_publisher.py' locally.
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text()

    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(
            f"\n\n"
            f"Expected: Valid Python syntax\n"
            f"Actual: SyntaxError on line {e.lineno}: {e.msg}\n\n"
            f"Suggestion: Check line {e.lineno} for syntax errors.\n"
        )


# ---------------------------------------------------------------------------
# Test 1.3: Adafruit IO Import (5 points)
# ---------------------------------------------------------------------------
def test_adafruit_io_import():
    """
    Verify that mqtt_publisher.py imports Adafruit IO.

    Expected: 'from Adafruit_IO import MQTTClient' or similar

    Suggestion: Add this import at the top of your script:
        from Adafruit_IO import MQTTClient
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text()

    has_adafruit_io = any([
        "Adafruit_IO" in content,
        "adafruit_io" in content,
        "MQTTClient" in content,
    ])

    if not has_adafruit_io:
        pytest.fail(
            f"\n\n"
            f"Expected: Adafruit IO import\n"
            f"Actual: No Adafruit IO import found\n\n"
            f"Suggestion: Add Adafruit IO import:\n"
            f"  from Adafruit_IO import MQTTClient\n"
            f"\n"
            f"Install with: pip install adafruit-io\n"
        )


# ---------------------------------------------------------------------------
# Test 1.4: Credentials Configuration (5 points)
# ---------------------------------------------------------------------------
def test_credentials_config():
    """
    Verify that credentials are configured (variables exist).

    Expected: ADAFRUIT_IO_USERNAME and ADAFRUIT_IO_KEY variables

    Suggestion: Define credential variables (but use env vars or config file):
        ADAFRUIT_IO_USERNAME = os.environ.get('ADAFRUIT_IO_USERNAME')
        ADAFRUIT_IO_KEY = os.environ.get('ADAFRUIT_IO_KEY')
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text()

    has_username_var = any([
        "ADAFRUIT_IO_USERNAME" in content,
        "AIO_USERNAME" in content,
        "username" in content.lower() and ("adafruit" in content.lower() or "aio" in content.lower()),
    ])

    has_key_var = any([
        "ADAFRUIT_IO_KEY" in content,
        "AIO_KEY" in content,
        "key" in content.lower() and ("adafruit" in content.lower() or "aio" in content.lower()),
    ])

    if not (has_username_var and has_key_var):
        pytest.fail(
            f"\n\n"
            f"Expected: Credential variables (username and key)\n"
            f"Actual: Missing username={has_username_var}, key={has_key_var}\n\n"
            f"Suggestion: Define credential variables:\n"
            f"  import os\n"
            f"  ADAFRUIT_IO_USERNAME = os.environ.get('ADAFRUIT_IO_USERNAME')\n"
            f"  ADAFRUIT_IO_KEY = os.environ.get('ADAFRUIT_IO_KEY')\n"
            f"\n"
            f"Never hardcode API keys directly in your code!\n"
        )


# ---------------------------------------------------------------------------
# Test 1.5: SECURITY - No Hardcoded API Keys (5 points)
# ---------------------------------------------------------------------------
def test_no_hardcoded_api_keys():
    """
    SECURITY: Verify that no API keys are hardcoded in the code.

    Expected: No 'aio_xxxxx' patterns in code

    WHY THIS MATTERS:
    Hardcoded API keys in public repos are a security risk.
    Anyone can use your key and exhaust your quota or access your data.

    Suggestion: Use environment variables or a config file:
        import os
        ADAFRUIT_IO_KEY = os.environ.get('ADAFRUIT_IO_KEY')
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text()

    # Adafruit IO keys start with "aio_" followed by alphanumeric characters
    has_hardcoded_key = re.search(r'["\']aio_[a-zA-Z0-9]{20,}["\']', content)

    if has_hardcoded_key:
        pytest.fail(
            f"\n\n"
            f"SECURITY WARNING: Hardcoded API key detected!\n\n"
            f"Expected: No API keys in source code\n"
            f"Actual: Found pattern matching Adafruit IO key\n\n"
            f"WHY THIS MATTERS:\n"
            f"  - Public repos expose your key to everyone\n"
            f"  - Anyone can use your quota\n"
            f"  - Keys can be revoked, breaking your code\n\n"
            f"Suggestion: Use environment variables:\n"
            f"  import os\n"
            f"  ADAFRUIT_IO_KEY = os.environ.get('ADAFRUIT_IO_KEY')\n"
            f"\n"
            f"Then set the env var before running:\n"
            f"  export ADAFRUIT_IO_KEY='your_key_here'\n"
        )
