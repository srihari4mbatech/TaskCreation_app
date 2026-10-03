from __future__ import annotations

from pathlib import Path

from taskmgr.agent import PROJECT_ROOT, build_options


def test_skills_enabled() -> None:
    options = build_options()
    assert options.setting_sources == ["project"]
    assert "Skill" in options.allowed_tools
    assert options.cwd == str(PROJECT_ROOT)


def test_skill_files_exist() -> None:
    skills = PROJECT_ROOT / ".claude" / "skills"
    for name in ("prioritize-tasks", "daily-planner", "task-breakdown"):
        text = Path(skills / name / "SKILL.md").read_text()
        assert f"name: {name}" in text
