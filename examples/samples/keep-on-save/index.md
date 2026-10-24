# Keep on Save

Use this archive to check that your app **keeps what it doesn't understand**
when it saves.

1. Open this archive in your app.
2. Change this sentence: EDIT ME.
3. Save, then list the archive (for example `mdz ls keep-on-save.mdz`).

After saving, all of the following must still be there, unchanged:

- `AGENTS.md`, a support file for AI agents (Section 5.8)
- `README.md`, a support file for people (Section 5.6)
- `data/prices.csv`, a file type your app may not open
- `extensions/other-app/state.bin`, a file in an unknown folder
- In `manifest.json`: the top-level `x-other-app` object and
  `author.x-other-app-id`. Fields your app doesn't recognize must survive a
  rewrite of the manifest (Section 6.3).

Then run `mdz validate` on the saved file. It should report no errors.

For an automated version of this check, use `round-trip.mdz` and
`round-trip-expectations.json` in the spec's `fixtures/` folder
(checks `P-004` and `P-005`).
