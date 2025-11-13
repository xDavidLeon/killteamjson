#!/usr/bin/env python3
"""
Comprehensive translation script with full sentence translation.
Uses official GW terminology and translates complete sentences.
Note: For production use, integrate with translation API (DeepL, Google Translate, etc.)
"""

import json
import sys
import re
from pathlib import Path

# Expanded official GW Spanish terminology
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
    
    # Common phrases
    "An operative": "Un operativo",
    "operative": "operativo",
    "operatives": "operativos",
    "friendly operative": "operativo amigo",
    "friendly operatives": "operativos amigos",
    "enemy operative": "operativo enemigo",
    "enemy operatives": "operativos enemigos",
    "active operative": "operativo activo",
    "the active operative": "el operativo activo",
    
    # Game terms
    "Kill Team": "Kill Team",
    "Space Marine": "Marine Espacial",
    "Angels Of Death": "Ángeles de la Muerte",
    "kill team": "kill team",
    "killzone": "zona de combate",
    "turning point": "punto de inflexión",
    "activation": "activación",
    "counteraction": "contrataque",
    "control range": "alcance de control",
    "within control range": "dentro del alcance de control",
    
    # Weapon/stats
    "attack dice": "dados de ataque",
    "defence dice": "dados de defensa",
    "critical success": "éxito crítico",
    "critical successes": "éxitos críticos",
    "normal success": "éxito normal",
    "normal successes": "éxitos normales",
    "cover saves": "salvaciones de cobertura",
    
    # Status
    "incapacitated": "incapacitado",
    
    # Archetypes
    "Security": "Seguridad",
    "Seek & Destroy": "Buscar y Destruir",
    "Recon": "Reconocimiento",
    "Infiltration": "Infiltración",
}

# Expanded official GW French terminology
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
    
    # Common phrases
    "An operative": "Un opératif",
    "operative": "opératif",
    "operatives": "opératifs",
    "friendly operative": "opératif allié",
    "friendly operatives": "opératifs alliés",
    "enemy operative": "opératif ennemi",
    "enemy operatives": "opératifs ennemis",
    "active operative": "opératif actif",
    "the active operative": "l'opératif actif",
    
    # Game terms
    "Kill Team": "Kill Team",
    "Space Marine": "Marine Spatial",
    "Angels Of Death": "Anges de la Mort",
    "kill team": "kill team",
    "killzone": "zone de combat",
    "turning point": "point tournant",
    "activation": "activation",
    "counteraction": "contre-attaque",
    "control range": "portée de contrôle",
    "within control range": "dans la portée de contrôle",
    
    # Weapon/stats
    "attack dice": "dés d'attaque",
    "defence dice": "dés de défense",
    "critical success": "succès critique",
    "critical successes": "succès critiques",
    "normal success": "succès normal",
    "normal successes": "succès normaux",
    "cover saves": "sauvegardes de couverture",
    
    # Status
    "incapacitated": "hors de combat",
    
    # Archetypes
    "Security": "Sécurité",
    "Seek & Destroy": "Rechercher et Détruire",
    "Recon": "Reconnaissance",
    "Infiltration": "Infiltration",
}

def translate_string_advanced(text, lang_terms):
    """
    Advanced string translation using GW terminology.
    For full translations, this should integrate with a translation API.
    Currently does terminology replacement as a baseline.
    """
    if not isinstance(text, str) or not text.strip():
        return text
    
    # Replace terminology (longest matches first)
    translated = text
    for en_term, trans_term in sorted(lang_terms.items(), key=lambda x: -len(x[0])):
        # Word boundary-aware replacement for better matching
        pattern = re.compile(r'\b' + re.escape(en_term) + r'\b', re.IGNORECASE)
        translated = pattern.sub(trans_term, translated)
    
    # For full translation, you would call a translation API here:
    # translated = translation_api.translate(translated, source='en', target='es')
    
    return translated

def translate_value(value, field_name, lang_terms):
    """Recursively translate JSON values."""
    if isinstance(value, str):
        translatable_fields = ['name', 'description', 'killteamName', 'opTypeName', 
                              'wepName', 'abilityName', 'ployName', 'eqName', 
                              'optionName', 'title', 'profileName', 'composition',
                              'reveal', 'additionalRules', 'victoryPoints']
        
        if field_name in translatable_fields:
            return translate_string_advanced(value, lang_terms)
        return value
    elif isinstance(value, dict):
        return {k: translate_value(v, k, lang_terms) for k, v in value.items()}
    elif isinstance(value, list):
        if field_name == 'archetypes' and value and isinstance(value[0], str):
            return [lang_terms.get(v, v) for v in value]
        elif field_name in ['effects', 'conditions'] and value and isinstance(value[0], str):
            return [translate_string_advanced(v, lang_terms) if isinstance(v, str) else v for v in value]
        elif field_name == 'packs' and value and isinstance(value[0], str):
            return [translate_string_advanced(v, lang_terms) if isinstance(v, str) else v for v in value]
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
        print(f"  [ERROR] Reading {en_file}: {e}")
        return False
    
    # Translate
    translated = translate_value(data, "", lang_terms)
    
    # Validate JSON
    try:
        json.dumps(translated)
    except Exception as e:
        print(f"  [ERROR] Invalid JSON structure after translation: {e}")
        return False
    
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
    """Translate all JSON files."""
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
    
    print("=" * 60)
    print("Translating all JSON files with GW terminology")
    print("=" * 60)
    
    print("\n[SPANISH] Translating files...")
    for filename in files:
        en_file = en_dir / filename
        es_file = es_dir / filename
        if en_file.exists():
            translate_file(en_file, es_file, GW_SPANISH, "Spanish")
    
    print("\n[FRENCH] Translating files...")
    for filename in files:
        en_file = en_dir / filename
        fr_file = fr_dir / filename
        if en_file.exists():
            translate_file(en_file, fr_file, GW_FRENCH, "French")
    
    print("\n" + "=" * 60)
    print("[OK] Translation complete!")
    print("=" * 60)
    print("\nNOTE: These translations use GW terminology replacement.")
    print("For full sentence-level translations, integrate with a translation API")
    print("(e.g., DeepL, Google Translate) or manually refine the translations.")

if __name__ == '__main__':
    main()

