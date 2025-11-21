import json
import re
import uuid
import os
from typing import Any, Dict, List, Optional


class TtsScriptGenerator:
    """Generate GMNotes and LuaScript for a card based on card_data and tts_config.

    Rules:
    - Use card_data.tts_config when present; if tts_config.version == 'v2', ignore legacy fields
      like card_data.tts_script and ad-hoc uses parsing.
    - GMNotes are generated for all card types using unified mapping.
    - LuaScript is generated only for Investigators when explicitly enabled.
    """

    _class_mapping = {
        "守护者": "Guardian",
        "探求者": "Seeker",
        "流浪者": "Rogue",
        "潜修者": "Mystic",
        "生存者": "Survivor",
        "中立": "Neutral",
    }

    _type_mapping = {
        "调查员": "Investigator",
        "调查员小卡": "Minicard",
        "支援卡": "Asset",
        "事件卡": "Event",
        "地点卡": "Location",
        # extended types
        "技能卡": "Skill",
        "调查员背面": "InvestigatorBack",
        "定制卡": "UpgradeSheet",
        "故事卡": "Story",
        "诡计卡": "Treachery",
        "敌人卡": "Enemy",
        "密谋卡": "Agenda",
        "密谋卡-大画": "Agenda",
        "场景卡": "Act",
        "场景卡-大画": "Act",
        # Scenario reference card
        "冒险参考卡": "ScenarioReference",
        "玩家卡背": "PlayerCardBack",
        "遭遇卡背": "EncounterCardBack",
    }

    _location_icon_mapping = {
        "绿菱": "diamond",
        "暗红漏斗": "hourglass",
        "橙心": "heart",
        "浅褐水滴": "blob",
        "深紫星": "star",
        "深绿斜二": "equals",
        "深蓝T": "T",
        "紫月": "crescent",
        "红十": "plus",
        "红方": "square.svg",
        "蓝三角": "triangle",
        "褐扭": "wave",
        "青花": "3circles",
        "黄圆": "circle",
        "粉桃": "spades",
    }

    def __init__(self, workspace_manager=None):
        self.workspace_manager = workspace_manager

    def _uuid8(self) -> str:
        return uuid.uuid4().hex[:8].upper()

    def _map_type(self, card_type: str) -> str:
        return self._type_mapping.get(card_type, self._type_mapping.get("支援卡", "Asset"))

    def _map_class(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        return self._class_mapping.get(value, None)

    def _map_icon(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        return self._location_icon_mapping.get(value, value)

    def _join_traits(self, traits: Any) -> Optional[str]:
        if isinstance(traits, list) and traits:
            return ". ".join(traits) + "."
        return None

    def _parse_clues(self, clues: Any) -> Optional[Dict[str, Any]]:
        """Parse clues string like '1<调查员>' or '4' into a uses entry.
        Returns a dict: { count | countPerInvestigator, type: 'Clue', token: 'clue' }
        """
        if not isinstance(clues, str) or not clues:
            return None
        m = re.match(r"^(\d+)(<调查员>)?$", clues)
        if not m:
            return None
        count = int(m.group(1))
        per_investigator = bool(m.group(2))
        entry: Dict[str, Any] = {
            "type": "Clue",
            "token": "clue",
        }
        if per_investigator:
            entry["countPerInvestigator"] = count
        else:
            entry["count"] = count
        return entry

    # ---- Optimization helpers ----
    def _parse_threshold(self, text: Any, investigator_tag: str = "<调查员>") -> Optional[Dict[str, Any]]:
        """Parse a threshold string.
        Rules: pick the first positive integer; if investigator tag present, mark per-investigator.
        Returns: { 'value': int, 'per': bool } or None when not parsable.
        """
        if not isinstance(text, str) or not text.strip():
            return None
        m = re.search(r"(\d+)", text)
        if not m:
            return None
        val = int(m.group(1))
        per = investigator_tag in text
        return {"value": val, "per": per}

    def _parse_modifier(self, desc: Any) -> int:
        """Pick first integer (may be negative) from description for token modifier; default 0."""
        if not isinstance(desc, str):
            return 0
        m = re.search(r"-?\d+", desc)
        return int(m.group(0)) if m else 0

    _SCENARIO_TOKEN_KEYS = (
        ("Skull", "skull"),
        ("Cultist", "cultist"),
        ("Tablet", "tablet"),
        ("Elder Thing", "elder_thing"),
    )

    def _build_scenario_tokens(self, side: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Build tokens object for ScenarioReference side.
        Only generate when scenario_type in (0, 1). Supports nested object 'scenario_card' or flat keys.
        """
        tokens: Dict[str, Dict[str, Any]] = {}
        st = side.get("scenario_type", 0)
        try:
            st_int = int(st)
        except Exception:
            st_int = 0
        if st_int not in (0, 1):
            return tokens

        sc = side.get("scenario_card") if isinstance(side.get("scenario_card"), dict) else None

        def get_value(flat_key: str, nested_key: str) -> Optional[str]:
            v = side.get(flat_key)
            if isinstance(v, str) and v:
                return v
            if sc:
                nv = sc.get(nested_key)
                if isinstance(nv, str) and nv:
                    return nv
            return None

        for label, nk in self._SCENARIO_TOKEN_KEYS:
            txt = get_value(f"scenario_card.{nk}", nk)
            if txt:
                tokens[label] = {"description": txt, "modifier": self._parse_modifier(txt)}
        return tokens

    def _ensure_script_id(self, card: Dict[str, Any]) -> str:
        tts_config = card.get("tts_config") or {}
        # Minicard: if bound to an investigator, use its script id with '-m' suffix
        card_type = str(card.get('type', '')).strip()
        if card_type == '调查员小卡':
            try:
                mini_cfg = tts_config.get('mini') or {}
                bind = mini_cfg.get('bind') or {}
                rel_path = bind.get('path')
                if isinstance(rel_path, str) and rel_path:
                    ref_json = self._read_card_json_by_path(rel_path)
                    base_sid = self.extract_script_id_from_card_json(ref_json) if ref_json else None
                    if base_sid:
                        return f"{base_sid}-m"
            except Exception:
                pass
        # Custom card (UpgradeSheet): if bound to a card, use its script id with '-c' suffix
        if card_type == '定制卡':
            try:
                custom_cfg = tts_config.get('custom') or {}
                bind = custom_cfg.get('bind') or {}
                rel_path = bind.get('path')
                if isinstance(rel_path, str) and rel_path:
                    ref_json = self._read_card_json_by_path(rel_path)
                    base_sid = self.extract_script_id_from_card_json(ref_json) if ref_json else None
                    if base_sid:
                        return f"{base_sid}-c"
            except Exception:
                pass
        # general: use provided script_id when present
        script_id = tts_config.get("script_id")
        if script_id and isinstance(script_id, str):
            return script_id
        # fallback to stable from card id if exists
        base = str(card.get("id", ""))
        if base:
            sid = base.replace("-", "").upper()
            if len(sid) >= 8:
                return sid[:8]
        return self._uuid8()

    def _aggregate_signatures_by_id(self, signatures: List[Dict[str, Any]]) -> List[Dict[str, int]]:
        agg: Dict[str, int] = {}
        for item in signatures or []:
            cid = str(item.get("id", "")).strip()
            count = int(item.get("count", 0) or 0)
            if not cid or count <= 0:
                continue
            agg[cid] = agg.get(cid, 0) + count
        return [agg] if agg else []

    def _read_card_json_by_path(self, rel_path: str) -> Optional[Dict[str, Any]]:
        wm = self.workspace_manager
        if not wm or not isinstance(rel_path, str) or not rel_path:
            return None
        try:
            # best-effort resolve absolute path
            abs_path = None
            if hasattr(wm, '_get_absolute_path'):
                abs_path = wm._get_absolute_path(rel_path)
            else:
                # Fallback: join with workspace_path if available
                base = getattr(wm, 'workspace_path', None)
                if base:
                    abs_path = os.path.join(base, rel_path)
            if not abs_path or not os.path.exists(abs_path):
                return None
            with open(abs_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def _persist_script_id(self, rel_path: str, card_json: Optional[Dict[str, Any]], script_id: str) -> None:
        """将生成的脚本 ID 写回卡牌文件（仅限工作区内）。"""
        wm = self.workspace_manager
        if not wm or not rel_path or not script_id or not card_json:
            return
        try:
            if hasattr(wm, '_is_path_in_workspace') and not wm._is_path_in_workspace(rel_path):
                return
            abs_path = wm._get_absolute_path(rel_path) if hasattr(wm, '_get_absolute_path') else None
            if not abs_path or not os.path.exists(abs_path):
                return
            tcfg = card_json.get('tts_config') if isinstance(card_json.get('tts_config'), dict) else {}
            if tcfg.get('script_id') == script_id and str(tcfg.get('version', '')).lower() == 'v2':
                return
            tcfg = dict(tcfg)
            tcfg['version'] = 'v2'
            tcfg['script_id'] = script_id
            card_json['tts_config'] = tcfg
            if 'tts_script' in card_json:
                del card_json['tts_script']
            with open(abs_path, 'w', encoding='utf-8') as f:
                json.dump(card_json, f, ensure_ascii=False, indent=2)
        except Exception:
            # 写入失败时不影响后续流程
            pass

    def extract_script_id_from_card_json(self, card_json: Dict[str, Any]) -> Optional[str]:
        """Public helper: extract stable script id from a card json.
        Priority: v2 tts_config.script_id -> legacy GMNotes.id -> normalized card.id
        """
        # Prefer v2
        tcfg = card_json.get('tts_config') or {}
        sid = tcfg.get('script_id')
        if isinstance(sid, str) and sid:
            return sid
        # Try GMNotes
        tts_script = card_json.get('tts_script') or {}
        gm = tts_script.get('GMNotes')
        if isinstance(gm, str) and gm:
            try:
                gmj = json.loads(gm)
                if isinstance(gmj, dict) and gmj.get('id'):
                    return str(gmj.get('id'))
            except Exception:
                pass
        # Try card id
        raw = str(card_json.get('id', '')).replace('-', '').upper()
        if raw:
            return raw[:8] if len(raw) >= 8 else raw
        return None

    # Backward-compat alias
    def _extract_script_id_from_card_json(self, card_json: Dict[str, Any]) -> Optional[str]:
        return self.extract_script_id_from_card_json(card_json)

    def _aggregate_signatures_from_paths(self, signatures: List[Dict[str, Any]]) -> List[Dict[str, int]]:
        agg: Dict[str, int] = {}
        for item in signatures or []:
            rel_path = str(item.get('path', '')).strip()
            count = int(item.get('count', 0) or 0)
            if not rel_path or count <= 0:
                continue
            card_json = self._read_card_json_by_path(rel_path)
            if not card_json:
                continue  # skip non-existing files
            sid = self._extract_script_id_from_card_json(card_json)
            if not sid:
                # fallback to uuid8 for this card instance if cannot derive stable id
                sid = self._uuid8()
            # 将生成的 ID 写回卡文件，避免后续随机
            self._persist_script_id(rel_path, card_json, sid)
            agg[sid] = agg.get(sid, 0) + count
        return [agg] if agg else []

    def _compose_uses(self, card: Dict[str, Any], tts_config: Dict[str, Any], is_location: bool,
                      current_side: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        uses: List[Dict[str, Any]] = []
        version = (tts_config.get("version") or "").lower()

        # Location-specific: clues from current side
        if is_location and current_side is not None:
            clue_entry = self._parse_clues(current_side.get("clues"))
            if clue_entry and (current_side.get("location_type") == "已揭示"):
                uses.append(clue_entry)

        # Entry tokens (v2)
        entry_tokens = tts_config.get("entryTokens")
        if isinstance(entry_tokens, list):
            uses.extend([et for et in entry_tokens if isinstance(et, dict)])
        elif version != "v2":
            # legacy fallback: from top-level uses
            legacy_uses = card.get("uses")
            if isinstance(legacy_uses, list):
                uses.extend([u for u in legacy_uses if isinstance(u, dict)])
        return uses

    # ---------------- GMNotes ----------------
    def generate_gmnotes(self, card: Dict[str, Any]) -> str:
        card_type = str(card.get("type", "")).strip()
        tts_config = card.get("tts_config") or {}
        script_id = self._ensure_script_id(card)

        # base fields common for all
        current = card
        mapped_type = self._map_type(card_type)
        base_data: Dict[str, Any] = {
            "id": script_id,
            "type": mapped_type,
        }
        traits_joined = self._join_traits(current.get("traits"))
        if traits_joined:
            base_data["traits"] = traits_joined
        mapped_class = self._map_class(current.get("class"))
        if mapped_class:
            base_data["class"] = mapped_class
        # 固定三类遭遇卡的 class 为 Mythos
        if mapped_type in ("Act", "Agenda", "ScenarioReference"):
            base_data["class"] = "Mythos"
        for key in ("level", "cost", "victory"):
            if key in current and current.get(key) is not None:
                if key in ['level', 'cost'] and current.get(key) < 0:
                    continue
                base_data[key] = current.get(key)

        # Game start flags
        game_start = tts_config.get("gameStart") or {}
        if game_start.get("startsInPlay"):
            base_data["startsInPlay"] = True
        if game_start.get("startsInHand"):
            base_data["startsInHand"] = True

        # Unified entry tokens for non-location cards
        if mapped_type != "Location":
            uses = self._compose_uses(card, tts_config, is_location=False)
            if uses:
                base_data["uses"] = uses

        gm: Dict[str, Any] = {}

        # Advanced types
        if mapped_type == "Investigator":
            inv = tts_config.get("investigator") or {}
            gm = {
                **base_data,
                "type": "Investigator",
                "willpowerIcons": int(inv.get("willpowerIcons", 3)),
                "intellectIcons": int(inv.get("intellectIcons", 3)),
                "combatIcons": int(inv.get("combatIcons", 2)),
                "agilityIcons": int(inv.get("agilityIcons", 2)),
                "extraToken": "|".join(inv.get("extraToken", [])) if inv.get("extraToken") else "None",
            }
            # v2: signatures use file relative paths; convert to ID map for GMNotes
            sig_entries = tts_config.get("signatures") or []
            if sig_entries and isinstance(sig_entries, list):
                # accept both legacy id-form and new path-form
                if sig_entries and 'path' in sig_entries[0]:
                    sigs = self._aggregate_signatures_from_paths(sig_entries)
                else:
                    sigs = self._aggregate_signatures_by_id(sig_entries)
            else:
                sigs = []
            if sigs:
                gm["signatures"] = sigs

        elif mapped_type in ("Asset", "Event"):
            gm = {
                **base_data,
            }
            # Pass through some fields if exist on card
            for k in ("slot", "willpowerIcons", "intellectIcons", "combatIcons", "agilityIcons"):
                if card.get(k) is not None:
                    gm[k] = card.get(k)

        elif mapped_type == "Location":
            # Build location data for front/back
            cfg_location = tts_config.get("location") if isinstance(tts_config.get("location"), dict) else None
            cfg_location_front = tts_config.get("locationFront") if isinstance(tts_config.get("locationFront"), dict) else None
            cfg_location_back = tts_config.get("locationBack") if isinstance(tts_config.get("locationBack"), dict) else None

            def _cfg_icons_and_conns(cfg: Optional[Dict[str, Any]]) -> (Optional[str], Optional[str]):
                icons_str: Optional[str] = None
                conns_str: Optional[str] = None
                if cfg:
                    icons = cfg.get("icons")
                    if isinstance(icons, list) and icons:
                        mapped = [self._map_icon(x) or x for x in icons]
                        icons_str = "|".join([str(x) for x in mapped if x]) if mapped else None
                    elif isinstance(icons, str) and icons:
                        mapped1 = self._map_icon(icons) or icons
                        icons_str = str(mapped1)
                    conns = cfg.get("connections")
                    if isinstance(conns, list) and conns:
                        mappedc = [self._map_icon(x) or x for x in conns]
                        conns_str = "|".join([str(x) for x in mappedc if x]) if mappedc else None
                return icons_str, conns_str

            def make_location(side: Dict[str, Any], cfg: Optional[Dict[str, Any]]) -> Dict[str, Any]:
                cfg_icons, cfg_conns = _cfg_icons_and_conns(cfg)
                loc: Dict[str, Any] = {
                    # 优先使用 tts_config.locationFront/locationBack（高级模式），其次使用 legacy tts_config.location，最后回退卡面字段
                    "icons": cfg_icons or (_cfg_icons_and_conns(cfg_location)[0]) or (self._map_icon(side.get("location_icon")) or side.get("location_icon") or "Diamond"),
                    "connections": cfg_conns or (_cfg_icons_and_conns(cfg_location)[1]) or "|".join([
                        self._map_icon(x) or x for x in (side.get("location_link") or [])
                    ]),
                }
                if side.get("victory") is not None:
                    loc["victory"] = side.get("victory")
                uses = self._compose_uses(card, tts_config, is_location=True, current_side=side)
                if uses:
                    loc["uses"] = uses
                return loc

            front = card
            back = card.get("back") if isinstance(card.get("back"), dict) else None
            front_is_loc = front.get("type") == "地点卡"
            back_is_loc = bool(back and back.get("type") == "地点卡")

            gm = {
                "id": script_id,
                "type": "Location",
                "traits": self._join_traits(front.get("traits")) or "",
            }
            if front_is_loc:
                gm["locationFront"] = make_location(front, cfg_location_front)
            if back_is_loc:
                gm["locationBack"] = make_location(back, cfg_location_back)
            if not (front_is_loc or back_is_loc):
                # single-face location-ish fallback（使用正面配置/legacy配置）
                gm = {**base_data, "location": make_location(front, cfg_location_front or cfg_location)}

        elif mapped_type == "Act":
            # 场景卡：解析线索阈值（front 侧）
            gm = {**base_data, "type": "Act"}
            parsed = self._parse_threshold(card.get("threshold"))
            if parsed:
                if parsed["per"]:
                    gm["clueThresholdPerInvestigator"] = parsed["value"]
                else:
                    gm["clueThreshold"] = parsed["value"]

        elif mapped_type == "Agenda":
            # 密谋卡：解析毁灭阈值（front 侧）
            gm = {**base_data, "type": "Agenda"}
            parsed = self._parse_threshold(card.get("threshold"))
            if parsed:
                if parsed["per"]:
                    gm["doomThresholdPerInvestigator"] = parsed["value"]
                else:
                    gm["doomThreshold"] = parsed["value"]

        elif mapped_type == "ScenarioReference":
            # 冒险参考卡：根据 scenario_type 生成 tokens（0/1 才生成），front/back 均检测
            gm = {**base_data, "type": "ScenarioReference"}
            tokens_obj: Dict[str, Any] = {}
            front_tokens = self._build_scenario_tokens(card)
            if front_tokens:
                tokens_obj["front"] = front_tokens
            back = card.get("back") if isinstance(card.get("back"), dict) else None
            if back and back.get("type") == "冒险参考卡":
                back_tokens = self._build_scenario_tokens(back)
                if back_tokens:
                    tokens_obj["back"] = back_tokens
            if tokens_obj:
                gm["tokens"] = tokens_obj

        else:
            gm = base_data

        try:
            return json.dumps(gm, ensure_ascii=False, indent=2)
        except Exception:
            return "// JSON generation failed"

    # ---------------- LuaScript ----------------
    def _generate_button_params(self, config: Dict[str, Any]) -> str:
        buttons = config.get("buttons") or []
        labels = ", ".join([f'"{btn.get("label", "w")}"' for btn in buttons])
        ids = ", ".join([f'"{btn.get("id", f"Button{i + 1}")}"' for i, btn in enumerate(buttons)])
        colors = ",\n    ".join([f'"{btn.get("color", "#ffffff")}"' for btn in buttons])
        return (
            "local buttonParams      = {\n"
            f"  buttonLabels = {{ {labels} }}, -- reaction symbols\n"
            f"  buttonIds    = {{ {ids} }},\n"
            "  buttonColors = {\n"
            f"    {colors}\n"
            "  }\n"
            "}"
        )

    def _lua_base_script(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, 'templates', 'phase_buttons.lua')
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    # ------ Seal template helpers ------
    def _seal_base_script(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, 'templates', 'seal.lua')
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    _ALLOWED_CHAOS_TOKENS = [
        'Elder Sign', '+1', '0', '-1', '-2', '-3', '-4', '-5', '-6', '-7', '-8',
        'Skull', 'Cultist', 'Tablet', 'Elder Thing', 'Auto-fail', 'Bless', 'Curse', 'Frost'
    ]

    def _generate_seal_lua(self, seal_cfg: Dict[str, Any], language: Optional[str]) -> str:
        base = self._seal_base_script()

        enabled = bool(seal_cfg.get('enabled'))
        if not enabled:
            return ''

        all_tokens = bool(seal_cfg.get('allTokens'))
        tokens = seal_cfg.get('tokens') or []
        max_count = seal_cfg.get('max')

        # sanitize tokens
        allowed = set(self._ALLOWED_CHAOS_TOKENS)
        filtered = [t for t in tokens if isinstance(t, str) and t in allowed]

        # VALID_TOKENS
        if all_tokens:
            valid_tokens_lua = 'VALID_TOKENS = {}'
            invalid_tokens_lua = 'INVALID_TOKENS = {}'
            update_on_hover_lua = 'UPDATE_ON_HOVER = true'
        else:
            if not filtered:
                # nothing selected -> default to allow-all
                valid_tokens_lua = 'VALID_TOKENS = {}'
                invalid_tokens_lua = 'INVALID_TOKENS = {}'
                update_on_hover_lua = 'UPDATE_ON_HOVER = true'
            else:
                entries = ',\n  '.join([f'["{name}"] = true' for name in filtered])
                valid_tokens_lua = f'VALID_TOKENS = {{\n  {entries}\n}}'
                invalid_tokens_lua = 'INVALID_TOKENS = nil'
                update_on_hover_lua = 'UPDATE_ON_HOVER = true'

        # MAX_SEALED
        max_lua = ''
        try:
            m = int(max_count) if max_count is not None else 0
            if m > 0:
                max_lua = f'MAX_SEALED = {m}'
        except Exception:
            pass

        # i18n for menu labels based on language
        lang = (language or '').lower()
        is_zh = lang in ('zh', 'zh-cht')
        if is_zh:
            menu_release_one = 'local MENU_RELEASE_ONE = "释放一个标记"'
            menu_release_one_prefix = 'local MENU_RELEASE_ONE_PREFIX = "释放 "'
            menu_release_all = 'local MENU_RELEASE_ALL = "释放所有标记"'
            menu_release_multi_prefix = 'local MENU_RELEASE_MULTI_PREFIX = "释放 "'
            menu_return_multi_prefix = 'local MENU_RETURN_MULTI_PREFIX = "归还 "'
            menu_token_suffix = 'local MENU_TOKEN_SUFFIX = " 个标记"'
            menu_return_all = 'local MENU_RETURN_ALL = "归还所有标记"'
            menu_resolve_prefix = 'local MENU_RESOLVE_PREFIX = "结算 "'
            menu_resolve_one = 'local MENU_RESOLVE_ONE = "结算一个标记"'
            menu_resolve_one_prefix = 'local MENU_RESOLVE_ONE_PREFIX = "结算 "'
            menu_seal_prefix = 'local MENU_SEAL_PREFIX = "封印 "'
            menu_seal_multi_prefix = 'local MENU_SEAL_MULTI_PREFIX = "封印 "'
            menu_seal_multi_infix = 'local MENU_SEAL_MULTI_INFIX = " 个 "'
            token_display = (
                'local TOKEN_NAME_MAP = {\n'
                '  ["Elder Sign"] = "旧印",\n'
                '  ["Auto-fail"] = "自动失败",\n'
                '  ["Skull"] = "骷髅",\n'
                '  ["Cultist"] = "异教徒",\n'
                '  ["Tablet"] = "石板",\n'
                '  ["Elder Thing"] = "古神",\n'
                '  ["Bless"] = "祝福",\n'
                '  ["Curse"] = "诅咒",\n'
                '  ["Frost"] = "寒霜",\n'
                '}\n'
                'local function TOKEN_DISPLAY(name) return TOKEN_NAME_MAP[name] or name end\n'
                'local function TOKEN_DISPLAY_OR_DEFAULT(name, default) return (name and TOKEN_DISPLAY(name)) or default end'
            )
            generic_token_label = 'local GENERIC_TOKEN_LABEL = "标记"'
        else:
            menu_release_one = 'local MENU_RELEASE_ONE = "Release one token"'
            menu_release_one_prefix = 'local MENU_RELEASE_ONE_PREFIX = "Release "'
            menu_release_all = 'local MENU_RELEASE_ALL = "Release all tokens"'
            menu_release_multi_prefix = 'local MENU_RELEASE_MULTI_PREFIX = "Release "'
            menu_return_multi_prefix = 'local MENU_RETURN_MULTI_PREFIX = "Return "'
            menu_token_suffix = 'local MENU_TOKEN_SUFFIX = " token(s)"'
            menu_return_all = 'local MENU_RETURN_ALL = "Return all tokens"'
            menu_resolve_prefix = 'local MENU_RESOLVE_PREFIX = "Resolve "'
            menu_resolve_one = 'local MENU_RESOLVE_ONE = "Resolve one token"'
            menu_resolve_one_prefix = 'local MENU_RESOLVE_ONE_PREFIX = "Resolve "'
            menu_seal_prefix = 'local MENU_SEAL_PREFIX = "Seal "'
            menu_seal_multi_prefix = 'local MENU_SEAL_MULTI_PREFIX = "Seal "'
            menu_seal_multi_infix = 'local MENU_SEAL_MULTI_INFIX = " "'
            token_display = 'local function TOKEN_DISPLAY(name) return name end\nlocal function TOKEN_DISPLAY_OR_DEFAULT(name, default) return (name and TOKEN_DISPLAY(name)) or default end'
            generic_token_label = 'local GENERIC_TOKEN_LABEL = "token"'

        script = base.replace('-- VALID_TOKENS_PLACEHOLDER --', valid_tokens_lua)
        script = script.replace('-- INVALID_TOKENS_PLACEHOLDER --', invalid_tokens_lua)
        script = script.replace('-- UPDATE_ON_HOVER_PLACEHOLDER --', update_on_hover_lua)
        script = script.replace('-- MAX_SEALED_PLACEHOLDER --', max_lua)
        script = script.replace('-- TOKEN_DISPLAY_FUNC_PLACEHOLDER --', token_display)
        script = script.replace('-- TOKEN_DISPLAY_OR_DEFAULT_FUNC_PLACEHOLDER --', '')
        script = script.replace('-- GENERIC_TOKEN_LABEL_PLACEHOLDER --', generic_token_label)
        script = script.replace('-- MENU_RELEASE_ONE_PREFIX_PLACEHOLDER --', menu_release_one_prefix)
        script = script.replace('-- MENU_RESOLVE_ONE_PREFIX_PLACEHOLDER --', menu_resolve_one_prefix)
        script = script.replace('-- MENU_RELEASE_ONE_PLACEHOLDER --', menu_release_one)
        script = script.replace('-- MENU_RESOLVE_ONE_PLACEHOLDER --', menu_resolve_one)
        script = script.replace('-- MENU_RELEASE_ALL_PLACEHOLDER --', menu_release_all)
        script = script.replace('-- MENU_RELEASE_MULTI_PREFIX_PLACEHOLDER --', menu_release_multi_prefix)
        script = script.replace('-- MENU_RETURN_MULTI_PREFIX_PLACEHOLDER --', menu_return_multi_prefix)
        script = script.replace('-- MENU_TOKEN_SUFFIX_PLACEHOLDER --', menu_token_suffix)
        script = script.replace('-- MENU_RETURN_ALL_PLACEHOLDER --', menu_return_all)
        script = script.replace('-- MENU_RESOLVE_PREFIX_PLACEHOLDER --', menu_resolve_prefix)
        script = script.replace('-- MENU_SEAL_PREFIX_PLACEHOLDER --', menu_seal_prefix)
        script = script.replace('-- MENU_SEAL_MULTI_PREFIX_PLACEHOLDER --', menu_seal_multi_prefix)
        script = script.replace('-- MENU_SEAL_MULTI_INFIX_PLACEHOLDER --', menu_seal_multi_infix)
        # Always enable resolve menu
        script = script.replace('-- RESOLVE_TOKEN_PLACEHOLDER --', 'RESOLVE_TOKEN = true')
        return script

    def generate_lua(self, card: Dict[str, Any]) -> str:
        card_type = str(card.get("type", "")).strip()
        tts_config = card.get("tts_config") or {}

        # 优先：升级表自定义脚本（Power Word 等）
        upgrade = tts_config.get("upgrade") or {}
        coords = upgrade.get("coordinates")
        if isinstance(coords, list) and coords:
            return self._generate_upgrade_lua(coords)

        # 封印脚本：除调查员与定制卡外可用
        seal_cfg = tts_config.get('seal') or {}
        if seal_cfg.get('enabled') and self._map_type(card_type) not in ("Investigator", "UpgradeSheet"):
            return self._generate_seal_lua(seal_cfg, card.get('language'))

        # 其次：调查员阶段按钮脚本
        if self._map_type(card_type) != "Investigator":
            return ""
        if not tts_config.get("enablePhaseButtons"):
            return ""
        config = tts_config.get("phaseButtonConfig") or {}
        buttons = config.get("buttons") or []
        if not buttons:
            buttons = [
                {"id": "Mythos", "label": "u", "color": "#ffffff"},
                {"id": "Investigation", "label": "u", "color": "#ff7800"},
                {"id": "Enemy", "label": "u", "color": "#e011ff"},
                {"id": "Upkeep", "label": "u", "color": "#ffe400"},
            ]
            config = {"buttons": buttons}

        base = self._lua_base_script()
        button_params = self._generate_button_params(config)
        button_id_index_map = ",\n".join([f"  {btn.get('id')} = {i + 1}" for i, btn in enumerate(buttons)])
        script = base.replace("-- BUTTON_PARAMS_PLACEHOLDER --", button_params)
        script = script.replace("<!-- BUTTON_ID_INDEX_PLACEHOLDER -->", button_id_index_map)
        script = script.replace("<!-- BUTTON_COUNT -->", str(len(buttons)))
        return script

    def _upgrade_base_script(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, 'templates', 'upgrade_sheet.lua')
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _generate_upgrade_lua(self, coordinates: List[List[float]]) -> str:
        # 1) 按 y 分组并排序
        row_map: Dict[float, List[float]] = {}
        for pt in coordinates:
            if not isinstance(pt, (list, tuple)) or len(pt) < 2:
                continue
            x, y = float(pt[0]), float(pt[1])
            row_map.setdefault(y, []).append(x)
        sorted_rows = sorted([(y, sorted(xs)) for y, xs in row_map.items()], key=lambda t: t[0])
        if not sorted_rows:
            return ""

        # 2) 计算变换参数（参考前端 CALIBRATION_DATA）
        # 参考像素坐标
        ref_px1 = (68.0, 206.0)
        ref_px2 = (89.0, 580.0)
        # 参考逻辑坐标
        ref_lx1, ref_lz1 = (-0.933 + 1 * 0.069, -0.905)  # (-0.864, -0.905)
        ref_lx2, ref_lz2 = (-0.933 + 2 * 0.069, 0.18)  # (-0.795, 0.18)

        scale_x = (ref_px2[0] - ref_px1[0]) / (ref_lx2 - ref_lx1)
        scale_y = (ref_px2[1] - ref_px1[1]) / (ref_lz2 - ref_lz1)
        offset_x = ref_px1[0] - scale_x * ref_lx1
        offset_y = ref_px1[1] - scale_y * ref_lz1

        # 3) 计算 xOffset（像素间距→逻辑间距）
        pixel_x_offset = 40.0
        for _, xs in sorted_rows:
            if len(xs) > 1:
                pixel_x_offset = xs[1] - xs[0]
                break
        logic_x_offset = pixel_x_offset / 350.287211740

        # 4) 计算 xInitial
        first_pixel_x = sorted_rows[0][1][0]
        first_logic_x = (first_pixel_x - offset_x) / scale_x
        x_initial = first_logic_x - logic_x_offset

        # 5) 生成 customizations 表
        def pos_z(y_pixel: float) -> float:
            return (y_pixel - offset_y) / scale_y

        custom_rows: List[str] = []
        for idx, (y, xs) in enumerate(sorted_rows, start=1):
            count = len(xs)
            pz = pos_z(y)
            entry = (
                f"  [{idx}] = {{\n"
                f"    checkboxes = {{\n"
                f"      posZ = {pz:.4f},\n"
                f"      count = {count},\n"
                f"    }}\n"
                f"  }}"
            )
            custom_rows.append(entry)
        customizations = "customizations = {\n" + ",\n".join(custom_rows) + "\n}"

        # 6) 替换模板占位符
        base = self._upgrade_base_script()
        script = base
        # Prefer replacing TS-style template placeholders first (keeps template identical to frontend)
        script = script.replace("${xInitial.toFixed(4)}", f"{x_initial:.4f}")
        script = script.replace("${xOffset.toFixed(4)}", f"{logic_x_offset:.4f}")
        script = script.replace("${customizations}", customizations)
        # Fallback to internal placeholders if present
        script = script.replace("<!-- X_INITIAL -->", f"{x_initial:.4f}")
        script = script.replace("<!-- X_OFFSET -->", f"{logic_x_offset:.4f}")
        script = script.replace("-- CUSTOMIZATIONS_PLACEHOLDER --", customizations)
        return script

    def generate(self, card_data: Dict[str, Any]) -> Dict[str, str]:
        """Unified entry for TTS script generation.
        - If tts_config.version != 'v2': return legacy fields from card_data.tts_script directly.
        - Else generate from v2 config.
        """
        tts_config = card_data.get("tts_config") or {}
        version = str(tts_config.get("version", "")).lower()
        if version != "v2":
            legacy = card_data.get("tts_script") or {}
            return {
                "GMNotes": legacy.get("GMNotes", ""),
                "LuaScript": legacy.get("LuaScript", ""),
            }

        gm = self.generate_gmnotes(card_data)
        lua = self.generate_lua(card_data)
        return {"GMNotes": gm, "LuaScript": lua}
