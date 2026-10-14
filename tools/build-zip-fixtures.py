"""Build the fixture archives that need ZIP features a plain "zip a folder"
can't express: symbolic link entries, a non-DEFLATE compression method, and
the project-mode archive built alongside them.

    python tools/build-zip-fixtures.py

Writes to examples/fixtures/:

- symlink-entries.mdz        (test T-017; Sections 4, 13.1)
- unsupported-compression.mdz (test T-014; Section 4)
- project-mode.mdz           (test T-015; Section 5.7.6), from examples/project-mode/

Output is byte-for-byte reproducible: fixed timestamps, fixed entry order and
attributes. Rerun it after changing anything below or in examples/project-mode/,
and commit the archives together with this script.

Python's zipfile is used because it writes Unix file types in the external
attributes and supports BZIP2 (method 12); Node has neither built in.
"""

from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "examples" / "fixtures"
DATE = (2026, 10, 13, 0, 0, 0)

S_IFREG = 0o100000
S_IFLNK = 0o120000


def entry(name, *, mode=S_IFREG | 0o644, method=zipfile.ZIP_DEFLATED):
    info = zipfile.ZipInfo(name, date_time=DATE)
    info.create_system = 3  # Unix, so readers interpret the file type bits
    info.external_attr = mode << 16
    info.compress_type = method
    return info


def write(path, entries):
    """entries: list of (ZipInfo, text)."""
    with zipfile.ZipFile(path, "w") as zf:
        for info, text in entries:
            zf.writestr(info, text.encode("utf-8"))
    print(f"wrote {path.relative_to(ROOT)}")


def manifest(title, mode):
    return (
        "{\n"
        '  "spec": {\n'
        '    "version": "1.2.0"\n'
        "  },\n"
        f'  "title": "{title}",\n'
        f'  "mode": "{mode}",\n'
        '  "entryPoint": "index.md"\n'
        "}\n"
    )


def symlink(name, target):
    # A symbolic link entry stores its target path as the entry's content.
    return entry(name, mode=S_IFLNK | 0o777, method=zipfile.ZIP_STORED), target


SYMLINK_INDEX = """# Symbolic link entries

Fixture for test T-017. Every entry is a regular file except the three
symbolic links: `shortcut.md`, `linked` and `escape.md`.

- [Regular file](notes.md)
- [Nested regular file](docs/page.md)
- [File link](shortcut.md): `shortcut.md` is a symbolic link to `notes.md`.
- [Through a directory link](linked/page.md): `linked` is a symbolic link to `docs`.
- [Escaping link](escape.md): `escape.md` is a symbolic link to a path outside the archive.
"""


def build_symlinks():
    write(FIXTURES / "symlink-entries.mdz", [
        (entry("manifest.json"), manifest("Symbolic Link Entries", "document")),
        (entry("index.md"), SYMLINK_INDEX),
        (entry("notes.md"), "# Notes\n\nThe real file that `shortcut.md` points to.\n"),
        (entry("docs/page.md"), "# Page\n\nThe real file under `docs/`, which `linked` points to.\n"),
        symlink("shortcut.md", "notes.md"),
        symlink("linked", "docs"),
        symlink("escape.md", "../../outside-the-archive.md"),
    ])


COMPRESSION_INDEX = """# Unsupported compression

Fixture for test T-014. This file is compressed with BZIP2 (method 12).
`manifest.json` uses DEFLATE (method 8), which every consumer supports.
"""


def build_compression():
    write(FIXTURES / "unsupported-compression.mdz", [
        (entry("manifest.json"), manifest("Unsupported Compression", "document")),
        (entry("index.md", method=zipfile.ZIP_BZIP2), COMPRESSION_INDEX),
    ])


def build_project():
    src = ROOT / "examples" / "project-mode"
    files = sorted(p for p in src.rglob("*") if p.is_file())
    # manifest.json first, then the rest in path order.
    files.sort(key=lambda p: (p.name != "manifest.json", p.relative_to(src).as_posix()))
    write(FIXTURES / "project-mode.mdz", [
        (entry(p.relative_to(src).as_posix()), p.read_bytes().decode("utf-8"))
        for p in files
    ])


if __name__ == "__main__":
    build_symlinks()
    build_compression()
    build_project()
