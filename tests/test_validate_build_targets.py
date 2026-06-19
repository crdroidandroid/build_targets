from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_build_targets.py"
VALID_FIXTURE = ROOT / "tests" / "fixtures" / "valid_build_targets.txt"
INVALID_FIXTURE = ROOT / "tests" / "fixtures" / "invalid_build_targets.txt"


def run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )


def test_valid_fixture_passes() -> None:
    result = run_validator(str(VALID_FIXTURE))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Summary: 0 error(s)" in result.stdout


def test_invalid_fixture_fails_and_reports_findings() -> None:
    result = run_validator(str(INVALID_FIXTURE))
    assert result.returncode == 1
    assert "duplicate device 'cheetah'" in result.stdout
    assert "invalid auto-upload 'maybe'" in result.stdout
    assert "saveimages contains an empty entry" in result.stdout
    assert "Summary:" in result.stdout


def test_json_output_shape() -> None:
    result = run_validator("--json", str(INVALID_FIXTURE))
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["checked_entries"] == 6
    assert len(payload["errors"]) >= 3
    assert len(payload["warnings"]) >= 1
