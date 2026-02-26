# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-io"]
# ///
"""
Local Hardware Validation for Formatif F5
==========================================

Run this script ON YOUR RASPBERRY PI to validate MQTT setup.
It creates marker files that GitHub Actions will verify.

Usage:
    python3 validate_pi.py

The script will:
1. Verify adafruit-io is installed
2. Check mqtt_publisher.py script
3. Optionally test MQTT connection (if credentials available)
4. Create marker files for GitHub Actions

After running successfully, commit and push the .test_markers/ folder.

NOTE: Do NOT commit your API keys! Use environment variables.
"""

import os
import sys
from pathlib import Path
from datetime import datetime


# ---------------------------------------------------------------------------
# Terminal Colors
# ---------------------------------------------------------------------------
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def success(msg):
    print(f"{Colors.GREEN}[PASS] {msg}{Colors.END}")


def fail(msg):
    print(f"{Colors.RED}[FAIL] {msg}{Colors.END}")


def warn(msg):
    print(f"{Colors.YELLOW}[WARN] {msg}{Colors.END}")


def info(msg):
    print(f"{Colors.BLUE}[INFO] {msg}{Colors.END}")


def header(msg):
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f" {msg}")
    print(f"{'='*60}{Colors.END}\n")


# ---------------------------------------------------------------------------
# Marker Management
# ---------------------------------------------------------------------------
MARKERS_DIR = Path(__file__).parent / ".test_markers"


def create_marker(name, content):
    """Create a marker file for GitHub Actions verification."""
    MARKERS_DIR.mkdir(exist_ok=True)
    marker_path = MARKERS_DIR / f"{name}.txt"
    timestamp = datetime.now().isoformat()
    marker_path.write_text(f"Verified: {timestamp}\n{content}\n")
    info(f"Marker created: {marker_path.name}")


# ---------------------------------------------------------------------------
# Test: Adafruit IO Installation
# ---------------------------------------------------------------------------
def check_adafruit_io():
    """Verify adafruit-io is installed."""
    header("ADAFRUIT IO VERIFICATION")

    try:
        from Adafruit_IO import MQTTClient
        success("adafruit-io imported successfully")
        create_marker("adafruit_io_verified", "adafruit-io available")
        return True
    except ImportError as e:
        fail(f"adafruit-io import failed: {e}")
        print("\n  Les dependances sont gerees automatiquement par uv run")
        print("  via les metadonnees PEP 723 du script.")
        return False


# ---------------------------------------------------------------------------
# Test: Script Validation
# ---------------------------------------------------------------------------
def check_mqtt_script():
    """Verify mqtt_publisher.py script."""
    header("SCRIPT VALIDATION")

    script_path = Path(__file__).parent / "mqtt_publisher.py"

    if not script_path.exists():
        fail("mqtt_publisher.py not found")
        print("\n  Create your mqtt_publisher.py script in the same folder.")
        return False

    success("mqtt_publisher.py exists")

    # Check syntax
    try:
        with open(script_path) as f:
            compile(f.read(), script_path, 'exec')
        success("Python syntax is valid")
    except SyntaxError as e:
        fail(f"Syntax error on line {e.lineno}: {e.msg}")
        return False

    # Check required content
    content = script_path.read_text()
    checks = [
        ("Adafruit_IO", "Adafruit IO import"),
        ("MQTTClient", "MQTTClient usage"),
        (".publish(", "publish function"),
    ]

    all_present = True
    for pattern, desc in checks:
        if pattern in content:
            success(f"Found: {desc}")
        else:
            fail(f"Missing: {desc}")
            all_present = False

    # Security check - no hardcoded keys
    import re
    if re.search(r'["\']aio_[a-zA-Z0-9]{20,}["\']', content):
        fail("SECURITY: Hardcoded API key detected!")
        print("\n  Never commit API keys to your repository!")
        print("  Use environment variables instead:")
        print("    export ADAFRUIT_IO_KEY='your_key_here'")
        all_present = False
    else:
        success("No hardcoded API keys found")

    if all_present:
        create_marker("mqtt_script_verified", "Script structure valid")

    return all_present


# ---------------------------------------------------------------------------
# Test: MQTT Connection (Optional)
# ---------------------------------------------------------------------------
def check_mqtt_connection():
    """Test MQTT connection if credentials are available."""
    header("MQTT CONNECTION TEST (Optional)")

    username = os.environ.get('ADAFRUIT_IO_USERNAME')
    key = os.environ.get('ADAFRUIT_IO_KEY')

    if not username or not key:
        warn("ADAFRUIT_IO_USERNAME or ADAFRUIT_IO_KEY not set")
        info("Set environment variables to test connection:")
        print("    export ADAFRUIT_IO_USERNAME='your_username'")
        print("    export ADAFRUIT_IO_KEY='your_key'")
        return True  # Optional, don't fail

    try:
        from Adafruit_IO import MQTTClient

        info(f"Testing connection for user: {username}")

        connected = False

        def on_connect(client):
            nonlocal connected
            connected = True
            success("Connected to Adafruit IO!")

        client = MQTTClient(username, key)
        client.on_connect = on_connect

        try:
            client.connect()

            # Wait briefly for connection
            import time
            start = time.time()
            while not connected and time.time() - start < 5:
                client.loop()
                time.sleep(0.1)

            if connected:
                create_marker("mqtt_connection_verified", f"User: {username}")
                client.disconnect()
                return True
            else:
                warn("Connection timeout - check credentials")
                return True  # Optional

        except Exception as e:
            warn(f"Connection failed: {e}")
            return True  # Optional

    except Exception as e:
        warn(f"MQTT test error: {e}")
        return True  # Optional


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"\n{Colors.BOLD}Formatif F5 - Local MQTT Validation{Colors.END}")
    print(f"{'='*60}\n")

    results = {}

    # Run all checks
    results["Adafruit IO"] = check_adafruit_io()
    results["Script"] = check_mqtt_script()
    results["Connection"] = check_mqtt_connection()

    # Summary
    header("FINAL RESULTS")

    all_required_passed = results["Adafruit IO"] and results["Script"]

    for test, passed in results.items():
        if passed:
            success(f"{test}: OK")
        elif test == "Connection":
            warn(f"{test}: SKIPPED (optional)")
        else:
            fail(f"{test}: FAILED")

    print()

    if all_required_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}")
        print("=" * 60)
        print(" ALL REQUIRED TESTS PASSED!")
        print("=" * 60)
        print(f"{Colors.END}")

        create_marker("all_tests_passed", "All required validations completed")

        print("\nNext steps:")
        print("  git add .test_markers/")
        print("  git commit -m \"feat: validation locale completee\"")
        print("  git push")
        print()
        print(f"{Colors.YELLOW}RAPPEL: Ne committez JAMAIS vos cles API!{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}")
        print("=" * 60)
        print(" SOME TESTS FAILED - Fix issues and run again")
        print("=" * 60)
        print(f"{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
