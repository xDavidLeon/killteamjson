#!/usr/bin/env python3
"""
Check translation completeness by comparing English and translated files.
Reports which fields are translated and which are missing.
"""

import json
import sys
from pathlib import Path
from extract_translatables import extract_strings, is_translatable_key

def get_translatable_strings(data, path="", strings=None):
    """Get all translatable strings with their paths and values."""
    if strings is None:
        strings = {}
    
    if isinstance(data, dict):
        for key, value in data.items():
            full_path = f"{path}.{key}" if path else key
            
            if is_translatable_key(key):
                if isinstance(value, str) and value.strip():
                    strings[full_path] = value
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, str) and item.strip():
                            strings[f"{full_path}[{i}]"] = item
            else:
                if isinstance(value, (dict, list)):
                    get_translatable_strings(value, full_path, strings)
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            get_translatable_strings(item, f"{path}[{i}]", strings)
    
    return strings

def check_completeness(english_file, translation_file):
    """Check translation completeness."""
    try:
        with open(english_file, 'r', encoding='utf-8') as f:
            en_data = json.load(f)
    except Exception as e:
        print(f"Error reading English file: {e}")
        return False
    
    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            trans_data = json.load(f)
    except Exception as e:
        print(f"Error reading translation file: {e}")
        return False
    
    # Get all translatable strings
    en_strings = get_translatable_strings(en_data)
    trans_strings = get_translatable_strings(trans_data)
    
    # Find missing translations
    missing = []
    translated = []
    untranslated = []
    
    for path, en_value in en_strings.items():
        if path not in trans_strings:
            missing.append(path)
        elif trans_strings[path] == en_value:
            untranslated.append(path)  # Same as English, likely not translated
        else:
            translated.append(path)
    
    # Calculate completeness
    total = len(en_strings)
    translated_count = len(translated)
    missing_count = len(missing)
    untranslated_count = len(untranslated)
    completeness = (translated_count / total * 100) if total > 0 else 0
    
    # Report
    print(f"\nTranslation Completeness Report")
    print(f"File: {translation_file}")
    print(f"{'='*60}")
    print(f"Total translatable strings: {total}")
    print(f"Translated: {translated_count} ({completeness:.1f}%)")
    print(f"Missing: {missing_count}")
    print(f"Untranslated (same as English): {untranslated_count}")
    
    if missing:
        print(f"\n[WARNING] Missing translations ({len(missing)}):")
        for path in missing[:20]:  # Show first 20
            print(f"  - {path}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")
    
    if untranslated:
        print(f"\n[INFO] Potentially untranslated ({len(untranslated)}):")
        for path in untranslated[:10]:  # Show first 10
            en_val = en_strings[path][:50] + "..." if len(en_strings[path]) > 50 else en_strings[path]
            trans_val = trans_strings[path][:50] + "..." if len(trans_strings[path]) > 50 else trans_strings[path]
            print(f"  - {path}")
            print(f"    EN: {en_val}")
            print(f"    TR: {trans_val}")
        if len(untranslated) > 10:
            print(f"  ... and {len(untranslated) - 10} more")
    
    if not missing and translated_count > 0:
        print(f"\n[OK] Translation appears complete!")
    
    return missing_count == 0

def main():
    if len(sys.argv) < 3:
        print("Usage: python check_translation_completeness.py <english_file> <translation_file>")
        print("Example: python check_translation_completeness.py teams.json teams.fr.json")
        sys.exit(1)
    
    english_file = sys.argv[1]
    translation_file = sys.argv[2]
    
    if not Path(english_file).exists():
        print(f"Error: English file not found: {english_file}")
        sys.exit(1)
    
    if not Path(translation_file).exists():
        print(f"Error: Translation file not found: {translation_file}")
        sys.exit(1)
    
    success = check_completeness(english_file, translation_file)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

