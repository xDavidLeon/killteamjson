#!/usr/bin/env python3
"""
Extract all translatable strings from JSON files into a structured format.
Useful for translation services and maintaining translation templates.
"""

import json
import sys
from pathlib import Path

# Fields that should NOT be translated
NON_TRANSLATABLE_FIELDS = {
    '*Id', '*id',  # All ID fields
    'version',
    'seq',
    'MOVE', 'APL', 'SAVE', 'WOUNDS',
    'ATK', 'HIT', 'DMG',
    'isDefault', 'isPublished', 'isHomebrew', 'isOpType', 'isActivated',
    'basesize', 'currWOUNDS',
    'amount',
    'AP',
    'wepType',
    'type',  # May need translation, but context-dependent
    'effects',  # Encoded string, not translatable
}

# Fields that definitely should be translated
TRANSLATABLE_FIELDS = {
    'killteamName', 'description', 'composition',
    'opTypeName', 'wepName', 'profileName',
    'abilityName', 'ployName', 'eqName', 'optionName',
    'name', 'title',
    'reveal', 'additionalRules', 'victoryPoints',
}

def is_translatable_key(key):
    """Determine if a key contains translatable content."""
    # Skip ID fields
    if key.lower().endswith('id'):
        return False
    
    # Skip known non-translatable fields
    if key in NON_TRANSLATABLE_FIELDS:
        return False
    
    # Explicitly translatable fields
    if key in TRANSLATABLE_FIELDS:
        return True
    
    # Fields with 'description' or 'name' are likely translatable
    if 'description' in key.lower() or 'name' in key.lower():
        return True
    
    # Arrays might contain translatable strings
    if key == 'archetypes':
        return True
    
    return False

def extract_strings(data, path="", strings=None):
    """Recursively extract translatable strings from JSON."""
    if strings is None:
        strings = {}
    
    if isinstance(data, dict):
        for key, value in data.items():
            full_path = f"{path}.{key}" if path else key
            
            if is_translatable_key(key):
                if isinstance(value, str) and value.strip():
                    strings[full_path] = value
                elif isinstance(value, list):
                    # Handle arrays (like archetypes)
                    for i, item in enumerate(value):
                        if isinstance(item, str) and item.strip():
                            strings[f"{full_path}[{i}]"] = item
            else:
                # Recurse into nested structures
                if isinstance(value, (dict, list)):
                    extract_strings(value, full_path, strings)
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            extract_strings(item, f"{path}[{i}]", strings)
    
    return strings

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_translatables.py <json_file> [output_file]")
        print("Example: python extract_translatables.py teams.json teams_translatable.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(json_file).exists():
        print(f"Error: File not found: {json_file}")
        sys.exit(1)
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Extract translatable strings
    strings = extract_strings(data)
    
    # Prepare output
    output = {
        "source_file": json_file,
        "total_strings": len(strings),
        "strings": strings
    }
    
    # Output
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"Extracted {len(strings)} translatable strings to {output_file}")
    else:
        # Print to stdout
        print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()

