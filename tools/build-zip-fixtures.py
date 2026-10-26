"""Build the fixture archives that need ZIP features a plain "zip a folder"
can't express: symbolic link entries, a non-DEFLATE compression method,
hostile resource-limit archives, and the project-mode archive built alongside
them.

    python tools/build-zip-fixtures.py

Writes to fixtures/:

- symlink-entries.mdz        (test T-017; Sections 4, 13.1)
- unsupported-compression.mdz (test T-014; Section 4)
- project-mode.mdz           (test T-015; Section 5.7.6), from fixtures/src/project-mode/
- limit-forged-size.mdz      (test T-018; Section 13.1)
- limit-high-ratio.mdz       (test T-018; Section 13.1)
- limit-overlapping-entries.mdz (test T-018; Section 13.1)

Output is byte-for-byte reproducible: fixed timestamps, fixed entry order and
attributes. Rerun it after changing anything below or in fixtures/src/project-mode/,
and commit the archives together with this script.

Python's zipfile is used because it writes Unix file types in the external
attributes and supports BZIP2 (method 12); Node has neither built in. The
resource-limit archives are written byte by byte instead, because they need
sizes and offsets that zipfile won't write (a declared size smaller than the
data, several directory entries sharing one file's data).
"""

from pathlib import Path
import hashlib
import struct
import zipfile
import zlib

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"
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
    src = FIXTURES / "src" / "project-mode"
    files = sorted(p for p in src.rglob("*") if p.is_file())
    # manifest.json first, then the rest in path order.
    files.sort(key=lambda p: (p.name != "manifest.json", p.relative_to(src).as_posix()))
    write(FIXTURES / "project-mode.mdz", [
        (entry(p.relative_to(src).as_posix()), p.read_bytes().decode("utf-8"))
        for p in files
    ])


# ---- Resource-limit archives (test T-018) ----

MiB = 1024 * 1024


def deflate(data):
    """Raw DEFLATE (method 8) at level 9."""
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return c.compress(data) + c.flush()


def dos_datetime():
    y, mo, d, h, mi, s = DATE
    return (h << 11) | (mi << 5) | (s // 2), ((y - 1980) << 9) | (mo << 5) | d


def raw_zip(path, files, aliases=()):
    """Write a ZIP byte by byte.

    files: list of dicts with name, payload (stored bytes), method, crc and the
    declared csize/usize, which are written as given even when they don't match
    the payload. aliases: extra central directory entries as (name, index of the
    file whose local header and data they reuse), with that file's sizes.
    """
    time, date = dos_datetime()
    out = bytearray()
    central = []
    for f in files:
        f["offset"] = len(out)
        name = f["name"].encode("ascii")
        out += struct.pack("<IHHHHHIIIHH", 0x04034B50, 20, 0, f["method"], time, date,
                           f["crc"], f["csize"], f["usize"], len(name), 0)
        out += name + f["payload"]
        central.append((name, f))
    for alias, index in aliases:
        central.append((alias.encode("ascii"), files[index]))
    cd_offset = len(out)
    for name, f in central:
        out += struct.pack("<IHHHHHHIIIHHHHHII", 0x02014B50, (3 << 8) | 20, 20, 0, f["method"],
                           time, date, f["crc"], f["csize"], f["usize"], len(name), 0, 0, 0, 0,
                           (S_IFREG | 0o644) << 16, f["offset"])
        out += name
    cd_size = len(out) - cd_offset
    out += struct.pack("<IHHHHIIH", 0x06054B50, 0, 0, len(central), len(central), cd_size, cd_offset, 0)
    path.write_bytes(bytes(out))
    print(f"wrote {path.relative_to(ROOT)} ({len(out)} bytes)")


def honest(name, data):
    payload = deflate(data)
    return {"name": name, "payload": payload, "method": 8, "crc": zlib.crc32(data),
            "csize": len(payload), "usize": len(data)}


def limit_entries(title, index_text):
    return [honest("manifest.json", manifest(title, "document").encode("utf-8")),
            honest("index.md", index_text.encode("utf-8"))]


FORGED_INDEX = """# Forged declared size

Fixture for test T-018. `data/blob.bin` declares 1024 bytes in both its local
header and the central directory, but its DEFLATE data expands to 64 MiB of
zeros (its CRC-32 is that of the 64 MiB). A reader must not return more than
the declared 1024 bytes, and must report an error rather than the first 1024.
This file and `manifest.json` are ordinary entries.
"""

RATIO_INDEX = """# High compression ratio

Fixture for test T-018. `data/zeros.bin` is 64 MiB of zeros stored in about
64 KB, a compression ratio above 1000:1. Its declared sizes are accurate.
This file and `manifest.json` are ordinary entries.
"""

OVERLAP_INDEX = """# Overlapping entries

Fixture for test T-018. The central directory lists 300 entries,
`data/part-000.bin` to `data/part-299.bin`, that all point at the same 16 MiB
of data stored in about 60 KB, so the archive declares about 4.7 GiB in total.
Each entry on its own has an ordinary size and ratio; only the total is
excessive. Only `data/part-000.bin` has a matching local header.
This file and `manifest.json` are ordinary entries.
"""


def build_forged_size():
    data = bytes(64 * MiB)
    payload = deflate(data)
    files = limit_entries("Forged Declared Size", FORGED_INDEX)
    files.append({"name": "data/blob.bin", "payload": payload, "method": 8,
                  "crc": zlib.crc32(data), "csize": len(payload), "usize": 1024})
    raw_zip(FIXTURES / "limit-forged-size.mdz", files)


def build_high_ratio():
    files = limit_entries("High Compression Ratio", RATIO_INDEX)
    files.append(honest("data/zeros.bin", bytes(64 * MiB)))
    ratio = files[-1]["usize"] / files[-1]["csize"]
    assert ratio > 1000, f"ratio {ratio:.0f}:1 is not above the 1000:1 reference limit"
    raw_zip(FIXTURES / "limit-high-ratio.mdz", files)


def sparse_data(size, step=1024):
    """Mostly zeros with a byte every `step` bytes: about 287:1 under DEFLATE."""
    buf = bytearray(size)
    seed = hashlib.sha256(b"mdzip").digest()
    for i in range(0, size, step):
        buf[i] = seed[(i // step) % 32] | 1
    return bytes(buf)


def build_overlapping():
    files = limit_entries("Overlapping Entries", OVERLAP_INDEX)
    files.append(honest("data/part-000.bin", sparse_data(16 * MiB)))
    part = files[-1]
    assert part["usize"] / part["csize"] < 1000, "each entry must stay under the 1000:1 reference ratio"
    count = 300
    assert count * part["usize"] > 4 * 1024**3, "the declared total must exceed the 4 GiB reference limit"
    aliases = [(f"data/part-{i:03d}.bin", len(files) - 1) for i in range(1, count)]
    raw_zip(FIXTURES / "limit-overlapping-entries.mdz", files, aliases)


if __name__ == "__main__":
    build_symlinks()
    build_compression()
    build_project()
    build_forged_size()
    build_high_ratio()
    build_overlapping()
