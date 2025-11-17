# killteamjson
JSON Dataset for Killteam 2024. Forked form [https://github.com/vjosset/killteamjson](https://github.com/vjosset/killteamjson)

See also [KT SERVITOR](https://ktservitor.xdavidleon.com/)

## JSON File Structures

### `teams/` (Individual Team Files)

Kill team definitions are stored as individual JSON files in the `teams/` subfolder, one file per kill team (e.g., `teams/IMP-AOD.json`). Each team file contains a single kill team object with:

- `factionId` - *string* - Faction identifier.
- `killteamId` - *string* - Unique kill team identifier.
- `version` - *string* - Version identifier (e.g., "October '25").
- `classified` - *boolean* - Whether the kill team is classified. Defaults to `true`, but is `false` for teams from the Octarius season.
- `season` - *string* - The season or release wave the kill team belongs to. Possible values include: `"Octarius"`, `"Gallowdark"`, `"BHETA-DECIMA"`, `"Volkus"`, `"Tomb world"`, or an empty string `""` for teams without a specific season assignment.
- `file` - *string* - URL to the official PDF source.
- `killteamName` - *string* - Display name.
- `description` - *string* - Markdown-formatted lore/flavour text.
- `composition` - *string* - Markdown-formatted roster construction rules.
- `archetypes` - *string[]* - Array of archetype keywords (e.g., ["Security", "Seek & Destroy"]).
- `opTypes` - *array* - Operative type definitions for the kill team (see below).
- `ploys` - *array* - Strategy and firefight ploys available to the team.
- `equipments` - *array* - Kill team equipment items (see also `universal_equipment.json`).

#### Operative types (`opTypes`)

Each operative type object contains profile data:

- `opTypeId` - *string* - Unique operative type identifier.
- `killteamId` - *string* - Owning kill team ID.
- `seq` - *integer* - Display ordering.
- `opTypeName` - *string* - Name shown on datasheets.
- `MOVE`, `APL`, `SAVE`, `WOUNDS` - *string | number* - Core stat line values.
- `keywords` - *string* - Comma-separated gameplay keywords.
- `basesize` - *integer* - Base diameter in millimetres.
- `weapons` - *array* - Weapon entries for the operative (see below).
- `abilities` - *array* - Special rules tied to the operative.
- `options` - *array* - Selectable loadout or tactic options (e.g., chapter tactics).

##### Weapons (`opTypes[].weapons`)

- `wepId` - *string* - Weapon identifier.
- `opTypeId` - *string* - Parent operative type.
- `seq` - *integer* - Display ordering.
- `wepName` - *string* - Weapon name.
- `wepType` - *string* - Weapon category (`R`, `M`, `P`, `E`).
- `profiles` - *array* - Attack profile definitions.

Weapon profiles contain:

- `wepprofileId` - *string* - Profile identifier.
- `wepId` - *string* - Parent weapon identifier.
- `seq` - *integer* - Ordering for multi-profile weapons.
- `profileName` - *string* - Optional profile label (may be empty string).
- `ATK` - *string* - Number of attack dice.
- `HIT` - *string* - Hit roll requirement (e.g., "3+").
- `DMG` - *string* - Damage stats in format "normal/critical" (e.g., "3/5").
- `WR` - *array* - Array of weapon rule objects, each containing:
  - `id` - *string* - Weapon rule identifier (references `weapon_rules.json`).
  - `number` - *integer | undefined* - Optional numeric parameter for the rule (e.g., range, lethal threshold).

##### Abilities (`opTypes[].abilities`)

- `abilityId` - *string* - Unique ability identifier.
- `opTypeId` - *string* - Parent operative type.
- `abilityName` - *string* - Display name.
- `description` - *string* - Markdown-formatted rules text.

##### Options (`opTypes[].options`)

- `optionId` - *string* - Unique option identifier.
- `opTypeId` - *string* - Parent operative type.
- `seq` - *integer* - Ordering for presentation.
- `optionName` - *string* - Display name.
- `description` - *string* - Markdown-formatted rules explanation.
- `effects` - *string* - Encoded modifications applied when the option is taken.

#### Ploys (`ploys`)

- `ployId` - *string* - Unique ploy identifier.
- `killteamId` - *string* - Parent kill team.
- `seq` - *integer* - Display ordering.
- `ployType` - *string* - `S` for Strategy ploys, `T` or `F` for Firefight ploys.
- `ployName` - *string* - Display name.
- `description` - *string* - Markdown-formatted rules text.

#### Equipment (`equipments`)

- `eqId` - *string* - Unique equipment identifier.
- `killteamId` - *string | null* - Owning kill team (or `null` when referencing universal gear).
- `seq` - *integer* - Display ordering.
- `eqName` - *string* - Equipment name.
- `description` - *string* - Markdown-formatted text.
- `effects` - *string* - Encoded effects applied when equipped.
- `weapons` - *array* - Optional array of weapon objects embedded in the equipment. When present, contains weapon definitions that are granted by this equipment. Each weapon object follows the same structure as `opTypes[].weapons`, but with `opTypeId` set to `null` since these weapons are not tied to a specific operative type.

### `universal_actions.json`

Universal actions available to all kill teams. Root object contains an `actions` array. Each action object contains:

- `id` - *string* - Action identifier.
- `type` - *string* - Action type: `universal`, `mission`, or `ability`.
- `seq` - *integer* - Ordering for presentation.
- `AP` - *integer* - Action Point cost.
- `name` - *string* - Display name.
- `description` - *string | null* - Markdown-formatted summary (may be null).
- `effects` - *string[]* - Array of effect descriptions, each as a bullet point. May be an empty array for actions that are fully described in the `description` field.
- `conditions` - *string[]* - Array of preconditions or restrictions.
- `packs` - *string[]* - Mission packs where the action is available (optional field, only present when an action is limited to specific killzones or mission packs).

### `universal_equipment.json`

Universal equipment options. Root object contains:

- `version` - *string* - Version identifier (e.g., "October '25").
- `file` - *string* - URL to the official PDF source.
- `equipments` - *array* - Array of equipment objects, each containing:
  - `eqId` - *string* - Equipment identifier (shared IDs can also appear in `teams.json`).
  - `killteamId` - *string | null* - Kill team ID when restricted, otherwise `null` for universal equipment.
  - `seq` - *integer* - Ordering value.
  - `eqName` - *string* - Equipment name.
  - `description` - *string* - Markdown-formatted rules text.
  - `effects` - *string* - Encoded effect string (may be empty).
  - `amount` - *integer* - Quantity of the item granted on selection.
  - `actions` - *string[]* - Optional array of action IDs that this equipment grants access to.
- `actions` - *array* - Array of action objects associated with equipment. Each action object follows the same structure as `actions.json`.

### `weapon_rules.json`

Weapon rule glossary. Root object contains a `weapon_rules` array. Each weapon rule object contains:

- `id` - *string* - Rule identifier referenced from weapon profiles (`WR` fields in `teams.json`).
- `name` - *string* - Display name of the rule.
- `description` - *string* - Detailed rules text explaining how the rule works.
- `team` - *string | null* - Kill team identifier if this is a team-specific rule, otherwise `null` for universal rules.

### `ops_2025.json`

Approved Operations (Tac Ops and Crit Ops) for 2025. Root object contains:

- `ops` - *array* - Array of operation objects (tac ops and crit ops), each containing:
  - `id` - *string* - Unique operation identifier.
  - `type` - *string* - Operation type: `tac-op` or `crit-op`.
  - `packs` - *string[]* - Mission packs where this operation is available.
  - `title` - *string* - Display name of the operation.
  - `archetype` - *string | null* - Archetype keyword for tac ops (e.g., "Recon", "Seek & Destroy", "Security", "Infiltration"), or `null` for crit ops.
  - `reveal` - *string | null* - Conditions for when the operation is revealed (may be null for crit ops).
  - `additionalRules` - *string | null* - Additional rules text explaining special mechanics (may be null).
  - `actions` - *string[]* - Array of action IDs that this operation grants access to (may be empty).
  - `victoryPoints` - *string | string[]* - Victory point scoring conditions. May be a single string or an array of strings.
- `actions` - *array* - Array of action objects associated with operations. Each action object follows the same structure as `universal_actions.json`.

### `packs/packs_actions.json`

Mission pack-specific actions. Root object contains an `actions` array. Each action object follows the same structure as `universal_actions.json`:

- `id` - *string* - Action identifier.
- `type` - *string* - Action type: `universal`, `mission`, or `ability`.
- `seq` - *integer* - Ordering for presentation.
- `AP` - *integer* - Action Point cost.
- `name` - *string* - Display name.
- `description` - *string | null* - Markdown-formatted summary (may be null).
- `effects` - *string[]* - Array of effect descriptions, each as a bullet point. May be an empty array for actions that are fully described in the `description` field.
- `conditions` - *string[]* - Array of preconditions or restrictions.
- `packs` - *string[]* - Mission packs where the action is available (optional field, only present when an action is limited to specific killzones or mission packs).

### `rules_key.json`

Key principles and rules glossary. Root object is an array of rule objects. Each rule object contains:

- `id` - *string* - Unique rule identifier.
- `name` - *string* - Display name of the rule.
- `aliases` - *string[]* - Array of alternative names or terms for the rule.
- `category` - *string* - Category classification (e.g., `"key_principle"`).
- `text` - *string* - Markdown-formatted rules text explaining the rule.
- `examples` - *string[]* - Array of example scenarios or use cases (may be empty).
- `tags` - *string[]* - Array of tags for categorization and search.
- `references` - *string[]* - Array of rule IDs that this rule references or relates to.

### `rules_sequence.json`

Game sequence and turn structure. Root object contains:

- `title` - *string* - Display title for the sequence.
- `steps` - *array* - Array of game sequence step objects, each containing:
  - `id` - *integer* - Step number.
  - `icon` - *string* - Icon or emoji representing the step.
  - `name` - *string* - Display name of the step.
  - `description` - *string[]* - Array of description strings explaining what happens in this step.

### `rules_terrain.json`

Terrain rules and mechanics. Root object contains a `rules_terrain` array. Each terrain rule object contains:

- `id` - *string* - Unique terrain rule identifier.
- `name` - *string* - Display name of the terrain rule.
- `aliases` - *string[]* - Array of alternative names or terms.
- `category` - *string* - Category classification (e.g., `"terrain_rule"`).
- `text` - *string* - Markdown-formatted rules text explaining the terrain rule.
- `examples` - *string[]* - Array of example scenarios or use cases (may be empty).
- `actions` - *string[]* - Array of action IDs related to this terrain rule (may be empty).
- `tags` - *string[]* - Array of tags for categorization and search.
- `references` - *string[]* - Array of rule IDs that this rule references or relates to.
- `packs` - *string[]* - Mission packs where this terrain rule applies (may be empty for universal rules).

## Contributing

We welcome contributions to this repository! Here's how you can help:

### Reporting Issues

If you find any errors, inconsistencies, or missing data in the JSON files, please open an issue on GitHub. When reporting:

- Include the file name and relevant section
- Describe the issue clearly
- If possible, reference the official source material (PDFs, rulebooks)
- Suggest the correction if you know what it should be

### Submitting Changes

1. **Fork the repository** to your own GitHub account
2. **Create a branch** for your changes (`git checkout -b fix/description-of-fix`)
3. **Make your changes** to the JSON files
   - Ensure JSON syntax is valid
   - Follow the existing schema structure
   - Maintain consistency with existing data formatting
4. **Test your changes** by validating the JSON files
5. **Commit your changes** with a clear, descriptive message
6. **Push to your fork** and create a pull request

### Guidelines

- **Accuracy**: All data should match official sources and not include homebrew content
- **Schema compliance**: Follow the schema documented in this README
- **Formatting**: Maintain consistent formatting with existing entries
- **Completeness**: When adding new entries, include all required fields
- **Validation**: Ensure all JSON files are valid and parseable

### Code of Conduct

- Be respectful and constructive in all interactions
- Focus on improving the dataset for the community
- Follow the existing patterns and conventions
- Provide clear descriptions in pull requests

Thank you for contributing to the Kill Team JSON dataset!

## Translation

This project supports translation into multiple languages. See [TRANSLATION_GUIDE.md](TRANSLATION_GUIDE.md) for detailed information on:

- Translation approaches and recommendations
- Which fields should be translated
- How to maintain translations
- Tooling for translation validation

**Quick Start for Translators:**

1. Copy the English JSON file structure (e.g., `en/teams/IMP-AOD.json` → `es/teams/IMP-AOD.json`)
2. Translate all user-facing string fields (names, descriptions, etc.)
3. Keep all IDs and structure identical
4. Validate using `python tools/validate_translation.py en/teams/IMP-AOD.json es/teams/IMP-AOD.json`
5. Check completeness using `python tools/check_translation_completeness.py en/teams/IMP-AOD.json es/teams/IMP-AOD.json`

**Translation Tooling:**
All translation tools are located in the `tools/` folder:
- `tools/validate_translation.py` - Validates structure matches English base
- `tools/extract_translatables.py` - Extracts translatable strings for translation services
- `tools/check_translation_completeness.py` - Reports translation progress

See [TRANSLATION_GUIDE.md](TRANSLATION_GUIDE.md) for full details.

