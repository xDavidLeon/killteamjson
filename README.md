# killteamjson
JSON Dataset for Killteam 2024. Forked form [https://github.com/vjosset/killteamjson](https://github.com/vjosset/killteamjson)

See also [KT SERVITOR](https://ktservitor.xdavidleon.com/)

## JSON File Structures

### `teams.json`

Kill team definitions. The root of the file is an array of kill team objects. Each kill team contains:

- `factionId` - *string* - Faction identifier.
- `killteamId` - *string* - Unique kill team identifier.
- `killteamName` - *string* - Display name.
- `description` - *string* - Markdown-formatted lore/flavour text.
- `composition` - *string* - Markdown-formatted roster construction rules.
- `archetypes` - *string* - Slash-delimited list of archetype keywords.
- `userId` - *string | null* - Author identifier when sourced from user submissions.
- `isPublished` - *boolean* - Indicates if the list is live in the source application.
- `isHomebrew` - *boolean* - Flags user-created content.
- `opTypes` - *array* - Operative type definitions for the kill team (see below).
- `ploys` - *array* - Strategy and firefight ploys available to the team.
- `equipments` - *array* - Kill team equipment items (see also `universal_equipment.json`).

#### Operative types (`opTypes`)

Each operative type object provides both profile data and runtime metadata:

- `opTypeId` - *string* - Unique operative type identifier.
- `killteamId` - *string* - Owning kill team ID.
- `seq` - *integer* - Display ordering.
- `opTypeName` - *string* - Name shown on datasheets.
- `MOVE`, `APL`, `SAVE`, `WOUNDS` - *string | number* - Core stat line values.
- `keywords` - *string* - Comma-separated gameplay keywords.
- `basesize` - *integer* - Base diameter in millimetres.
- `nameType` - *string* - Name generation key.
- `isOpType` - *boolean* - Flags entries that represent selectable operative types.
- `isActivated` - *boolean* - Runtime flag used when tracking activations.
- `currWOUNDS` - *integer* - Current wounds tracker; defaults to maximum.
- `opName`, `opType`, `opId` - *string | null* - Additional runtime metadata slots.
- `weapons` - *array* - Weapon entries for the operative (see below).
- `abilities` - *array* - Special rules tied to the operative.
- `options` - *array* - Selectable loadout or tactic options (e.g., chapter tactics).

##### Weapons (`opTypes[].weapons`)

- `wepId` - *string* - Weapon identifier.
- `opTypeId` - *string* - Parent operative type.
- `seq` - *integer* - Display ordering.
- `wepName` - *string* - Weapon name.
- `wepType` - *string* - Weapon category (`R`, `M`, `P`, `E`).
- `isDefault` - *boolean* - Indicates if the weapon is part of the default loadout.
- `profiles` - *array* - Attack profile definitions.

Weapon profiles contain:

- `wepprofileId` - *string* - Profile identifier.
- `wepId` - *string* - Parent weapon identifier.
- `seq` - *integer* - Ordering for multi-profile weapons.
- `profileName` - *string* - Optional profile label.
- `ATK`, `HIT`, `DMG`, `WR` - *string* - Attack characteristics, including comma-delimited weapon rules in `WR`.

##### Abilities (`opTypes[].abilities`)

- `abilityId` - *string* - Unique ability identifier.
- `opTypeId` - *string* - Parent operative type.
- `abilityName` - *string* - Display name.
- `AP` - *integer | null* - Action Point cost; `null` denotes passive abilities.
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

### `mission_actions.json`

Mission-pack specific actions. Root object contains an `actions` array:

- `id` - *string* - Action identifier.
- `type` - *string* - Always `mission` for this dataset.
- `seq` - *integer* - Ordering for presentation.
- `AP` - *integer* - Action Point cost.
- `name` - *string* - Display name.
- `description` - *string | null* - Markdown-formatted summary.
- `effects` - *string[]* - Free-form rules text split into bullet descriptions.
- `conditions` - *string[]* - Preconditions or restrictions (optional for some entries).
- `packs` - *string[]* - Mission packs where the action is available (optional).

### `universal_actions.json`

Core actions available to all kill teams. Root object contains an `actions` array with the same structure as mission actions, except:

- `type` - *string* - Always `universal`.
- `packs` - *string[]* - Only present when an action is limited to specific killzones.

### `universal_equipment.json`

Universal equipment options. Root object contains an `equipments` array:

- `eqId` - *string* - Equipment identifier (shared IDs can also appear in `teams.json`).
- `killteamId` - *string | null* - Kill team ID when restricted, otherwise `null`.
- `seq` - *integer* - Ordering value.
- `eqName` - *string* - Display name.
- `description` - *string* - Markdown-formatted rules text.
- `effects` - *string* - Encoded effect string (may be empty).
- `amount` - *integer* - Quantity of the item granted on selection.

### `weapon_rules.json`

Weapon rule glossary. Root object contains a `weapon_rules` array:

- `id` - *string* - Rule identifier referenced from weapon profiles (`WR` fields).
- `name` - *string* - Display name of the rule.
- `variable` - *boolean* - Indicates whether the rule expects an argument (e.g., `Lethal 5+`).
- `description` - *string* - Detailed rules text.

