#!/usr/bin/env python3
"""Offline distribution integrity check; no installed Codex or user data needed."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "DISTRIBUTION.json").read_text(encoding="utf-8"))
for relative, expected in report["sha256"].items():
    path = ROOT / relative
    assert path.resolve().is_relative_to(ROOT) and not path.is_symlink(), relative
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, relative
catalog = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
assert catalog["name"] == "threads-collector"
assert len(catalog["plugins"]) == 1
assert catalog["plugins"][0]["source"] == {"source": "local", "path": "./plugins/threads-collector"}
plugin = ROOT / "plugins/threads-collector"
manifest = json.loads((plugin / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
assert manifest["name"] == "threads-collector" and manifest["version"] == report["version"]
skills = sorted(path.parent.name for path in (plugin / "skills").glob("*/SKILL.md"))
assert {"threads-collect", "threads-setup", "threads-plugin-check"}.issubset(skills)
for name in skills:
    text = (plugin / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n") and re.search(r"^name: " + re.escape(name) + "$", text, re.M)
assert "계정당 미디어가 있는 고유 원글 최대 2건" in (plugin / "skills/threads-collect/SKILL.md").read_text(encoding="utf-8")
print(json.dumps({"verifiedFiles": len(report["sha256"]), "version": manifest["version"], "skills": skills}, ensure_ascii=False))
