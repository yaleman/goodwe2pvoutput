"""Merge matching x86_64 and ARM64 Python installs into one Lambda layer."""

import base64
import csv
import hashlib
import shutil
import sys
from pathlib import Path


def files(root: Path) -> dict[Path, Path]:
    return {path.relative_to(root): path for path in root.rglob("*") if path.is_file()}


def record_rows(path: Path) -> set[str]:
    with path.open(newline="") as record:
        return {row[0] for row in csv.reader(record)}


def merge(x86: Path, arm: Path) -> None:
    x86_files, arm_files = files(x86), files(arm)
    x86_only = set(x86_files) - set(arm_files)
    arm_only = set(arm_files) - set(x86_files)
    x86_modules = {str(path).replace("x86_64-linux-gnu.so", "") for path in x86_only}
    arm_modules = {str(path).replace("aarch64-linux-gnu.so", "") for path in arm_only}
    if (
        x86_modules != arm_modules
        or any(not str(path).endswith("x86_64-linux-gnu.so") for path in x86_only)
        or any(not str(path).endswith("aarch64-linux-gnu.so") for path in arm_only)
    ):
        raise ValueError("Architecture builds have different installed files")

    for path in sorted(set(x86_files) & set(arm_files)):
        if x86_files[path].read_bytes() == arm_files[path].read_bytes():
            continue
        if ".dist-info/sboms/" in str(path):
            # A wheel's SBOM describes one binary build, not the combined layer.
            x86_files[path].unlink()
            continue
        if path.name not in {"WHEEL", "RECORD"} or not path.parent.name.endswith(
            ".dist-info"
        ):
            raise ValueError(f"Architecture builds disagree on {path}")
        if path.name == "WHEEL":
            x86_lines = x86_files[path].read_text().splitlines()
            arm_lines = arm_files[path].read_text().splitlines()
            if [line for line in x86_lines if not line.startswith("Tag: ")] != [
                line for line in arm_lines if not line.startswith("Tag: ")
            ]:
                raise ValueError(f"Wheel metadata differs beyond platform tags: {path}")
            tags = [line for line in arm_lines if line.startswith("Tag: ")]
            x86_files[path].write_text("\n".join([*x86_lines, *tags]) + "\n")

    for path in arm_only:
        destination = x86 / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(arm_files[path], destination)

    for info_dir in x86.glob("*.dist-info"):
        x86_record = info_dir / "RECORD"
        arm_record = arm / info_dir.name / "RECORD"
        entries = record_rows(x86_record) | record_rows(arm_record)
        with x86_record.open("w", newline="") as record:
            writer = csv.writer(record)
            for name in sorted(entries):
                installed_file = x86 / name
                if name == str(x86_record.relative_to(x86)):
                    writer.writerow((name, "", ""))
                elif installed_file.is_file():
                    content = installed_file.read_bytes()
                    digest = base64.urlsafe_b64encode(
                        hashlib.sha256(content).digest()
                    ).rstrip(b"=")
                    writer.writerow((name, f"sha256={digest.decode()}", len(content)))


if __name__ == "__main__":
    merge(Path(sys.argv[1]), Path(sys.argv[2]))
