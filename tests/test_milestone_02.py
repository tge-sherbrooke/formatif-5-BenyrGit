"""
Milestone 2: MQTT Publishing (35 points)
========================================

This milestone verifies that the student has:
1. Created MQTT client
2. Implemented publish function
3. Used correct feed/topic format
4. Published to multiple feeds

Tests use code analysis and mocking for GitHub Actions.
"""

import os
import ast
import re
from pathlib import Path

import pytest
from unittest.mock import patch, MagicMock


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
# Test 2.1: MQTTClient Creation (10 points)
# ---------------------------------------------------------------------------
def test_mqtt_client_creation():
    """
    Verify that an MQTT client is created.

    Expected: MQTTClient() instantiation

    Suggestion: Create the MQTT client:
        from Adafruit_IO import MQTTClient
        client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text()

    has_client_creation = any([
        "MQTTClient(" in content,
        "mqtt_client" in content.lower(),
        "client = " in content.lower() and "mqtt" in content.lower(),
    ])

    if not has_client_creation:
        pytest.fail(
            f"\n\n"
            f"Expected: MQTT client creation\n"
            f"Actual: No MQTTClient instantiation found\n\n"
            f"Suggestion: Create the MQTT client:\n"
            f"  from Adafruit_IO import MQTTClient\n"
            f"  client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)\n"
        )


# ---------------------------------------------------------------------------
# Test 2.2: Publish Function (10 points)
# ---------------------------------------------------------------------------
def test_publish_function():
    """
    Verify that a publish function exists.

    Expected: def publish_... or client.publish() usage

    Suggestion: Create a publish function or use client.publish():
        def publish_sensor_data(client, temperature, humidity):
            client.publish('temperature', temperature)
            client.publish('humidity', humidity)
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text()

    has_publish = any([
        ".publish(" in content,
        "def publish" in content.lower(),
    ])

    if not has_publish:
        pytest.fail(
            f"\n\n"
            f"Expected: Publish functionality\n"
            f"Actual: No publish function or client.publish() found\n\n"
            f"Suggestion: Implement publishing:\n"
            f"  def publish_sensor_data(client, temp, humidity):\n"
            f"      client.publish('temperature', temp)\n"
            f"      client.publish('humidity', humidity)\n"
        )


# ---------------------------------------------------------------------------
# Test 2.3: Multiple Feeds (8 points)
# ---------------------------------------------------------------------------
def test_multiple_feeds():
    """
    Verify that the script publishes to multiple feeds.

    Expected: At least 2 different feed names (temperature, humidity, etc.)

    Suggestion: Publish each sensor value to its own feed:
        client.publish('temperature', temp)
        client.publish('humidity', humidity)
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text().lower()

    feed_indicators = [
        "temperature" in content,
        "humidity" in content or "humidite" in content,
    ]

    feed_count = sum(feed_indicators)

    if feed_count < 2:
        pytest.fail(
            f"\n\n"
            f"Expected: Multiple feed references (at least 2)\n"
            f"Actual: Found {feed_count} feed types\n\n"
            f"Suggestion: Publish to multiple feeds:\n"
            f"  # One feed per sensor value (Adafruit IO best practice)\n"
            f"  client.publish('temperature', temp)\n"
            f"  client.publish('humidity', humidity)\n"
        )


# ---------------------------------------------------------------------------
# Test 2.4: Feed Key Format (7 points)
# ---------------------------------------------------------------------------
def test_feed_key_format():
    """
    Verify that feed keys use lowercase format.

    Expected: Feed names like 'temperature', not 'Temperature'

    WHY THIS MATTERS:
    Adafruit IO feed KEYS are always lowercase with no spaces.
    The feed NAME can be "Temperature Sensor" but the KEY is "temperature-sensor".
    Using the wrong format causes 404 errors.

    Suggestion: Use lowercase feed keys:
        client.publish('temperature', value)  # GOOD
        client.publish('Temperature', value)  # BAD - 404 error!
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text()

    # Look for publish calls with feed names
    publish_calls = re.findall(r'\.publish\s*\(\s*[\'"]([^\'"]+)[\'"]', content)

    if not publish_calls:
        pytest.skip("No publish calls found to check format")

    # Check if any feed names have uppercase letters
    bad_feeds = [feed for feed in publish_calls if feed != feed.lower()]

    if bad_feeds:
        pytest.fail(
            f"\n\n"
            f"Expected: Lowercase feed keys\n"
            f"Actual: Found uppercase in feeds: {bad_feeds}\n\n"
            f"WHY THIS MATTERS:\n"
            f"  Adafruit IO feed KEYS are always lowercase.\n"
            f"  Using 'Temperature' instead of 'temperature' causes 404 errors!\n\n"
            f"Suggestion: Use lowercase feed keys:\n"
            f"  client.publish('temperature', value)  # Correct\n"
            f"  client.publish('Temperature', value)  # Wrong!\n"
        )
