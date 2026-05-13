#!/usr/bin/env python3
"""
Build flat Spanish JSON under es/ from English canonical (en/) + Spanish overlays (es/overlays/).

  python scripts/build_es_locale.py build     # write all es/* files
  python scripts/build_es_locale.py verify    # round-trip check vs current es/ (optional)
  python scripts/build_es_locale.py extract   # regenerate overlays from en + legacy flat es (one-off)

KT SERVITOR and other consumers should keep using merged paths:
  es/teams/*.json, es/weapon_rules.json, etc.
Source of truth for Spanish strings: es/overlays/...
Canonical rules data: en/
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping

ROOT = Path(__file__).resolve().parent.parent
EN = ROOT / "en"
ES = ROOT / "es"
OVER = ES / "overlays"

TEAM_TOP_STRINGS = frozenset({"killteamName", "description", "composition"})
PLOY_STRINGS = frozenset({"ployName", "description"})
EQ_STRINGS = frozenset({"eqName", "description", "effects"})
ABILITY_STRINGS = frozenset({"abilityName", "description"})
ACTION_STRINGS = frozenset({"name", "description", "effects", "conditions"})


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def diff_keys(en_o: Mapping[str, Any], es_o: Mapping[str, Any], keys: frozenset) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k in keys:
        if k not in es_o:
            continue
        ev, sv = en_o.get(k), es_o.get(k)
        if ev != sv:
            out[k] = sv
    return out


def merge_weapon_profiles(
    en_profiles: List[MutableMapping[str, Any]], patch_map: Mapping[str, Mapping[str, Any]]
) -> None:
    for pid, patch in patch_map.items():
        if isinstance(pid, str) and pid.startswith("__idx_"):
            idx = int(pid[6:])
            if idx >= len(en_profiles):
                raise IndexError(f"profile index {idx} out of range")
            en_profiles[idx].update(patch)
            continue
        for p in en_profiles:
            if p.get("wepprofileId") == pid:
                p.update(patch)
                break
        else:
            raise KeyError(f"unknown wepprofileId {pid}")


def extract_weapon_profiles(
    en_profiles: List[Mapping[str, Any]], es_profiles: List[Mapping[str, Any]]
) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for i, ep in enumerate(en_profiles):
        if i >= len(es_profiles):
            break
        sp = es_profiles[i]
        pid = ep.get("wepprofileId") or sp.get("wepprofileId")
        key: str = pid if pid else f"__idx_{i}"
        d = diff_keys(ep, sp, frozenset({"profileName"}))
        if d:
            out[key] = d
    return out


def apply_weapons_list(
    weapons: List[MutableMapping[str, Any]], patch_map: Mapping[str, Mapping[str, Any]]
) -> None:
    by_wid = {w["wepId"]: w for w in weapons}
    for wid, patch in patch_map.items():
        if wid not in by_wid:
            raise KeyError(f"unknown wepId {wid}")
        w = by_wid[wid]
        sub = dict(patch)
        profs = sub.pop("profiles", None)
        w.update(sub)
        if profs is not None:
            merge_weapon_profiles(w["profiles"], profs)


def extract_weapons_list(
    en_ws: List[Mapping[str, Any]], es_ws: List[Mapping[str, Any]]
) -> Dict[str, Any]:
    es_by = {w["wepId"]: w for w in es_ws}
    out: Dict[str, Any] = {}
    for w in en_ws:
        wid = w["wepId"]
        if wid not in es_by:
            continue
        sw = es_by[wid]
        patch = diff_keys(w, sw, frozenset({"wepName"}))
        pp = extract_weapon_profiles(w.get("profiles", []), sw.get("profiles", []))
        if pp:
            patch["profiles"] = pp
        if patch:
            out[wid] = patch
    return out


def apply_equipments(
    equipments: List[MutableMapping[str, Any]], patch_map: Mapping[str, Mapping[str, Any]]
) -> None:
    by_id = {e["eqId"]: e for e in equipments}
    for eid, patch in patch_map.items():
        if eid not in by_id:
            raise KeyError(f"unknown eqId {eid}")
        e = by_id[eid]
        sub = dict(patch)
        nested_w = sub.pop("weapons", None)
        e.update(sub)
        if nested_w is not None:
            apply_weapons_list(e["weapons"], nested_w)


def extract_equipments(
    en_eq: List[Mapping[str, Any]], es_eq: List[Mapping[str, Any]]
) -> Dict[str, Any]:
    es_by = {e["eqId"]: e for e in es_eq}
    out: Dict[str, Any] = {}
    for e in en_eq:
        eid = e["eqId"]
        if eid not in es_by:
            continue
        se = es_by[eid]
        patch = diff_keys(e, se, EQ_STRINGS)
        if "weapons" in e and "weapons" in se:
            wpatch = extract_weapons_list(e["weapons"], se["weapons"])
            if wpatch:
                patch["weapons"] = wpatch
        if patch:
            out[eid] = patch
    return out


def apply_actions_list(
    actions: List[MutableMapping[str, Any]], patch_map: Mapping[str, Mapping[str, Any]]
) -> None:
    by_id = {a["id"]: a for a in actions}
    for aid, patch in patch_map.items():
        if aid not in by_id:
            raise KeyError(f"unknown action id {aid}")
        by_id[aid].update(patch)


def extract_actions_list(
    en_a: List[Mapping[str, Any]], es_a: List[Mapping[str, Any]]
) -> Dict[str, Any]:
    es_by = {a["id"]: a for a in es_a}
    out: Dict[str, Any] = {}
    for a in en_a:
        aid = a["id"]
        if aid not in es_by:
            continue
        patch = diff_keys(a, es_by[aid], ACTION_STRINGS)
        if patch:
            out[aid] = patch
    return out


def apply_optype(op: MutableMapping[str, Any], patch: Mapping[str, Any]) -> None:
    sub = dict(patch)
    ab = sub.pop("abilities", None)
    opts = sub.pop("options", None)
    acts = sub.pop("actions", None)
    wep = sub.pop("weapons", None)
    op.update(sub)
    if wep is not None:
        apply_weapons_list(op["weapons"], wep)
    if ab is not None:
        by_aid = {x["abilityId"]: x for x in op["abilities"]}
        for aid, ap in ab.items():
            if aid not in by_aid:
                raise KeyError(f"unknown abilityId {aid}")
            by_aid[aid].update(ap)
    if opts is not None:
        by_oid = {x["optionId"]: x for x in op.get("options", [])}
        for oid, opa in opts.items():
            if oid not in by_oid:
                raise KeyError(f"unknown optionId {oid}")
            by_oid[oid].update(opa)
    if acts is not None:
        apply_actions_list(op["actions"], acts)


def extract_optype(en_o: Mapping[str, Any], es_o: Mapping[str, Any]) -> Dict[str, Any]:
    patch = diff_keys(en_o, es_o, frozenset({"opTypeName"}))
    if en_o.get("weapons") and es_o.get("weapons"):
        w = extract_weapons_list(en_o["weapons"], es_o["weapons"])
        if w:
            patch["weapons"] = w
    if en_o.get("abilities") and es_o.get("abilities"):
        es_ab = {a["abilityId"]: a for a in es_o["abilities"]}
        ab_patch: Dict[str, Any] = {}
        for a in en_o["abilities"]:
            aid = a["abilityId"]
            if aid not in es_ab:
                continue
            d = diff_keys(a, es_ab[aid], ABILITY_STRINGS)
            if d:
                ab_patch[aid] = d
        if ab_patch:
            patch["abilities"] = ab_patch
    if en_o.get("options") and es_o.get("options"):
        es_opt = {o["optionId"]: o for o in es_o["options"]}
        o_patch: Dict[str, Any] = {}
        for o in en_o["options"]:
            oid = o["optionId"]
            if oid not in es_opt:
                continue
            d = diff_keys(o, es_opt[oid], frozenset({"optionName", "description", "effects"}))
            if d:
                o_patch[oid] = d
        if o_patch:
            patch["options"] = o_patch
    if en_o.get("actions") and es_o.get("actions"):
        ap = extract_actions_list(en_o["actions"], es_o["actions"])
        if ap:
            patch["actions"] = ap
    return patch


def apply_team_overlay(canonical: MutableMapping[str, Any], overlay: Mapping[str, Any]) -> None:
    if overlay.get("killteamId") and overlay["killteamId"] != canonical.get("killteamId"):
        raise ValueError("killteamId mismatch in overlay")
    if "team" in overlay:
        for k, v in overlay["team"].items():
            canonical[k] = v
    if "ploys" in overlay:
        pmap = {p["ployId"]: p for p in canonical["ploys"]}
        for pid, p in overlay["ploys"].items():
            if pid not in pmap:
                raise KeyError(f"unknown ployId {pid}")
            pmap[pid].update(p)
    if "equipments" in overlay:
        apply_equipments(canonical["equipments"], overlay["equipments"])
    if "teamAbilities" in overlay:
        tmap = {t["abilityId"]: t for t in canonical.get("teamAbilities", [])}
        for tid, p in overlay["teamAbilities"].items():
            if tid not in tmap:
                raise KeyError(f"unknown team abilityId {tid}")
            tmap[tid].update(p)
    if "opTypes" in overlay:
        omap = {o["opTypeId"]: o for o in canonical["opTypes"]}
        for oid, p in overlay["opTypes"].items():
            if oid not in omap:
                raise KeyError(f"unknown opTypeId {oid}")
            apply_optype(omap[oid], p)


def extract_team_overlay(en_team: Mapping[str, Any], es_team: Mapping[str, Any]) -> Dict[str, Any]:
    kid = en_team["killteamId"]
    if es_team["killteamId"] != kid:
        raise ValueError(f"killteamId mismatch {kid}")
    o: Dict[str, Any] = {"killteamId": kid, "locale": "es"}
    team_patch = diff_keys(en_team, es_team, TEAM_TOP_STRINGS)
    if team_patch:
        o["team"] = team_patch
    ploy_patch: Dict[str, Any] = {}
    es_ploy = {p["ployId"]: p for p in es_team["ploys"]}
    for p in en_team["ploys"]:
        pid = p["ployId"]
        if pid not in es_ploy:
            continue
        d = diff_keys(p, es_ploy[pid], PLOY_STRINGS)
        if d:
            ploy_patch[pid] = d
    if ploy_patch:
        o["ploys"] = ploy_patch
    eqp = extract_equipments(en_team["equipments"], es_team["equipments"])
    if eqp:
        o["equipments"] = eqp
    if en_team.get("teamAbilities") and es_team.get("teamAbilities"):
        es_ta = {t["abilityId"]: t for t in es_team["teamAbilities"]}
        ta_patch: Dict[str, Any] = {}
        for t in en_team["teamAbilities"]:
            tid = t["abilityId"]
            if tid not in es_ta:
                continue
            d = diff_keys(t, es_ta[tid], ABILITY_STRINGS)
            if d:
                ta_patch[tid] = d
        if ta_patch:
            o["teamAbilities"] = ta_patch
    es_op = {x["opTypeId"]: x for x in es_team["opTypes"]}
    op_patch: Dict[str, Any] = {}
    for op in en_team["opTypes"]:
        oid = op["opTypeId"]
        if oid not in es_op:
            continue
        p = extract_optype(op, es_op[oid])
        if p:
            op_patch[oid] = p
    if op_patch:
        o["opTypes"] = op_patch
    return o


def build_team(en_path: Path, over_path: Path) -> dict:
    canonical = load_json(en_path)
    if not over_path.is_file():
        return copy.deepcopy(canonical)
    overlay = load_json(over_path)
    out = copy.deepcopy(canonical)
    apply_team_overlay(out, overlay)
    return out


def merge_id_map_array(
    canonical_list: List[MutableMapping[str, Any]],
    id_key: str,
    patch_map: Mapping[str, Mapping[str, Any]],
) -> None:
    by_id = {x[id_key]: x for x in canonical_list}
    for iid, patch in patch_map.items():
        if iid not in by_id:
            raise KeyError(f"unknown {id_key} {iid}")
        by_id[iid].update(patch)


def build_weapon_rules() -> dict:
    c = load_json(EN / "weapon_rules.json")
    p = OVER / "weapon_rules.json"
    if not p.is_file():
        return c
    o = load_json(p)
    out = copy.deepcopy(c)
    merge_id_map_array(out["weapon_rules"], "id", o["weapon_rules"])
    return out


def extract_weapon_rules(en_doc: dict, es_doc: dict) -> dict:
    es_by = {w["id"]: w for w in es_doc["weapon_rules"]}
    wr: Dict[str, Any] = {}
    for w in en_doc["weapon_rules"]:
        wid = w["id"]
        if wid not in es_by:
            continue
        d = diff_keys(w, es_by[wid], frozenset({"name", "description"}))
        if d:
            wr[wid] = d
    return {"locale": "es", "weapon_rules": wr}


def build_universal_actions() -> dict:
    c = load_json(EN / "universal_actions.json")
    p = OVER / "universal_actions.json"
    if not p.is_file():
        return c
    o = load_json(p)
    out = copy.deepcopy(c)
    merge_id_map_array(out["actions"], "id", o["actions"])
    return out


def extract_universal_actions(en_doc: dict, es_doc: dict) -> dict:
    acts = extract_actions_list(en_doc["actions"], es_doc["actions"])
    return {"locale": "es", "actions": acts}


def build_universal_equipment() -> dict:
    c = load_json(EN / "universal_equipment.json")
    p = OVER / "universal_equipment.json"
    if not p.is_file():
        return c
    o = load_json(p)
    out = copy.deepcopy(c)
    if "equipments" in o:
        merge_id_map_array(out["equipments"], "eqId", o["equipments"])
    if "actions" in o:
        merge_id_map_array(out["actions"], "id", o["actions"])
    return out


def extract_universal_equipment(en_doc: dict, es_doc: dict) -> dict:
    o: Dict[str, Any] = {"locale": "es"}
    eq = extract_equipments(en_doc["equipments"], es_doc["equipments"])
    if eq:
        o["equipments"] = eq
    acts = extract_actions_list(en_doc.get("actions", []), es_doc.get("actions", []))
    if acts:
        o["actions"] = acts
    return o


def build_ops_2025() -> dict:
    c = load_json(EN / "packs" / "ops_2025.json")
    p = OVER / "packs" / "ops_2025.json"
    if not p.is_file():
        return c
    o = load_json(p)
    out = copy.deepcopy(c)
    merge_id_map_array(out["ops"], "id", o["ops"])
    return out


def extract_ops_2025(en_doc: dict, es_doc: dict) -> dict:
    keys = frozenset({"title", "reveal", "additionalRules", "victoryPoints"})
    es_by = {x["id"]: x for x in es_doc["ops"]}
    ops: Dict[str, Any] = {}
    for x in en_doc["ops"]:
        oid = x["id"]
        if oid not in es_by:
            continue
        d = diff_keys(x, es_by[oid], keys)
        if d:
            ops[oid] = d
    return {"locale": "es", "ops": ops}


def build_packs_actions() -> dict:
    c = load_json(EN / "packs" / "packs_actions.json")
    p = OVER / "packs" / "packs_actions.json"
    if not p.is_file():
        return c
    o = load_json(p)
    out = copy.deepcopy(c)
    merge_id_map_array(out["actions"], "id", o["actions"])
    return out


def build_rules_key() -> list:
    c = load_json(EN / "rules_key.json")
    p = OVER / "rules_key.json"
    if not p.is_file():
        return c
    o = load_json(p)
    by_id = {x["id"]: x for x in c}
    for rid, patch in o["entries"].items():
        if rid not in by_id:
            raise KeyError(f"unknown rules_key id {rid}")
        by_id[rid].update(patch)
    return c


def extract_rules_key(en_list: list, es_list: list) -> dict:
    keys = frozenset({"name", "text", "aliases", "examples"})
    es_by = {e["id"]: e for e in es_list}
    entries: Dict[str, Any] = {}
    for e in en_list:
        eid = e["id"]
        if eid not in es_by:
            continue
        d = diff_keys(e, es_by[eid], keys)
        if d:
            entries[eid] = d
    return {"locale": "es", "entries": entries}


def build_rules_sequence() -> dict:
    c = load_json(EN / "rules_sequence.json")
    p = OVER / "rules_sequence.json"
    if not p.is_file():
        return c
    o = load_json(p)
    out = copy.deepcopy(c)
    if "title" in o:
        out["title"] = o["title"]
    if "steps" in o:
        steps_by_id = {s["id"]: s for s in out["steps"]}
        for sid_key, patch in o["steps"].items():
            sid = int(sid_key) if isinstance(sid_key, str) else sid_key
            if sid not in steps_by_id:
                raise KeyError(f"unknown step id {sid_key}")
            steps_by_id[sid].update(patch)
    return out


def extract_rules_sequence(en_doc: dict, es_doc: dict) -> dict:
    o: Dict[str, Any] = {"locale": "es"}
    if en_doc["title"] != es_doc["title"]:
        o["title"] = es_doc["title"]
    es_st = {s["id"]: s for s in es_doc["steps"]}
    steps: Dict[str, Any] = {}
    for s in en_doc["steps"]:
        sid = s["id"]
        if sid not in es_st:
            continue
        ss = es_st[sid]
        p = diff_keys(s, ss, frozenset({"name", "description"}))
        if p:
            steps[str(sid)] = p
    if steps:
        o["steps"] = steps
    return o


def build_rules_terrain() -> dict:
    c = load_json(EN / "rules_terrain.json")
    p = OVER / "rules_terrain.json"
    if not p.is_file():
        return c
    o = load_json(p)
    out = copy.deepcopy(c)
    by_id = {x["id"]: x for x in out["rules_terrain"]}
    for rid, patch in o["rules_terrain"].items():
        if rid not in by_id:
            raise KeyError(f"unknown terrain rule id {rid}")
        by_id[rid].update(patch)
    return out


def extract_rules_terrain(en_doc: dict, es_doc: dict) -> dict:
    keys = frozenset({"name", "text", "aliases", "examples"})
    es_by = {e["id"]: e for e in es_doc["rules_terrain"]}
    tr: Dict[str, Any] = {}
    for e in en_doc["rules_terrain"]:
        eid = e["id"]
        if eid not in es_by:
            continue
        d = diff_keys(e, es_by[eid], keys)
        if d:
            tr[eid] = d
    return {"locale": "es", "rules_terrain": tr}


def stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


def validate_team_overlay_contents(en_team: dict, ov: dict, label: str) -> List[str]:
    errs: List[str] = []
    if ov.get("killteamId") != en_team.get("killteamId"):
        errs.append(f"{label}: killteamId mismatch")
    for pid in ov.get("ploys", {}):
        if not any(p["ployId"] == pid for p in en_team["ploys"]):
            errs.append(f"{label}: unknown ployId {pid}")
    for eid in ov.get("equipments", {}):
        if not any(e["eqId"] == eid for e in en_team["equipments"]):
            errs.append(f"{label}: unknown eqId {eid}")
    for tid in ov.get("teamAbilities", {}):
        if not any(t["abilityId"] == tid for t in en_team.get("teamAbilities", [])):
            errs.append(f"{label}: unknown team abilityId {tid}")
    en_ops = {o["opTypeId"]: o for o in en_team["opTypes"]}
    for oid, opatch in ov.get("opTypes", {}).items():
        if oid not in en_ops:
            errs.append(f"{label}: unknown opTypeId {oid}")
            continue
        eop = en_ops[oid]
        for aid in opatch.get("abilities", {}):
            if not any(a["abilityId"] == aid for a in eop.get("abilities", [])):
                errs.append(f"{label}: unknown abilityId {aid} in {oid}")
        for wid, wpatch in opatch.get("weapons", {}).items():
            ew = next((w for w in eop.get("weapons", []) if w["wepId"] == wid), None)
            if ew is None:
                errs.append(f"{label}: unknown wepId {wid} in {oid}")
                continue
            for prof_key in wpatch.get("profiles", {}):
                if isinstance(prof_key, str) and prof_key.startswith("__idx_"):
                    continue
                if not any(p.get("wepprofileId") == prof_key for p in ew.get("profiles", [])):
                    errs.append(f"{label}: unknown wepprofileId {prof_key} in {wid}")
        for actid in opatch.get("actions", {}):
            if not any(a["id"] == actid for a in eop.get("actions", [])):
                errs.append(f"{label}: unknown action id {actid} in {oid}")
        for optid in opatch.get("options", {}):
            if not any(o.get("optionId") == optid for o in eop.get("options", [])):
                errs.append(f"{label}: unknown optionId {optid} in {oid}")
    return errs


def cmd_validate() -> None:
    """Referential checks + optional JSON Schema (pip install jsonschema)."""
    errs: List[str] = []
    try:
        import jsonschema

        team_schema = load_json(SCHEMA_DIR / "team_overlay.schema.json")
        for p in sorted((OVER / "teams").glob("*.json")):
            try:
                jsonschema.validate(instance=load_json(p), schema=team_schema)
            except jsonschema.ValidationError as e:
                errs.append(f"{p.name}: schema: {e.message}")
    except ImportError:
        pass
    for p in sorted((OVER / "teams").glob("*.json")):
        en = load_json(EN / "teams" / p.name)
        ov = load_json(p)
        errs.extend(validate_team_overlay_contents(en, ov, p.name))
    wr_path = OVER / "weapon_rules.json"
    if wr_path.is_file():
        en_ids = {w["id"] for w in load_json(EN / "weapon_rules.json")["weapon_rules"]}
        for wid in load_json(wr_path).get("weapon_rules", {}):
            if wid not in en_ids:
                errs.append(f"weapon_rules overlay: unknown id {wid}")
    ua_path = OVER / "universal_actions.json"
    if ua_path.is_file():
        en_ids = {a["id"] for a in load_json(EN / "universal_actions.json")["actions"]}
        for aid in load_json(ua_path).get("actions", {}):
            if aid not in en_ids:
                errs.append(f"universal_actions overlay: unknown id {aid}")
    ue_path = OVER / "universal_equipment.json"
    if ue_path.is_file():
        doc = load_json(ue_path)
        en_doc = load_json(EN / "universal_equipment.json")
        if "equipments" in doc:
            eids = {e["eqId"] for e in en_doc["equipments"]}
            for x in doc["equipments"].keys():
                if x not in eids:
                    errs.append(f"universal_equipment overlay: unknown eqId {x}")
        if "actions" in doc:
            aids = {a["id"] for a in en_doc.get("actions", [])}
            for x in doc["actions"].keys():
                if x not in aids:
                    errs.append(f"universal_equipment overlay: unknown action id {x}")
    ops_path = OVER / "packs" / "ops_2025.json"
    if ops_path.is_file():
        en_ids = {o["id"] for o in load_json(EN / "packs" / "ops_2025.json")["ops"]}
        for oid in load_json(ops_path).get("ops", {}):
            if oid not in en_ids:
                errs.append(f"ops_2025 overlay: unknown id {oid}")
    pa_path = OVER / "packs" / "packs_actions.json"
    if pa_path.is_file():
        en_ids = {a["id"] for a in load_json(EN / "packs" / "packs_actions.json")["actions"]}
        for aid in load_json(pa_path).get("actions", {}):
            if aid not in en_ids:
                errs.append(f"packs_actions overlay: unknown id {aid}")
    rk_path = OVER / "rules_key.json"
    if rk_path.is_file():
        en_ids = {e["id"] for e in load_json(EN / "rules_key.json")}
        for rid in load_json(rk_path).get("entries", {}):
            if rid not in en_ids:
                errs.append(f"rules_key overlay: unknown id {rid}")
    rs_path = OVER / "rules_sequence.json"
    if rs_path.is_file():
        en_steps = {s["id"] for s in load_json(EN / "rules_sequence.json")["steps"]}
        for sk in load_json(rs_path).get("steps", {}):
            sid = int(sk) if str(sk).isdigit() else sk
            if sid not in en_steps:
                errs.append(f"rules_sequence overlay: unknown step {sk}")
    rt_path = OVER / "rules_terrain.json"
    if rt_path.is_file():
        en_ids = {e["id"] for e in load_json(EN / "rules_terrain.json")["rules_terrain"]}
        for tid in load_json(rt_path).get("rules_terrain", {}):
            if tid not in en_ids:
                errs.append(f"rules_terrain overlay: unknown id {tid}")
    if errs:
        print("\n".join(errs), file=sys.stderr)
        sys.exit(1)
    print("VALIDATE OK", file=sys.stderr)


def cmd_build() -> None:
    over_teams = OVER / "teams"
    for en_path in sorted((EN / "teams").glob("*.json")):
        name = en_path.name
        built = build_team(en_path, over_teams / name)
        save_json(ES / "teams" / name, built)
    save_json(ES / "weapon_rules.json", build_weapon_rules())
    save_json(ES / "universal_actions.json", build_universal_actions())
    save_json(ES / "universal_equipment.json", build_universal_equipment())
    save_json(ES / "packs" / "ops_2025.json", build_ops_2025())
    save_json(ES / "packs" / "packs_actions.json", build_packs_actions())
    save_json(ES / "rules_key.json", build_rules_key())
    save_json(ES / "rules_sequence.json", build_rules_sequence())
    save_json(ES / "rules_terrain.json", build_rules_terrain())
    print("Wrote merged Spanish files under es/", file=sys.stderr)


def cmd_extract() -> None:
    """Populate es/overlays from current en + es (legacy flat) trees."""
    over_teams = OVER / "teams"
    for en_path in sorted((EN / "teams").glob("*.json")):
        name = en_path.name
        es_path = ES / "teams" / name
        ext = extract_team_overlay(load_json(en_path), load_json(es_path))
        if not [k for k in ext if k not in ("killteamId", "locale")]:
            continue
        save_json(over_teams / name, ext)
    save_json(OVER / "weapon_rules.json", extract_weapon_rules(load_json(EN / "weapon_rules.json"), load_json(ES / "weapon_rules.json")))
    save_json(OVER / "universal_actions.json", extract_universal_actions(load_json(EN / "universal_actions.json"), load_json(ES / "universal_actions.json")))
    save_json(OVER / "universal_equipment.json", extract_universal_equipment(load_json(EN / "universal_equipment.json"), load_json(ES / "universal_equipment.json")))
    (OVER / "packs").mkdir(parents=True, exist_ok=True)
    save_json(OVER / "packs" / "ops_2025.json", extract_ops_2025(load_json(EN / "packs" / "ops_2025.json"), load_json(ES / "packs" / "ops_2025.json")))
    save_json(OVER / "packs" / "packs_actions.json", extract_universal_actions(load_json(EN / "packs" / "packs_actions.json"), load_json(ES / "packs" / "packs_actions.json")))
    rk = extract_rules_key(load_json(EN / "rules_key.json"), load_json(ES / "rules_key.json"))
    save_json(OVER / "rules_key.json", rk)
    rs = extract_rules_sequence(load_json(EN / "rules_sequence.json"), load_json(ES / "rules_sequence.json"))
    if [k for k in rs if k != "locale"]:
        save_json(OVER / "rules_sequence.json", rs)
    elif (OVER / "rules_sequence.json").is_file():
        (OVER / "rules_sequence.json").unlink()
    rt = extract_rules_terrain(load_json(EN / "rules_terrain.json"), load_json(ES / "rules_terrain.json"))
    save_json(OVER / "rules_terrain.json", rt)
    print("Wrote overlays under es/overlays/", file=sys.stderr)


def cmd_verify() -> None:
    errors = []
    for en_path in sorted((EN / "teams").glob("*.json")):
        name = en_path.name
        merged = build_team(en_path, OVER / "teams" / name)
        expected = load_json(ES / "teams" / name)
        if stable_json(merged) != stable_json(expected):
            errors.append(f"teams/{name}")
    checks = [
        ("weapon_rules.json", lambda: stable_json(build_weapon_rules()) == stable_json(load_json(ES / "weapon_rules.json"))),
        ("universal_actions.json", lambda: stable_json(build_universal_actions()) == stable_json(load_json(ES / "universal_actions.json"))),
        ("universal_equipment.json", lambda: stable_json(build_universal_equipment()) == stable_json(load_json(ES / "universal_equipment.json"))),
        ("packs/ops_2025.json", lambda: stable_json(build_ops_2025()) == stable_json(load_json(ES / "packs" / "ops_2025.json"))),
        ("packs/packs_actions.json", lambda: stable_json(build_packs_actions()) == stable_json(load_json(ES / "packs" / "packs_actions.json"))),
        ("rules_key.json", lambda: stable_json(build_rules_key()) == stable_json(load_json(ES / "rules_key.json"))),
        ("rules_sequence.json", lambda: stable_json(build_rules_sequence()) == stable_json(load_json(ES / "rules_sequence.json"))),
        ("rules_terrain.json", lambda: stable_json(build_rules_terrain()) == stable_json(load_json(ES / "rules_terrain.json"))),
    ]
    for label, fn in checks:
        if not fn():
            errors.append(label)
    if errors:
        print("VERIFY FAILED:", ", ".join(errors), file=sys.stderr)
        sys.exit(1)
    print("VERIFY OK", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build or extract Spanish locale overlays")
    ap.add_argument("command", choices=["build", "extract", "verify", "validate"])
    args = ap.parse_args()
    if args.command == "build":
        cmd_build()
    elif args.command == "extract":
        cmd_extract()
    elif args.command == "validate":
        cmd_validate()
    else:
        cmd_verify()


if __name__ == "__main__":
    main()
