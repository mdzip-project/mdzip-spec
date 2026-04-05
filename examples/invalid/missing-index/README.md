# Invalid Fixture

This fixture intentionally omits `index.md` while the manifest declares `"entryPoint": "index.md"`. The referenced entry point file does not exist in the archive. A conforming consumer MUST report an error (`ERR_ENTRYPOINT_MISSING`). See spec Section 5.5.
