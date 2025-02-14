"""Tests for the json_to_markdown helper module."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.json_to_markdown import json_to_markdown

def test_basic_conversion():
    """Test basic JSON to markdown conversion."""
    test_data = {
        "Project": {
            "Name": "Test Project",
            "Details": {
                "Version": "1.0",
                "Status": "Active",
                "Components": ["Web", "API", "Database"],
                "Configuration": {
                    "Environment": "Production",
                    "Debug": False
                }
            }
        }
    }
    
    result = json_to_markdown(test_data)
    print("\nTest output:")
    print(result)
    
    expected_parts = [
        "## Project",
        "### Name",
        "Test Project",
        "### Details",
        "* Version",
        "  - 1.0",
        "* Status",
        "  - Active",
        "* Components",
        "  * Web",
        "  * API",
        "  * Database",
        "* Configuration",
        "  * Environment",
        "    - Production",
        "  * Debug",
        "    - False"
    ]
    
    # Verify each expected part is in the result
    for part in expected_parts:
        assert part in result, f"Missing expected part: {part}"
    
if __name__ == "__main__":
    test_basic_conversion()
    print("All tests passed!")
