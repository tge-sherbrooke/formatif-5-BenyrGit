"""
Milestone 3: Robust Connection (40 points)
==========================================

This milestone verifies that the student has:
1. Implemented reconnection with exponential backoff
2. Defined delay constants
3. Handled disconnections with buffering
4. Used non-blocking loop

These tests verify code patterns for robust MQTT handling.
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
# Test 3.1: Reconnection Pattern (15 points)
# ---------------------------------------------------------------------------
def test_reconnection_pattern():
    """
    Verify that reconnection logic is implemented.

    Expected: Reconnection handling (try/except with retry)

    WHY THIS MATTERS:
    MQTT connections can drop due to network issues.
    Professional code automatically reconnects.

    Suggestion: Implement reconnection:
        def on_disconnect(client):
            print("Deconnecte - tentative de reconnexion...")
            reconnect_with_backoff(client)
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text()

    has_reconnect = any([
        "reconnect" in content.lower(),
        "on_disconnect" in content,
        "backoff" in content.lower(),
        "retry" in content.lower() and "connect" in content.lower(),
    ])

    if not has_reconnect:
        pytest.fail(
            f"\n\n"
            f"Expected: Reconnection handling\n"
            f"Actual: No reconnection pattern found\n\n"
            f"WHY THIS MATTERS:\n"
            f"  MQTT connections can drop due to network issues.\n"
            f"  Without reconnection, your program stops publishing!\n\n"
            f"Suggestion: Implement reconnection:\n"
            f"  def on_disconnect(client):\n"
            f"      print(\"Deconnecte!\")\n"
            f"      reconnect_with_backoff(client)\n"
            f"\n"
            f"  client.on_disconnect = on_disconnect\n"
        )


# ---------------------------------------------------------------------------
# Test 3.2: Delay Constants (10 points)
# ---------------------------------------------------------------------------
def test_delay_constants():
    """
    Verify that delay constants are defined for backoff.

    Expected: MIN_DELAY and MAX_DELAY or similar constants

    Suggestion: Define backoff constants:
        MIN_DELAY = 1    # 1 second initial delay
        MAX_DELAY = 120  # 2 minutes max delay
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text()

    has_delay_constants = any([
        re.search(r'MIN_DELAY\s*=\s*\d+', content),
        re.search(r'MAX_DELAY\s*=\s*\d+', content),
        re.search(r'INITIAL_DELAY\s*=\s*\d+', content),
        re.search(r'DELAY\s*=\s*\d+', content),
        "backoff" in content.lower() and ("delay" in content.lower() or "interval" in content.lower()),
    ])

    if not has_delay_constants:
        pytest.fail(
            f"\n\n"
            f"Expected: Delay constants for backoff\n"
            f"Actual: No delay constants found\n\n"
            f"Suggestion: Define backoff constants:\n"
            f"  MIN_DELAY = 1    # Start with 1 second\n"
            f"  MAX_DELAY = 120  # Max 2 minutes between retries\n"
            f"\n"
            f"These constants make exponential backoff configurable.\n"
        )


# ---------------------------------------------------------------------------
# Test 3.3: Buffer Pattern (7 points)
# ---------------------------------------------------------------------------
def test_buffer_pattern():
    """
    Verify that data buffering is implemented for disconnections.

    Expected: Buffer or queue for storing data during disconnect

    Suggestion: Buffer data when disconnected:
        buffer = []
        if not connected:
            buffer.append((feed, value))
        # After reconnect:
        for feed, value in buffer:
            client.publish(feed, value)
        buffer.clear()
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text()

    has_buffer = any([
        "buffer" in content.lower(),
        "queue" in content.lower(),
        "pending" in content.lower(),
        "cache" in content.lower(),
    ])

    if not has_buffer:
        pytest.fail(
            f"\n\n"
            f"Expected: Data buffering for disconnections\n"
            f"Actual: No buffer pattern found\n\n"
            f"WHY THIS MATTERS:\n"
            f"  When disconnected, sensor data is lost!\n"
            f"  Buffering preserves data until reconnection.\n\n"
            f"Suggestion: Implement buffering:\n"
            f"  data_buffer = []\n"
            f"\n"
            f"  def publish_or_buffer(client, feed, value):\n"
            f"      if is_connected:\n"
            f"          client.publish(feed, value)\n"
            f"      else:\n"
            f"          data_buffer.append((feed, value))\n"
        )


# ---------------------------------------------------------------------------
# Test 3.4: Non-blocking Loop (8 points)
# ---------------------------------------------------------------------------
def test_non_blocking_loop():
    """
    Verify that non-blocking MQTT loop is used.

    Expected: loop_background() or threading for MQTT loop

    Suggestion: Use non-blocking loop:
        client.loop_background()
    """
    script_path = REPO_ROOT / "mqtt_publisher.py"

    if not script_path.exists():
        pytest.skip("mqtt_publisher.py not found")

    content = script_path.read_text()

    has_nonblocking = any([
        "loop_background" in content,
        "loop_start" in content,
        "threading" in content and "loop" in content.lower(),
    ])

    # Also check for blocking loop (which would be wrong)
    has_blocking = "loop_blocking" in content or ".loop()" in content

    if has_blocking and not has_nonblocking:
        pytest.fail(
            f"\n\n"
            f"Expected: Non-blocking MQTT loop\n"
            f"Actual: Found blocking loop pattern\n\n"
            f"WHY THIS MATTERS:\n"
            f"  loop_blocking() blocks your program!\n"
            f"  You can't read sensors or respond to buttons.\n\n"
            f"Suggestion: Use non-blocking loop:\n"
            f"  client.connect()\n"
            f"  client.loop_background()  # Runs in background thread\n"
            f"\n"
            f"  # Now you can do other things:\n"
            f"  while True:\n"
            f"      data = sensor.read()\n"
            f"      client.publish('temperature', data['temp'])\n"
        )

    if not has_nonblocking and not has_blocking:
        pytest.fail(
            f"\n\n"
            f"Expected: MQTT loop (preferably non-blocking)\n"
            f"Actual: No MQTT loop found\n\n"
            f"Suggestion: Add non-blocking loop:\n"
            f"  client.connect()\n"
            f"  client.loop_background()  # Required for callbacks!\n"
        )
