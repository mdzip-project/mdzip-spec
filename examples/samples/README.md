# Sample archives

Small, valid `.mdz` files for trying an app by hand. Each archive is built
from the folder with the same name, so you can see exactly what's inside.
What each one checks, and how to use them, is in
[Conformance guide for apps](../implementers.md#step-1-open-the-sample-files).

| Archive | Source folder |
|---------|---------------|
| [`hello.mdz`](hello.mdz) | [`hello/`](hello/) |
| [`field-guide.mdz`](field-guide.mdz) | [`field-guide/`](field-guide/) |
| [`team-notes.mdz`](team-notes.mdz) | [`team-notes/`](team-notes/) |
| [`hand-zipped.mdz`](hand-zipped.mdz) | [`hand-zipped/`](hand-zipped/) |
| [`keep-on-save.mdz`](keep-on-save.mdz) | [`keep-on-save/`](keep-on-save/) |

These are examples, not tests: they are all valid and contain nothing
hostile. The conformance tests, including broken and hostile archives, are in
[`fixtures/`](../../fixtures/README.md).

To rebuild the archives after changing a folder, run
`python tools/build-examples.py` from the repository root. The output is
reproducible byte for byte.
