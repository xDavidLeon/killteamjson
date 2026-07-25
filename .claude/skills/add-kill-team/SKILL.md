---
name: add-kill-team
description: Add a new Warhammer 40K Kill Team (2024) to this dataset from an official GW rules PDF. Use when the user wants to add a new team, import a team from a rules PDF/URL, or create a new en/teams/{ID}.json (and its Spanish overlay). Covers PDF extraction, the JSON schema, ID conventions, killteam_ids.txt, Spanish overlays, and the build/verify/commit steps — including the gotchas that are easy to get wrong.
---

# Add a new Kill Team

Goal: turn an official GW PDF into `en/teams/{ID}.json` (+ `killteam_ids.txt` row + Spanish overlay), then build/verify and commit. Data must come **only** from official GW sources — never invent stats or rules.

Read `README.md` (full schema) and this repo's `CLAUDE.md` before starting. Study **one existing team of the same faction** as a live template (e.g. `en/teams/AEL-BOK.json`) — match its field shapes exactly.

## 0. Get the PDF(s)

Ask for / locate the English PDF URL. Also ask whether an **official Spanish PDF** exists (GW publishes `spa_...` alongside `eng_...`) — if so, get that URL too and translate from it rather than translating yourself.

Download to the scratchpad and extract text with **pypdf** (do NOT rely on other tools):
- `WebFetch` fails on PDFs >10 MB (`maxContentLength exceeded`).
- The `Read` tool needs poppler (`pdftoppm`), which is **not installed** here.
- `pdftotext` is also not installed. `pypdf` **is** available.

```bash
SP=<scratchpad>            # from the session's scratchpad path
curl -sL "<PDF_URL>" -o "$SP/team.pdf"
python3 -c "
import pypdf
r=pypdf.PdfReader('$SP/team.pdf')
open('$SP/team.txt','w').write(''.join(f'\n===== PAGE {i+1} =====\n'+p.extract_text() for i,p in enumerate(r.pages)))
print('pages',len(r.pages))
"
```
Then `Read` the `.txt`.

**Gotcha — jumbled datacards:** the front datacard page interleaves multiple operatives (weapon tables, abilities, keyword line, stat line appear out of order). Attribute each weapon table to an operative by matching it to the nearest `KEYWORDS ... , <ROLE>` line and the `NAME  APL SAVE WOUNDS` / `MOVE` stat block. Cross-check against the "Kill Team Selection" pages near the end, which list each operative's weapons by name.

## 1. Choose IDs

- **killteamId** = `{FACTION}-{CODE}` (uppercase). Faction prefixes in use: `AEL`, `CHAOS`, `IMP`, `NEC`, `ORK`, `SPEC`, `TAU`, `TYR`, `VOT`. Pick a short mnemonic CODE not already taken (check `killteam_ids.txt`).
- All child IDs are dot-path style under the killteamId, e.g. operative `AEL-EDM-LEY`, weapon `AEL-EDM-LEY-LR`, profile `AEL-EDM-LEY-LR-0`, ability `AEL-EDM-LEY-A-UPG`, ploy `AEL-EDM-S-DF`, equipment `AEL-EDM-EQ-CT`, action `AEL-EDM-STO-ACT-SOR`.
- **Never reuse or change IDs** of existing entries — downstream apps (KT SERVITOR) reference them.

## 2. Build `en/teams/{ID}.json`

Prefer generating it with a small Python script in the scratchpad (dump with `json.dump(..., ensure_ascii=False, indent=2)` and a trailing newline) — it avoids hand-JSON syntax errors and lets you validate immediately.

Top level: `factionId`, `killteamId`, `version` (dataslate `"Month 'YY"`), `classified` (true), `season` (`""` if none), `file` (the PDF URL), `killteamName`, `description` (lore), `composition` (markdown roster), `archetypes` (array), `ploys`, `equipments`, `teamAbilities`, `opTypes`, and optionally `weapon_rules` (team-specific rules).

### Mapping rules & gotchas (learned the hard way)

- **Faction rules → `teamAbilities`** `[{abilityId, abilityName, description}]`. If a faction rule grants unique **actions** shared by many operatives (e.g. Sprint/Turn for all MOUNTED), describe those actions inside that faction rule's `description` (markdown `**Action (0AP)**` sub-headers) rather than duplicating them on every operative.
- **Per-operative selectable upgrades** ("select 2 of 5", chapter-tactic style): model as **one `ability` per operative** whose markdown `description` lists the selection rule + all options as `**Name**` sub-sections. This mirrors the proven `AEL-BOK` "Aspect Techniques" pattern and renders reliably. Do **not** use the `options[]` field — no team uses it and app rendering is unproven.
- **An operative's own unique action** (clean 1AP/2AP action, e.g. a psychic heal) → structured `actions[]`: `{id, type:"ability", seq, AP, name, description:null, effects:[...], conditions:[...]}` (see `en/teams/NEC-CAN.json`).
- **Weapons:** `wepType` is `R` (ranged), `M` (melee), `P`, or `E`. Single-profile weapons use `profileName: ""` and one profile `-0`. Multi-profile (e.g. a rifle with mobile/stationary) get profiles `-0`, `-1` with named `profileName`s.
- **`WR` weapon-rule refs:** reuse existing `WR-UNIV-*` IDs from `en/weapon_rules.json` (`{id, number?}`). **Never invent** a `WR-` ID. If the PDF has a genuinely team-specific rule (e.g. "Aimed"), add it to the team file's own `weapon_rules: [{id:"WR-{FACTION}-{CODE}-XXX", name, description, team:"{ID}"}]` and reference that ID (pattern: `NEC-CAN`'s embedded rule). Verify every referenced ID resolves.
- **`basesize`:** integer for round bases (`28`, `32`); **string** for ovals (`"75x42"`).
- Stats `MOVE`, `APL`, `SAVE`, `WOUNDS` — follow the existing files' string/number choices (e.g. `MOVE:"12\""`, `SAVE:"3+"`; APL/WOUNDS are often numbers).
- Keep `keywords` exactly as printed (comma-separated). Only include `LEADER` if the PDF prints it.
- Ploy `ployType`: `S` (Strategy), `T`/`F` (Firefight).

Validate as you go: `python3 -c "import json; json.load(open('en/teams/{ID}.json'))"` and a small script that checks every `WR` id resolves against `en/weapon_rules.json` + the team's embedded `weapon_rules`.

## 3. Update `killteam_ids.txt` (REQUIRED)

Add a `killteamId<TAB>killteamName` row in the correct spot (grouped by faction prefix, then alphabetical by ID), and **bump the `Total: N teams`** line. Never leave a new team file without this row.

## 4. Spanish overlay `es/overlays/teams/{ID}.json`

Authoring source is the sparse overlay (see an existing one like `es/overlays/teams/AEL-BOK.json` for shape). Keyed-by-ID structure:
```
{ killteamId, locale:"es",
  team:{killteamName, description, composition},
  ploys:{<ployId>:{ployName, description}},
  equipments:{<eqId>:{eqName, description, effects}},
  teamAbilities:{<abilityId>:{abilityName, description}},
  opTypes:{<opTypeId>:{opTypeName,
     weapons:{<wepId>:{wepName, profiles?:{<wepprofileId>:{profileName}}}},
     abilities:{<abilityId>:{abilityName, description}},
     actions:{<actionId>:{name, effects:[...], conditions:[...]}} }} }
```
- Translate user-facing strings only (`killteamName`, `description`, `composition`, `ployName`, `abilityName`, `eqName`, `wepName`, `profileName`, action `name/effects/conditions`). Do **not** localize `*Id`s, stats, sequencing, or `WR` references.
- **`en/` is canonical.** If the official Spanish PDF conflicts with English on a *stat or mechanic* (GW translation errors happen — e.g. profile labels/Hit stats swapped), keep the English value and only translate the surrounding text/names. Note the discrepancy to the user.
- Team-embedded `weapon_rules` are **not** translated by the build (no overlay path); they stay English, consistent with the rest of the repo.
- Not every team has an overlay — an English-only team is acceptable (build falls back to English), but prefer authoring the overlay when a Spanish PDF exists.

## 5. Build, validate, verify (local only)

```bash
python3 scripts/build_es_locale.py build
python3 scripts/build_es_locale.py validate
python3 scripts/build_es_locale.py verify      # expect: VALIDATE OK / VERIFY OK
```
The flat `es/` files this generates are **git-ignored build artifacts** (see `.gitignore`). Run these to check your work, but **never stage or commit the flat `es/` files** — commit only `es/overlays/` sources.

## 6. Commit

Stage exactly: `en/teams/{ID}.json`, `es/overlays/teams/{ID}.json`, `killteam_ids.txt` (and the team file's referenced changes only). Do **not** stage generated flat `es/` files or unrelated files the build may have resynced.

Commit message: `feat: add {Team Name} ({Month 'YY})`. End the body with:
```
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```
Only push if the user asks.

## Quick checklist

- [ ] `en/teams/{ID}.json` valid JSON; all `WR` ids resolve; oval bases are strings
- [ ] Faction rules in `teamAbilities`; upgrades as one markdown ability/operative; unique actions in `actions[]`
- [ ] `killteam_ids.txt` row added + `Total:` bumped
- [ ] `es/overlays/teams/{ID}.json` authored (from Spanish PDF if available); EN kept canonical on conflicts
- [ ] `build` / `validate` / `verify` all pass
- [ ] Commit contains only source files (no flat `es/`)
