#!/usr/bin/env python3
"""
Configuration validation script.
Run this to validate your topic configuration after adding new topics.

Usage:
    python scripts/validate_config.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.aggregation.sources_config import (
    validate_all_topics,
    get_all_categories,
    CATEGORY_DISPLAY_NAMES,
    RSS_SOURCES
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def main():
    """Main validation function."""
    print_section("Topic Configuration Validation")

    # Get all categories
    categories = get_all_categories()
    print(f"📋 Total categories configured: {len(categories)}")
    print(f"   {', '.join(categories)}\n")

    # Validate all topics
    results = validate_all_topics()

    print_section("Validation Results")
    print(f"✅ Valid topics: {results['valid']}")
    print(f"❌ Invalid topics: {results['invalid']}")

    # Show details for each topic
    if results['invalid'] > 0:
        print_section("Issues Found")

        for topic, validation in results['details'].items():
            if not validation['valid']:
                print(f"\n⚠️  Topic: {topic}")
                print(f"   Missing configuration:")
                for missing in validation['missing']:
                    print(f"   - {missing}")

    # Show summary by category
    print_section("Category Summary")

    for topic in sorted(categories):
        display_name = CATEGORY_DISPLAY_NAMES.get(topic, "❓ No display name")
        feed_count = len(RSS_SOURCES.get(topic, []))
        status = "✅" if results['details'][topic]['valid'] else "❌"

        print(f"{status} {display_name}")
        print(f"   Key: {topic}")
        print(f"   RSS Feeds: {feed_count}")

        if not results['details'][topic]['valid']:
            print(f"   Issues: {len(results['details'][topic]['missing'])}")

        print()

    # Final verdict
    print_section("Final Verdict")

    if results['invalid'] == 0:
        print("✅ All topics are properly configured!")
        print("   You can now run the main pipeline: python main.py")
        return 0
    else:
        print(f"❌ Found {results['invalid']} topic(s) with issues.")
        print("   Please fix the configuration issues listed above.")
        print("   Refer to docs/ADDING_NEW_TOPICS.md for guidance.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
