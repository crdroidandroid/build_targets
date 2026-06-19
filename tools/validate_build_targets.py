#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ALLOWED_BUILD_TYPES = {"user", "userdebug", "eng"}
ALLOWED_AUTO_UPLOAD = {"yes", "no"}
DEVICE_PATTERN = re.compile(r"^[A-Za-z0-9._+-]+$")
IMAGE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*\.img$")
LINE_PATTERN = re.compile(r"^(\S+)\s+(\S+)\s+(\S+)\s+(\[.*\])\s*$")


@dataclass
class Finding:
    level: str
    line: int
    message: str


@dataclass
class ValidationResult:
    file: str
    checked_entries: int
    errors: list[Finding]
    warnings: list[Finding]

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_saveimages(raw: str, line_no: int, findings: list[Finding]) -> list[str]:
    if not (raw.startswith("[") and raw.endswith("]")):
        findings.append(Finding("error", line_no, "saveimages must be enclosed in [ ]"))
        return []

    inner = raw[1:-1].strip()
    if not inner:
        findings.append(Finding("warning", line_no, "saveimages list is empty"))
        return []

    images: list[str] = []
    for part in inner.split(","):
        image = part.strip()
        if not image:
            findings.append(Finding("error", line_no, "saveimages contains an empty entry"))
            continue
        images.append(image)
    return images


def validate_lines(lines: Iterable[str], file_path: Path) -> ValidationResult:
    errors: list[Finding] = []
    warnings: list[Finding] = []
    seen_devices: dict[str, int] = {}
    seen_casefold: dict[str, tuple[str, int]] = {}
    checked_entries = 0

    for index, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        checked_entries += 1
        match = LINE_PATTERN.match(line)
        if not match:
            errors.append(
                Finding(
                    "error",
                    index,
                    "line must match: <device> <build_type> <auto-upload> <saveimages>",
                )
            )
            continue

        device, build_type, auto_upload, saveimages_raw = match.groups()
        device_key = device.casefold()

        if device in seen_devices:
            errors.append(
                Finding(
                    "error",
                    index,
                    f"duplicate device '{device}' (already defined at line {seen_devices[device]})",
                )
            )
        else:
            seen_devices[device] = index

        previous_case = seen_casefold.get(device_key)
        if previous_case and previous_case[0] != device:
            warnings.append(
                Finding(
                    "warning",
                    index,
                    f"device differs only by case from '{previous_case[0]}' at line {previous_case[1]}",
                )
            )
        else:
            seen_casefold[device_key] = (device, index)

        if not DEVICE_PATTERN.match(device):
            errors.append(
                Finding("error", index, f"invalid device token '{device}'")
            )

        if build_type not in ALLOWED_BUILD_TYPES:
            errors.append(
                Finding(
                    "error",
                    index,
                    f"invalid build_type '{build_type}'; expected one of {sorted(ALLOWED_BUILD_TYPES)}",
                )
            )

        if auto_upload not in ALLOWED_AUTO_UPLOAD:
            errors.append(
                Finding(
                    "error",
                    index,
                    f"invalid auto-upload '{auto_upload}'; expected one of {sorted(ALLOWED_AUTO_UPLOAD)}",
                )
            )

        line_findings: list[Finding] = []
        images = parse_saveimages(saveimages_raw, index, line_findings)
        for finding in line_findings:
            (errors if finding.level == "error" else warnings).append(finding)

        for image in images:
            if not IMAGE_PATTERN.match(image):
                warnings.append(
                    Finding(
                        "warning",
                        index,
                        f"suspicious image name '{image}' (expected lowercase *.img style)",
                    )
                )

        if build_type == "user" and len(images) > 4:
            warnings.append(
                Finding(
                    "warning",
                    index,
                    "user build target has many saved images; verify this is intentional",
                )
            )

    return ValidationResult(
        file=str(file_path),
        checked_entries=checked_entries,
        errors=errors,
        warnings=warnings,
    )


def emit_text(result: ValidationResult) -> None:
    print(f"Validated {result.checked_entries} build target entries in {result.file}")
    for finding in result.errors + result.warnings:
        print(f"{finding.level.upper()} line {finding.line}: {finding.message}")
    print(
        f"Summary: {len(result.errors)} error(s), {len(result.warnings)} warning(s)"
    )


def emit_json(result: ValidationResult) -> None:
    payload = {
        "ok": result.ok,
        "file": result.file,
        "checked_entries": result.checked_entries,
        "errors": [asdict(f) for f in result.errors],
        "warnings": [asdict(f) for f in result.warnings],
    }
    print(json.dumps(payload, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate build_targets entries against repository schema."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="build_targets",
        help="Path to build_targets-style file (default: ./build_targets)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    file_path = Path(args.path)
    if not file_path.exists():
        print(f"ERROR: file not found: {file_path}", file=sys.stderr)
        return 2
    if not file_path.is_file():
        print(f"ERROR: not a regular file: {file_path}", file=sys.stderr)
        return 2

    lines = file_path.read_text(encoding="utf-8").splitlines()
    result = validate_lines(lines, file_path)

    if args.json:
        emit_json(result)
    else:
        emit_text(result)

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
