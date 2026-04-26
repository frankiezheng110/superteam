"""Lightweight markdown/json parsers for SuperTeam artifacts.

No heavy deps; regex + line splits. Each parser returns structured data that
downstream validators and checkers consume.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------- generic helpers ----------

def read_text(path: Path | str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def has_section(text: str, heading_regex: str) -> bool:
    return bool(re.search(rf"(?m)^#{{1,6}}\s*{heading_regex}", text, re.IGNORECASE))


def extract_section(text: str, heading_regex: str) -> str:
    """Return the section body (until next heading of same-or-lower depth)."""
    # Wrap heading_regex so '|' alternations only affect the heading match
    m = re.search(
        rf"(?ms)^(?P<h>#{{1,6}})\s*(?:{heading_regex}).*?\n(?P<body>.*?)(?=^#{{1,6}}\s|\Z)",
        text,
        re.IGNORECASE,
    )
    if not m:
        return ""
    body = m.group("body")
    return (body or "").strip()


# ---------- activity-trace parsing ----------

AGENT_ENTRY_LOG_RE = re.compile(
    r"(?m)^##\s+(?P<agent>[\w\-]+)\s+Entry\s*[—\-]\s*Gate\s+(?P<gate>\d+)"
)
INSPECTOR_CHECKPOINT_RE = re.compile(
    r"(?m)^##\s+Inspector\s+Checkpoint\s*:\s*(?P<stage>\w+)", re.IGNORECASE
)
GATE_DECISION_RE = re.compile(
    r"(?m)^##\s+Gate\s+(?P<gate>\d+)\s+(Decision|Check)\b", re.IGNORECASE
)
USER_APPROVAL_RE = re.compile(
    r"(?im)approved_by\s*:\s*user\b|G[123]\s*(approved|closed)\s*by\s+user\b|用户[已]?(批准|确认|同意)\s*G[123]"
)


def list_agent_entries(trace_text: str) -> list[tuple[str, int]]:
    return [(m.group("agent").lower(), int(m.group("gate"))) for m in AGENT_ENTRY_LOG_RE.finditer(trace_text)]


def extract_entry_log_section(trace_text: str, agent: str, gate: int) -> str:
    """Return the body text of a specific agent's Entry Log section (up to next ## heading)."""
    pattern = rf"(?ms)^##\s+{re.escape(agent)}\s+Entry\s*[—\-]\s*Gate\s+{gate}\b.*?\n(?P<body>.*?)(?=^##\s|\Z)"
    m = re.search(pattern, trace_text, re.IGNORECASE)
    return (m.group("body") if m else "").strip()


_ARTIFACT_LINE_RE = re.compile(
    r"(?mi)^\s*[-*]\s+(?P<name>[\w\-.]+\.[\w]+)\s*:\s*(?P<path>\S.+?)\s*$"
)


def parse_entry_log_artifacts(section_text: str) -> list[tuple[str, str]]:
    """Return [(artifact_name, path)] from the Entry Log's Key artifacts list."""
    return [(m.group("name"), m.group("path")) for m in _ARTIFACT_LINE_RE.finditer(section_text)]


_MUST_HEADER_RE = re.compile(
    r"(?im)^(?:MUST\s+items|.*MUST.*items\s+I\s+will\s+work\s+from)\s*:?\s*$"
)


def parse_entry_log_must_items(section_text: str) -> list[str]:
    """Return MUST item texts listed under 'MUST items I will work from' (or equivalent)."""
    lines = section_text.splitlines()
    items: list[str] = []
    in_must = False
    for line in lines:
        if _MUST_HEADER_RE.match(line):
            in_must = True
            continue
        if in_must:
            stripped = line.strip()
            if not stripped:
                # blank line may or may not terminate; allow one blank then stop
                if items:
                    break
                continue
            m = re.match(r"^[-*]\s+(.+)$", stripped)
            if m:
                items.append(m.group(1).strip())
            elif re.match(r"^[A-Z][\w\s]+:", stripped):
                # next labeled field starts, end of MUST list
                break
    return items


def normalize_must_item(item: str) -> str:
    """Normalize a MUST item string for comparison (strip MUST prefix / quotes / trailing punct)."""
    s = item.strip()
    s = re.sub(r"(?i)^(must\s*[:\-]\s*|\[must\]\s*)", "", s)
    s = s.strip().strip("。.,，;；")
    return s.lower()


# ---------- orchestrator decision log parsing ----------

ORCH_DECISION_RE = re.compile(
    r"(?ms)^##\s+Orchestrator\s+Decision\s*[—\-]\s*(?P<unit>.+?)\n(?P<body>.*?)(?=^##\s|\Z)"
)
UNIT_ID_RE = re.compile(r"(?im)^\s*Unit\s+id\s*:\s*(?P<id>\S+)")


def parse_orchestrator_decisions(trace_text: str) -> list[tuple[str, str, str]]:
    """Return [(header_unit, unit_id, body)] for each Orchestrator Decision section."""
    out: list[tuple[str, str, str]] = []
    for m in ORCH_DECISION_RE.finditer(trace_text):
        header = m.group("unit").strip()
        body = m.group("body")
        uid_m = UNIT_ID_RE.search(body)
        unit_id = uid_m.group("id").strip() if uid_m else header.split()[0]
        out.append((header, unit_id, body))
    return out


# Extract checkpoint IDs referenced in plan.md (e.g. "C00", "C01" ... "C15") or Task IDs
_CHECKPOINT_ID_RE = re.compile(r"\b(?P<id>C\d{2,3})\b")
_TASK_ID_RE = re.compile(r"\b(?P<id>T\d+[A-Z.\d]*)\b")
_FEATURE_ID_RE = re.compile(r"\b(?P<id>F-\d{3,})\b")


def extract_plan_unit_ids(plan_text: str) -> list[str]:
    """Return ordered list of checkpoint / task / feature IDs declared in plan.md (dedup, keep order)."""
    ids: list[str] = []
    seen: set[str] = set()
    for regex in (_CHECKPOINT_ID_RE, _TASK_ID_RE, _FEATURE_ID_RE):
        for m in regex.finditer(plan_text):
            uid = m.group("id")
            if uid not in seen:
                seen.add(uid)
                ids.append(uid)
    return ids


def extract_completed_unit_ids(execution_text: str) -> list[str]:
    """Return unit IDs marked COMPLETE in execution.md.

    Matches heading-adjacent status: finds "## Feature/Task/Checkpoint <ID>" followed by
    "Status: COMPLETE" within the same section.
    """
    completed: list[str] = []
    # Any section starting with "## Feature/Task/Checkpoint ... <ID>..."
    section_re = re.compile(
        r"(?ms)^##\s+(?:Feature|Task|Checkpoint)\s*[:\-]?\s*(?P<id>[\w\-.]+).*?(?=^##\s|\Z)"
    )
    for m in section_re.finditer(execution_text):
        body = m.group(0)
        if re.search(r"(?im)^\s*Status\s*:\s*COMPLETE\b", body):
            uid = m.group("id")
            completed.append(uid)
    return completed


def list_inspector_checkpoints(trace_text: str) -> list[str]:
    return [m.group("stage").lower() for m in INSPECTOR_CHECKPOINT_RE.finditer(trace_text)]


def list_gate_decisions(trace_text: str) -> list[int]:
    return [int(m.group("gate")) for m in GATE_DECISION_RE.finditer(trace_text)]


def has_user_approval(trace_text: str) -> bool:
    """True only if text contains a non-AI-self-signed approval pattern."""
    return bool(USER_APPROVAL_RE.search(trace_text))


# ---------- plan.md parsing ----------

PLAN_TASK_RE = re.compile(r"(?m)^##\s+(?:Task|任务)\s+[\w\-.]+")
PLAN_MUST_RE = re.compile(r"(?mi)^[\s\-*]*\[?\s*MUST\s*\]?\s*[:\-]?\s*(?P<item>.+)$")
PLAN_DEFERRED_RE = re.compile(r"(?mi)^[\s\-*]*\[?\s*DEFERRED\s*\]?\s*[:\-]?\s*(?P<item>.+)$")

# MUST item with explicit [CATEGORY-ID] or [ID] prefix (A5.4 multi-category must)
PLAN_MUST_IDENTIFIED_RE = re.compile(
    r"(?mi)^[\s\-*]*\[?\s*MUST\s*\]?\s*[:\-]?\s*\[(?P<id>[A-Za-z][\w\-]{1,40})\]\s*(?P<desc>.+?)$"
)

# Category heading marker within Delivery Scope — e.g. "### 功能" / "### API endpoint"
MUST_CATEGORY_RE = re.compile(r"(?m)^###\s+(?P<cat>[\w\s一-鿿\-/]+?)\s*(?:\(.*\))?\s*$")


@dataclass
class PlanTask:
    heading: str
    body: str
    fields: dict[str, str] = field(default_factory=dict)

    def has(self, field_name: str) -> bool:
        return field_name.lower() in {k.lower() for k in self.fields}


REQUIRED_TASK_FIELDS = ("objective", "target", "steps", "verification", "done")


def parse_plan_tasks(plan_text: str) -> list[PlanTask]:
    tasks: list[PlanTask] = []
    pattern = re.compile(r"(?ms)^(##\s+(?:Task|任务)\s+.+?)\n(.*?)(?=^##\s+(?:Task|任务)|\Z)")
    for m in pattern.finditer(plan_text):
        heading = m.group(1).strip()
        body = m.group(2)
        fields: dict[str, str] = {}
        for kw in REQUIRED_TASK_FIELDS:
            # Accept 'kw', 'kw X', 'X kw', 'X kw Y' — keyword as whole word, allow 1 adjacent modifier
            mf = re.search(
                rf"(?im)^[-*]?\s*\*?\*?\s*(?:\w+\s+)?{kw}(?:\s+\w+)?\s*:\s*(?P<val>.+?)$",
                body,
            )
            if mf:
                fields[kw] = mf.group("val").strip()
        tasks.append(PlanTask(heading=heading, body=body, fields=fields))
    return tasks


def plan_must_items(plan_text: str) -> list[str]:
    """Return list of MUST item descriptions (legacy API; strips any [ID] prefix)."""
    out: list[str] = []
    for m in PLAN_MUST_RE.finditer(plan_text):
        raw = m.group("item").strip()
        # Strip optional [ID] prefix
        m2 = re.match(r"\[([A-Za-z][\w\-]{1,40})\]\s*(.+)$", raw)
        out.append(m2.group(2).strip() if m2 else raw)
    return out


@dataclass
class MustItem:
    must_id: str  # "[F-001]" → "F-001"; fallback auto-generated "MUST-auto-{n}"
    category: str  # "功能" / "UI" / "API endpoint" / "Migration" / "uncategorized"
    desc: str

    @property
    def has_explicit_id(self) -> bool:
        return not self.must_id.startswith("MUST-auto-")


def plan_must_items_structured(plan_text: str) -> list[MustItem]:
    """Return MUST items with category + ID resolved.

    Category = nearest preceding '###' heading within a 'Delivery Scope' section
               (or 'uncategorized' if no heading precedes).
    ID       = from `[XXX]` prefix on the MUST line, or auto-generated sequential.
    """
    # Restrict to Delivery Scope section if present; else scan whole doc
    scope = extract_section(plan_text, r"Delivery\s+Scope|交付范围|交付清单")
    text = scope or plan_text
    # Build line-indexed category map
    current_cat = "uncategorized"
    items: list[MustItem] = []
    auto_idx = 0
    for line in text.splitlines():
        mcat = MUST_CATEGORY_RE.match(line)
        if mcat:
            current_cat = mcat.group("cat").strip()
            continue
        mid = PLAN_MUST_IDENTIFIED_RE.match(line)
        if mid:
            items.append(MustItem(must_id=mid.group("id"), category=current_cat, desc=mid.group("desc").strip()))
            continue
        m = PLAN_MUST_RE.match(line)
        if m:
            auto_idx += 1
            items.append(
                MustItem(
                    must_id=f"MUST-auto-{auto_idx:03d}",
                    category=current_cat,
                    desc=m.group("item").strip(),
                )
            )
    return items


def plan_must_categories(plan_text: str) -> dict[str, list[MustItem]]:
    """Group MUST items by category."""
    groups: dict[str, list[MustItem]] = {}
    for item in plan_must_items_structured(plan_text):
        groups.setdefault(item.category, []).append(item)
    return groups


def plan_deferred_items(plan_text: str) -> list[str]:
    return [m.group("item").strip() for m in PLAN_DEFERRED_RE.finditer(plan_text)]


# ---------- feature-checklist.md parsing ----------

FEATURE_ITEM_RE = re.compile(
    r"(?m)^[-*]\s+(?P<body>.+?)(?:\n(?P<detail>(?:\s{2,}.+\n?)+))?",
)

PHASE_MODULE_WORDS = re.compile(
    r"\b(phase\s+\d|stage|module|category|feature\s+set|部分|模块|阶段)\b",
    re.IGNORECASE,
)


@dataclass
class FeatureItem:
    id: str
    behavior: str
    test_type: str = ""
    test_tool: str = ""
    is_behavior: bool = True  # False if looks like phase/module name

    def valid(self) -> bool:
        return self.is_behavior and bool(self.test_type) and bool(self.test_tool)


def parse_feature_checklist(text: str) -> list[FeatureItem]:
    items: list[FeatureItem] = []
    counter = 0
    for line in text.splitlines():
        m = re.match(r"^[-*]\s+(.+)$", line)
        if not m:
            continue
        counter += 1
        body = m.group(1)
        test_type = ""
        test_tool = ""
        mt = re.search(r"test[_\s-]*type\s*[:=]\s*(\w+)", body, re.IGNORECASE)
        if mt:
            test_type = mt.group(1)
        mtool = re.search(r"test[_\s-]*tool\s*[:=]\s*([\w\-.]+)", body, re.IGNORECASE)
        if mtool:
            test_tool = mtool.group(1)
        is_behavior = not PHASE_MODULE_WORDS.search(body)
        items.append(
            FeatureItem(
                id=f"F-{counter:03d}",
                behavior=re.sub(r"\s*test[_\s-]*type.*", "", body, flags=re.IGNORECASE).strip(),
                test_type=test_type,
                test_tool=test_tool,
                is_behavior=is_behavior,
            )
        )
    return items


# ---------- execution.md parsing ----------

EXEC_FEATURE_HEADING_RE = re.compile(r"(?mi)^##\s+Feature(?:\s*[:\-])?\s+(?P<name>.+?)\s*$")
EXEC_STATUS_RE = re.compile(r"(?mi)^\s*Status\s*:\s*(?P<status>COMPLETE|BLOCKED|DEFERRED)")
EXEC_RED_RE = re.compile(r"(?mi)^###\s+RED\s+evidence\b")
EXEC_GREEN_RE = re.compile(r"(?mi)^###\s+GREEN\s+evidence\b")
EXEC_BLOCKED_RE = re.compile(r"(?mi)^##\s+BLOCKED\s*[—\-]\s*Feature")


@dataclass
class FeatureSection:
    name: str
    status: str
    body: str
    has_red: bool
    has_green: bool


def parse_execution_features(text: str) -> list[FeatureSection]:
    sections: list[FeatureSection] = []
    matches = list(EXEC_FEATURE_HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        status = (EXEC_STATUS_RE.search(body) or [None, ""])[0] if False else ""
        ms = EXEC_STATUS_RE.search(body)
        status = ms.group("status") if ms else ""
        sections.append(
            FeatureSection(
                name=m.group("name").strip(),
                status=status,
                body=body,
                has_red=bool(EXEC_RED_RE.search(body)),
                has_green=bool(EXEC_GREEN_RE.search(body)),
            )
        )
    return sections


# ---------- review.md parsing ----------

REVIEW_VERDICT_RE = re.compile(r"(?mi)^\s*\*?\*?\s*Verdict\s*\*?\*?\s*:\s*(?P<v>CLEAR_WITH_CONCERNS|CLEAR|BLOCK)")


def review_verdict(text: str) -> str:
    m = REVIEW_VERDICT_RE.search(text)
    return m.group("v").upper() if m else ""


# ---------- verification.md parsing ----------

VERIFY_VERDICT_RE = re.compile(r"(?mi)^\s*\*?\*?\s*Verdict\s*\*?\*?\s*:\s*(?P<v>PASS|FAIL|INCOMPLETE)")
DELIVERY_CONFIDENCE_RE = re.compile(r"(?mi)delivery[_\s-]*confidence\s*:\s*(?P<c>high|medium|low)")


def verification_verdict(text: str) -> str:
    m = VERIFY_VERDICT_RE.search(text)
    return m.group("v").upper() if m else ""


def verification_confidence(text: str) -> str:
    m = DELIVERY_CONFIDENCE_RE.search(text)
    return m.group("c").lower() if m else ""


# ---------- subjective-language detector ----------

SUBJECTIVE_WORDS = re.compile(
    r"\b(appears|seems|probably|should|looks\s+fine)\b",
    re.IGNORECASE,
)

BACKTICK_QUOTED_RE = re.compile(r"`[^`]*`")


def find_subjective_violations(text: str) -> list[str]:
    """Find disallowed subjective words outside of backtick-quoted spans."""
    # Strip backticks to avoid matching quoted forms like `should pass`
    stripped = BACKTICK_QUOTED_RE.sub("", text)
    return [m.group(0) for m in SUBJECTIVE_WORDS.finditer(stripped)]


# ---------- ui-intent.md parsing ----------

UI_INTENT_REQUIRED_SECTIONS = (
    r"Aesthetic\s+Direction",
    r"Typography\s+Contract",
    r"Color\s+Contract",
    r"Motion\s+Contract",
    r"Spatial\s+Contract",
    r"Visual\s+Detail\s+Contract",
    r"Anti[-\s]Pattern\s+Exclusions",
)


def ui_intent_missing_sections(text: str) -> list[str]:
    missing: list[str] = []
    for sect in UI_INTENT_REQUIRED_SECTIONS:
        if not has_section(text, sect):
            missing.append(sect.replace(r"\s+", " ").replace("[-\\s]", " "))
    return missing


def ui_intent_typography_whitelist(text: str) -> list[str]:
    """Extract declared font-family names from Typography Contract section."""
    body = extract_section(text, r"Typography\s+Contract")
    if not body:
        return []
    # Naive: pick quoted strings + bare names after 'font-family:' / 'font:'
    names: list[str] = []
    for m in re.finditer(r'["\']([A-Za-z][\w\s\-]{1,40})["\']', body):
        names.append(m.group(1).strip())
    for m in re.finditer(r"(?mi)font(?:-family)?\s*[:=]\s*([A-Za-z][\w\s\-,]{2,80})", body):
        for n in m.group(1).split(","):
            n = n.strip().strip('"').strip("'")
            if n:
                names.append(n)
    return list(dict.fromkeys(names))  # dedupe preserving order
