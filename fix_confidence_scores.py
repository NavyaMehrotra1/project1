#!/usr/bin/env python3
"""
Script to fix malformed confidence_score values in graph_data_for_frontend.json
Sets all confidence_score values to 1
"""

import json
import re

def fix_confidence_scores():
    file_path = "/Users/navyamehrotra/project1/data_agent/data_agent/output/graph_data_for_frontend.json"
    
    print("Loading graph data...")
    with open(file_path, 'r') as f:
        content = f.read()
    
    print("Fixing confidence_score values...")
    # Replace any confidence_score with a number (including large malformed ones) with 1
    pattern = r'"confidence_score":\s*\d+(?:\.\d+)?'
    replacement = '"confidence_score": 1'
    
    fixed_content = re.sub(pattern, replacement, content)
    
    print("Saving fixed data...")
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    # Count how many replacements were made
    matches = re.findall(pattern, content)
    print(f"Fixed {len(matches)} confidence_score values")
    
    # Verify the JSON is still valid
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        print("✅ JSON file is valid after fixes")
    except json.JSONDecodeError as e:
        print(f"❌ JSON validation error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = fix_confidence_scores()
    if success:
        print("🎉 All confidence scores successfully set to 1!")
    else:
        print("❌ Failed to fix confidence scores")
