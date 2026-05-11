# killteamjson — Claude Code Context

## Project Purpose

Machine-readable JSON dataset for **Warhammer 40K Kill Team (2024 edition)**, powering the [KT SERVITOR](https://ktservitor.app/) companion app. Data is sourced exclusively from official GW PDFs/website — no homebrew content.

Primary tasks are:
1. **Dataslate/season updates** — adding or correcting team data when GW releases new rules
2. **Bug fixes** — correcting wrong stats, weapon rules, or text

## Repository Structure

```
en/                         # English data (canonical source of truth)
  teams/                    # One JSON per kill team  (e.g. IMP-AOD.json)
  packs/ops_2025.json       # Approved Tac Ops & Crit Ops
  packs/packs_actions.json  # Mission pack actions
  universal_actions.json
  universal_equipment.json
  weapon_rules.json
  rules_key.json
  rules_sequence.json
  rules_terrain.json
es/                         # Generated Spanish flat JSON (for app/runtime compatibility)
  overlays/                 # Spanish sparse overlays (authoring source) — mirrors en/ layout
    teams/                  # One sparse overlay per translated team
    packs/
    ...                       # Same relative paths as en/ (e.g. rules_key.json, weapon_rules.json)
extra/                      # Tier lists and supplementary data
scripts/                    # Build/validation scripts
killteam_ids.txt            # Reference list of all kill team IDs (see below)
README.md                   # Full schema documentation
```

## killteam_ids.txt (IMPORTANT)

Whenever you **add a new kill team** (`en/teams/{ID}.json`), **always** update `killteam_ids.txt` at the repo root in the same pass:

- Add a line `killteamId` then tab then `killteamName`, matching the existing rows.
- Keep ordering consistent with the file (grouped by faction prefix, then by ID).
- Bump the trailing `Total: N teams` count to match.

Do not leave new team JSON in `en/teams/` without the corresponding `killteam_ids.txt` entry.

## Translation Rule (IMPORTANT)

**Whenever you change a file under `en/`, you must update the matching Spanish overlay under `es/overlays/` (same relative path), then regenerate flat `es/` files.** Do not treat `en/` as the only edit when an overlay exists for that path.

1. **Path pairing** — mirror the path after the locale folder:
   - `en/teams/{ID}.json` → `es/overlays/teams/{ID}.json`
   - `en/packs/foo.json` → `es/overlays/packs/foo.json`
   - `en/rules_key.json` → `es/overlays/rules_key.json` (and likewise for `weapon_rules.json`, `universal_actions.json`, `universal_equipment.json`, `rules_sequence.json`, `rules_terrain.json`, etc.)
2. **Author** sparse translations in that overlay (keyed by IDs / structure the build script expects), then run:
   `python3 scripts/build_es_locale.py build`
3. If the `en/` change is **only** structural (IDs, stats, `references` to other rule ids, sequencing) and the overlay does not duplicate those fields, still **open the paired overlay** and confirm nothing is stale; update any affected Spanish strings.

Translate user-facing strings such as `killteamName`, `description`, `composition`, `ployName`, `abilityName`, `eqName`, `wepName`, `profileName`, `optionName`, action `name`/`effects`/`conditions`, etc.

Do **not** localize structural/mechanical fields (`*Id`, stats, sequencing, weapon rules references, cross-rule `references[]` ids in `rules_key.json`).
Keep `archetypes[]`, `keywords`, and weapon rule `details` as canonical English tokens for now (localized client-side).

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
4. If you added a **new** team file under `en/teams/`, update `killteam_ids.txt` per **killteam_ids.txt (IMPORTANT)** above.
5. Check `en/weapon_rules.json` to confirm any referenced `WR-` IDs exist.
6. Update the matching `es/overlays/...` file(s) for any changed user-facing strings (at minimum `es/overlays/teams/{ID}.json`; if you edited other `en/*.json` in the same change, update those overlays too).
7. Regenerate flat Spanish files: `python3 scripts/build_es_locale.py build`.
8. Validate overlays and merge output:
   - `python3 scripts/build_es_locale.py validate`
   - `python3 scripts/build_es_locale.py verify`

## Workflow: Bug Fix

1. Identify the file (`en/teams/{ID}.json`) and the wrong field.
2. Correct the value to match the official source PDF.
3. Mirror translation-impacting text updates in the paired `es/overlays/...` file (same relative path as the `en/` file you fixed).
4. Rebuild and verify:
   - `python3 scripts/build_es_locale.py build`
   - `python3 scripts/build_es_locale.py verify`
5. Commit with a message like `fix: correct [field] for [team name]`.

## Commit Message Convention

```
feat: updated [TEAM NAME] to [Month 'YY]
fix: correct [field description] for [team name]
chore: [structural/tooling change]
```

## What NOT to Do

- Do not add a new `en/teams/{ID}.json` without updating `killteam_ids.txt` (and its total).
- Do not add homebrew stats, abilities, or rules not in official GW sources.
- Do not invent new `WR-` IDs — check `weapon_rules.json` first.
- Do not modify `es/` without also updating `en/` (or vice versa).
- Do not change `en/` without checking the matching `es/overlays/{same path}` and running `build` / `verify` when strings or overlay structure are affected.
- Do not change IDs for existing entries — downstream apps (KT SERVITOR) reference them.
