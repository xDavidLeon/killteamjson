# killteamjson — Claude Code Context

## Project Purpose

Machine-readable JSON dataset for **Warhammer 40K Kill Team (2024 edition)**, powering the [KT SERVITOR](https://ktservitor.app/) companion app. Data is sourced exclusively from official GW PDFs/website — no homebrew content.

Primary tasks are:
1. **Dataslate/season updates** — adding or correcting team data when GW releases new rules
2. **Bug fixes** — correcting wrong stats, weapon rules, or text

## Repository Structure

```
en/                         # English data (source of truth)
  teams/                    # One JSON per kill team  (e.g. IMP-AOD.json)
  packs/ops_2025.json       # Approved Tac Ops & Crit Ops
  packs/packs_actions.json  # Mission pack actions
  universal_actions.json
  universal_equipment.json
  weapon_rules.json
  rules_key.json
  rules_sequence.json
  rules_terrain.json
es/                         # Spanish translations (mirrors en/ structure exactly)
  teams/
  ...
extra/                      # Tier lists and supplementary data
tools/                      # Python scripts for translation (git-ignored)
killteam_ids.txt            # Reference list of all kill team IDs
README.md                   # Full schema documentation
```

## Translation Rule (IMPORTANT)

**Whenever `en/` is modified, the corresponding `es/` file must be updated too.**  
Keep all IDs, structure, and non-translatable fields identical. Only translate user-facing strings: `name`, `description`, `composition`, `ployName`, `abilityName`, `eqName`, `wepName`, `profileName`, `optionName`, etc.  
IDs (e.g. `killteamId`, `ployId`, `wepId`) are **never** translated.

## Kill Team File Naming

`[FACTION]-[CODE].json` — e.g. `IMP-AOD.json`, `AEL-BOK.json`, `CHAOS-CULT.json`

Faction prefixes: `AEL`, `CHAOS`, `IMP`, `NEC`, `ORK`, `SPEC`, `TAU`, `TYR`, `VOT`

## Key Schema Patterns

Full schema is in `README.md`. Quick reference for the most-edited fields:

### Team file top level
```jsonc
{
  "factionId": "IMP",
  "killteamId": "IMP-AOD",
  "version": "April '26",       // Month + year of latest dataslate
  "classified": true,
  "season": "Volkus",           // Or "Octarius", "Gallowdark", "BHETA-DECIMA", "Tomb world", ""
  "file": "https://...",        // Official GW PDF URL
  "killteamName": "...",
  "description": "...",         // Markdown lore text
  "composition": "...",         // Markdown roster rules
  "archetypes": ["Security", "Seek & Destroy"],
  "opTypes": [...],
  "ploys": [...],
  "equipments": [...]
}
```

### Operative stat line
`MOVE`, `APL`, `SAVE`, `WOUNDS` are strings (e.g. `"3\""`, `"2"`, `"3+"`, `"12"`).

### Weapon profile
```jsonc
{
  "wepprofileId": "IMP-AOD-WPN-X-P1",
  "wepId": "IMP-AOD-WPN-X",
  "seq": 1,
  "profileName": "",     // Empty string if single-profile weapon
  "ATK": "4",
  "HIT": "3+",
  "DMG": "3/5",          // normal/critical damage
  "WR": [
    { "id": "WR-UNIV-RANGE", "number": 6 },
    { "id": "WR-UNIV-LETHAL", "number": 5 }
  ]
}
```

Weapon rule IDs are defined in `en/weapon_rules.json`. Always reference existing `WR-` IDs rather than inventing new ones.

### Ploy types
- `"S"` — Strategy ploy (used in Strategy phase)
- `"T"` or `"F"` — Firefight ploy (used during firefight)

### ID construction convention
IDs follow a hierarchical dot-notation path:  
`{KILLTEAM_ID}-{ELEMENT_TYPE}-{SHORTCODE}` — e.g. `AEL-BOK-S-DOD` (ploy), `IMP-AOD-WPN-X-P1` (weapon profile).

## Workflow: Updating a Team for a New Dataslate

1. Locate the relevant PDF on the GW website and update the `file` URL.
2. Update `version` to the new dataslate month/year (e.g. `"April '26"`).
3. Apply stat/weapon/ploy/equipment changes from the PDF.
4. Check `en/weapon_rules.json` to confirm any referenced `WR-` IDs exist.
5. Mirror all changes to the matching `es/teams/` file (translate user-facing strings, keep IDs identical).

## Workflow: Bug Fix

1. Identify the file (`en/teams/{ID}.json`) and the wrong field.
2. Correct the value to match the official source PDF.
3. Mirror the fix to `es/teams/{ID}.json`.
4. Commit with a message like `fix: correct [field] for [team name]`.

## Commit Message Convention

```
feat: updated [TEAM NAME] to [Month 'YY]
fix: correct [field description] for [team name]
chore: [structural/tooling change]
```

## What NOT to Do

- Do not add homebrew stats, abilities, or rules not in official GW sources.
- Do not invent new `WR-` IDs — check `weapon_rules.json` first.
- Do not modify `es/` without also updating `en/` (or vice versa).
- Do not change IDs for existing entries — downstream apps (KT SERVITOR) reference them.
