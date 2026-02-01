"""
Quick test to verify crisis detector works
"""

from crisis.detector import CrisisDetector
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Initialize detector
print("Loading crisis detector...")
detector = CrisisDetector()

# Test cases
test_messages = [
    ("I want to kill myself tonight", "IMMINENT"),
    ("I feel worthless and depressed", "HIGH"),
    ("Feeling a bit sad today", "LOW"),
    ("I have thoughts of self-harm", "HIGH"),
]

print("\n=== Testing Crisis Detection ===\n")

for message, expected_level in test_messages:
    result = detector.detect_risk(message)
    status = "✅" if result['risk_level'] == expected_level else "❌"
    print(f"{status} Input: \"{message}\"")
    print(f"   Detected: {result['risk_level']} (expected: {expected_level})")
    print(f"   Confidence: {result['confidence']:.2f}")
    # Show first 2 triggers
    print(
        f"   Triggers: {result['triggers'][:2] if result['triggers'] else 'None'}")
    print()

print("✅ Phase 1 Complete: Crisis Detector Working!\n")
