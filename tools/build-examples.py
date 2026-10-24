"""Build the sample archives in examples/samples/ from their source folders.

    python tools/build-examples.py

Each folder in examples/samples/ is the archive-root contents of one sample;
the archive is written next to it as <folder>.mdz. Output is byte-for-byte
reproducible (fixed timestamps, sorted entries, `manifest.json` first), so
rerun this after changing a sample and commit the folder and archive together.

Every archive is a conforming archive: DEFLATE entries, forward slashes,
NFC names with the UTF-8 flag set for non-ASCII names (Python's zipfile sets
bit 11 automatically), regular files only.
"""

from pathlib import Path
import unicodedata
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "examples" / "samples"
DATE = (2026, 10, 24, 0, 0, 0)
S_IFREG = 0o100000


def build(folder: Path) -> None:
    files = [p for p in folder.rglob("*") if p.is_file()]
    names = {unicodedata.normalize("NFC", p.relative_to(folder).as_posix()): p for p in files}
    order = sorted(names, key=lambda n: (n != "manifest.json", n))
    out = folder.with_suffix(".mdz")
    with zipfile.ZipFile(out, "w") as zf:
        for name in order:
            info = zipfile.ZipInfo(name, date_time=DATE)
            info.create_system = 3  # Unix
            info.external_attr = (S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, names[name].read_bytes())
    print(f"wrote {out.relative_to(ROOT).as_posix()} ({len(order)} entries)")


def main() -> None:
    for folder in sorted(p for p in SAMPLES.iterdir() if p.is_dir()):
        build(folder)


if __name__ == "__main__":
    main()
