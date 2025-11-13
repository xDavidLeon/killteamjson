#!/usr/bin/env python3
"""
Comprehensive translation script for all JSON files.
Translates English JSON files to Spanish and French using official Games Workshop terminology.
"""

import json
import sys
from pathlib import Path

# Official GW Spanish terminology
GW_SPANISH = {
    # Actions
    "Shoot": "Disparar",
    "Fight": "Combatir",
    "Reposition": "Reposicionar",
    "Dash": "Carrera",
    "Fall Back": "Retirada",
    "Charge": "Carga",
    "Guard": "Vigilancia",
    "Pick Up Marker": "Recoger Marcador",
    "Place Marker": "Colocar Marcador",
    "Counteract": "Contraatacar",
    
    # Game terms
    "operative": "operativo",
    "operatives": "operativos",
    "Kill Team": "Kill Team",  # Often kept in English
    "Space Marine": "Marine Espacial",
    "Angels Of Death": "Ángeles de la Muerte",
    "kill team": "kill team",
    
    # Keywords
    "LEADER": "LÍDER",
    
    # Weapon rules
    "Critical success": "Éxito crítico",
    "critical success": "éxito crítico",
    "critical successes": "éxitos críticos",
    "normal success": "éxito normal",
    "normal successes": "éxitos normales",
    "attack dice": "dados de ataque",
    "defence dice": "dados de defensa",
    "cover saves": "salvaciones de cobertura",
    
    # Status
    "incapacitated": "incapacitado",
    "activation": "activación",
    "counteraction": "contrataque",
    "turning point": "punto de inflexión",
    
    # Archetypes
    "Security": "Seguridad",
    "Seek & Destroy": "Buscar y Destruir",
    "Recon": "Reconocimiento",
    "Infiltration": "Infiltración",
}

# Official GW French terminology
GW_FRENCH = {
    # Actions
    "Shoot": "Tirer",
    "Fight": "Combattre",
    "Reposition": "Repositionner",
    "Dash": "Ruée",
    "Fall Back": "Repli",
    "Charge": "Charge",
    "Guard": "Vigilance",
    "Pick Up Marker": "Ramasser un Marqueur",
    "Place Marker": "Placer un Marqueur",
    "Counteract": "Contre-attaquer",
    
    # Game terms
    "operative": "opératif",
    "operatives": "opératifs",
    "Kill Team": "Kill Team",
    "Space Marine": "Marine Spatial",
    "Angels Of Death": "Anges de la Mort",
    "kill team": "kill team",
    
    # Keywords
    "LEADER": "CHEF",
    
    # Weapon rules
    "Critical success": "Succès critique",
    "critical success": "succès critique",
    "critical successes": "succès critiques",
    "normal success": "succès normal",
    "normal successes": "succès normaux",
    "attack dice": "dés d'attaque",
    "defence dice": "dés de défense",
    "cover saves": "sauvegardes de couverture",
    
    # Status
    "incapacitated": "hors de combat",
    "activation": "activation",
    "counteraction": "contre-attaque",
    "turning point": "point tournant",
    
    # Archetypes
    "Security": "Sécurité",
    "Seek & Destroy": "Rechercher et Détruire",
    "Recon": "Reconnaissance",
    "Infiltration": "Infiltration",
}

def translate_text(text, lang_terms):
    """Translate text using GW terminology dictionary."""
    if not isinstance(text, str) or not text.strip():
        return text
    
    # Apply term-by-term replacement (longest first to avoid partial matches)
    translated = text
    # Sort by length descending to match longer terms first
    for en_term, trans_term in sorted(lang_terms.items(), key=lambda x: -len(x[0])):
        # Use word boundary-aware replacement where appropriate
        # For now, simple replacement - manual review needed for context
        translated = translated.replace(en_term, trans_term)
    
    return translated

def translate_value(value, field_name, lang_terms):
    """Recursively translate JSON values."""
    if isinstance(value, str):
        # Only translate certain fields
        translatable_fields = ['name', 'description', 'killteamName', 'opTypeName', 
                              'wepName', 'abilityName', 'ployName', 'eqName', 
                              'optionName', 'title', 'profileName', 'composition',
                              'reveal', 'additionalRules', 'victoryPoints']
        
        if field_name in translatable_fields:
            return translate_text(value, lang_terms)
        return value
    elif isinstance(value, dict):
        return {k: translate_value(v, k, lang_terms) for k, v in value.items()}
    elif isinstance(value, list):
        # Check if list contains translatable strings (like archetypes)
        if field_name == 'archetypes' and value and isinstance(value[0], str):
            return [lang_terms.get(v, v) for v in value]
        elif field_name == 'packs' and value and isinstance(value[0], str):
            # Packs might contain translatable names
            return [translate_text(v, lang_terms) if isinstance(v, str) else v for v in value]
        elif field_name in ['effects', 'conditions'] and value and isinstance(value[0], str):
            # Translate each string in effects/conditions arrays
            return [translate_text(v, lang_terms) if isinstance(v, str) else v for v in value]
        return [translate_value(item, field_name, lang_terms) for item in value]
    else:
        return value

def translate_file(en_file, target_file, lang_terms, lang_name):
    """Translate a JSON file."""
    print(f"Translating {en_file.name} to {lang_name}...")
    
    try:
        with open(en_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  Error reading {en_file}: {e}")
        return False
    
    # Translate
    translated = translate_value(data, "", lang_terms)
    
        # Write
    try:
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(translated, f, ensure_ascii=False, indent=2)
        print(f"  [OK] Created {target_file.name}")
        return True
    except Exception as e:
        print(f"  [ERROR] Writing {target_file}: {e}")
        return False

def main():
    """Translate all JSON files to Spanish and French."""
    files = [
        'weapon_rules.json',
        'universal_equipment.json',
        'universal_actions.json',
        'mission_actions.json',
        'ops_2025.json',
        'teams.json'
    ]
    
    en_dir = Path('en')
    es_dir = Path('es')
    fr_dir = Path('fr')
    
    es_dir.mkdir(exist_ok=True)
    fr_dir.mkdir(exist_ok=True)
    
    print("Translating files to Spanish...")
    print("=" * 50)
    for filename in files:
        en_file = en_dir / filename
        es_file = es_dir / filename
        
        if en_file.exists():
            translate_file(en_file, es_file, GW_SPANISH, "Spanish")
        else:
            print(f"Warning: {en_file} not found")
    
    print("\nTranslating files to French...")
    print("=" * 50)
    for filename in files:
        en_file = en_dir / filename
        fr_file = fr_dir / filename
        
        if en_file.exists():
            translate_file(en_file, fr_file, GW_FRENCH, "French")
        else:
            print(f"Warning: {en_file} not found")
    
    print("\n[OK] Translation complete!")
    print("\nNote: This is a basic translation using terminology dictionaries.")
    print("For complete translations, manual review and refinement is recommended.")

if __name__ == '__main__':
    main()

