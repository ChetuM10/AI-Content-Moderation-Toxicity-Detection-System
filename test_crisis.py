import sys
sys.path.insert(0, 'src')  # Tell Python to look in src/ folder

from crisis.detector import CrisisDetector
from crisis.resources import CrisisResources

# Test detector
print("=== Testing Crisis Detector ===\n")
detector = CrisisDetector()

tests = [
    ("I want to kill myself tonight", "IMMINENT"),
    ("I feel worthless and depressed", "HIGH"),
    ("Feeling a bit sad today", "LOW"),
]

for text, expected in tests:
    result = detector.detect_risk(text)
    status = "✅" if result['risk_level'] == expected else "❌"
    print(f"{status} '{text}' → {result['risk_level']} (expected {expected})")

# Test resources
print("\n=== Testing Crisis Resources ===\n")
resources = CrisisResources.get_resources('IN')
print(f"India Crisis Hotline: {resources['hotlines']['suicide_prevention']['number']}")
print(f"Emergency: {resources['hotlines']['emergency']['number']}")

print("\n🎉 Phase 1-3 Complete!")
