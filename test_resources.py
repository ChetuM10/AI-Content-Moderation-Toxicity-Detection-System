"""
Test crisis hotline resources
"""

import sys
sys.path.append('src')

from crisis.resources import CrisisResources

print("=== Testing Crisis Resources ===\n")

# Test for different countries
countries = ['US', 'IN', 'UK', 'AU']

for country in countries:
    resources = CrisisResources.get_resources(country)
    print(f"📍 {country} Resources:")
    for key, info in resources['hotlines'].items():
        print(f"   {info['name']}: {info['number']}")
    print()

print("✅ Phase 2 Complete: Resources Database Working!\n")
