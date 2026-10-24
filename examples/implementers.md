# Conformance guide for apps

For developers of editors, viewers, converters and other tools that support
`.mdz` files: what the specification requires and what is optional, how to
test your support, and how to get your app listed on
[mdzip.org](https://mdzip.org/works-with.html).

To add `.mdz` support using MDZip's libraries, start with
[Add MDZip to Your App](https://mdzip.org/docs/integrate.html), which has code
and AI prompts for each step. The libraries take care of most of the
requirements below. This guide matters most if you implement the format
yourself, and for checking the result either way.

This guide is non-normative. The requirements are in
[`SPEC.md`](../SPEC.md), mainly [Section 14 (Conformance)](../SPEC.md#14-conformance);
when this page and the specification disagree, the specification governs.
It is written against specification **1.2.0**.

- [1. Decide which roles your app plays](#1-decide-which-roles-your-app-plays)
- [2. Required, recommended and optional](#2-required-recommended-and-optional)
- [3. Test it](#3-test-it)
- [4. Common mistakes](#4-common-mistakes)
- [5. If your app also reads other `.mdz` formats](#5-if-your-app-also-reads-other-mdz-formats)
- [6. Getting listed on mdzip.org](#6-getting-listed-on-mdziporg)
- [7. Questions and feedback](#7-questions-and-feedback)

## 1. Decide which roles your app plays

The specification has two roles. Most apps play more than one.

| Your app...                                   | Role                         | Spec section |
|-----------------------------------------------|------------------------------|--------------|
| opens `.mdz` files                            | **consumer**                 | [14.2](../SPEC.md#142-conforming-consumer) |
| makes new `.mdz` files (New, Save As, export) | **producer: creation**       | [14.1](../SPEC.md#141-conforming-producer), first list |
| saves changes to an existing `.mdz` file      | **producer: modification**   | [14.1](../SPEC.md#141-conforming-producer), second list |
| shows Markdown as HTML                        | **rendering consumer**: also the content-safety rules | [13.2](../SPEC.md#132-content-handling) |

A Markdown editor that opens, edits and saves `.mdz` files plays all four.
A converter that only writes `.mdz` files is a producer only.

## 2. Required, recommended and optional

MUST items are required for conformance; SHOULD items are strongly
recommended; MAY items are optional features. Each line links to the rule it
summarizes.

### Opening an archive (consumer)

Required:

- [ ] Read ZIP entries stored with method 0 (stored) or 8 (DEFLATE). For any other method, either read it correctly or reject the archive; never show the entry empty. ([§4](../SPEC.md#4-file-format))
- [ ] Open archives **without** `manifest.json`. A missing manifest is not an error. ([§14.2](../SPEC.md#142-conforming-consumer) item 4)
- [ ] Find the main document with the entry point discovery algorithm: `manifest.json` `entryPoint`, then `index.md`, then the only root-level Markdown file once support files (`README`, `AGENTS`, `LICENSE`, `CHANGELOG`, `CONTRIBUTING`) are set aside. If none of these applies, ask the user or show an error; never pick a file arbitrarily. ([§5.5](../SPEC.md#55-entry-point-discovery))
- [ ] If the manifest's `entryPoint` is malformed or names a missing file, don't silently open a different file. Report it, or recover with a **visible** warning. ([§5.5](../SPEC.md#55-entry-point-discovery))
- [ ] Validate `manifest.json` and ignore fields you don't recognize. ([§6.4](../SPEC.md#64-manifest-validation))
- [ ] Treat a missing `mode` as `"document"`. For `"project"`, either open the documents separately, or (if your app is document-only) refuse with `ERR_MODE_UNSUPPORTED` or open the entry point with a visible warning. Never treat an unknown mode as `"document"` silently. ([§5.7](../SPEC.md#57-mode-semantics))
- [ ] Reject an archive whose `spec.version` has a higher **major** version than you support. ([§14.2](../SPEC.md#142-conforming-consumer) item 13)
- [ ] Accept `created` and `modified` either as an object (`{"when": ...}`) or as a plain date string. ([§6.1](../SPEC.md#61-schema))
- [ ] Resolve links and images relative to the file that contains them, percent-decoding each path segment, and match paths **case-sensitively** after Unicode NFC normalization. ([§9.3](../SPEC.md#93-path-resolution), [§5.4.1](../SPEC.md#541-path-matching))
- [ ] Accept LF and CRLF line endings. ([§12.2](../SPEC.md#122-line-endings))
- [ ] Handle unsafe entry names (`../`, absolute paths, duplicates) without extracting them under their stored names or renaming them silently. Never follow symbolic link entries. ([§13.1](../SPEC.md#131-archive-handling))
- [ ] If you render to HTML: run no script from the archive. ([§13.2](../SPEC.md#132-content-handling))

Recommended:

- [ ] Let users turn off automatic loading of remote images and other external resources, and warn before opening external links. ([§13.2](../SPEC.md#132-content-handling))
- [ ] Limit entry count, uncompressed size and compression ratio, to guard against ZIP bombs. ([§13.1](../SPEC.md#131-archive-handling))

Optional:

- [ ] Show `title`, `cover` and other manifest metadata. An invalid `cover` is ignored, not an error. ([§6.2](../SPEC.md#62-field-definitions))
- [ ] Follow links that leave the archive (`../Notes.md`) or point into another archive (`Other.mdz/page.md`). If you don't support these, treat them as unresolved; never resolve them to a different file. ([§9.4–9.6](../SPEC.md#94-links-outside-the-archive-optional))
- [ ] Support wikilinks (`[[Page]]`) and other dialect-specific syntax. ([§9.7](../SPEC.md#97-other-link-syntaxes))

### Creating a new archive (producer)

Required:

- [ ] Write a valid ZIP archive with the `.mdz` extension, using method 0 or 8, no encryption, no symbolic links, and no ZIP64 extensions unless the archive is too large without them. ([§4](../SPEC.md#4-file-format))
- [ ] Write `manifest.json` at the root with `spec.version` (for example `"1.2.0"`) and `entryPoint` naming a Markdown file in the archive. ([§14.1](../SPEC.md#141-conforming-producer) items 2–4)
- [ ] If the archive is a collection of separate documents, set `"mode": "project"`. ([§5.7.3](../SPEC.md#573-project-mode))
- [ ] Write Markdown and JSON files as UTF-8.
- [ ] Use forward slashes in entry names. No `..`, empty or `.` segments, no reserved characters (`\ : * ? " < > |`), no control characters, no duplicate names. ([§5.4](../SPEC.md#54-path-constraints))
- [ ] Set the ZIP UTF-8 flag (general-purpose bit 11) on non-ASCII entry names. ([§4](../SPEC.md#4-file-format))
- [ ] Keep the capitalization of file names as the user wrote them. Paths are case-sensitive, so lowercasing them breaks links. ([§14.1](../SPEC.md#141-conforming-producer) item 13)

Recommended:

- [ ] Include `title` and `mode` (also `"document"`).
- [ ] Name the main document `index.md` when you can.
- [ ] Include every image the document uses.
- [ ] Include `producer.application.name`, `.version` and `.url`, so a file can be traced back to your app.
- [ ] Write NFC entry names and LF line endings in Markdown and `manifest.json`.

Optional: `author`, `language`, `description`, `created`, `modified`,
`license`, `keywords`, `cover`, a human-facing `README.md`
([§5.6](../SPEC.md#56-human-facing-readmemd-optional)) and an agent-facing
`AGENTS.md` ([§5.8](../SPEC.md#58-agent-facing-agentsmd-optional)).

### Saving changes to an existing archive (producer)

This is where most editors go wrong. Required:

- [ ] **Keep every entry you don't intend to change**, byte for byte: files you don't recognize, can't display or don't use, including `AGENTS.md`, `README.md` and files in unfamiliar folders. Remove one only when the user asks. ([§14.1](../SPEC.md#141-conforming-producer), modification item 4)
- [ ] **Keep manifest fields you don't recognize** when you rewrite `manifest.json`, at the top level and inside known objects such as `author`. If you load the manifest into a typed model, keep the unknown fields alongside it. ([§6.3](../SPEC.md#63-additional-fields))
- [ ] Don't change which file is the entry point unless that is what the user asked for.
- [ ] Don't introduce anything the creation rules forbid (bad names, unsupported compression) into the entries you write.

Recommended: if the archive had no manifest, add one with the entry point the
archive had before saving.

## 3. Test it

### Step 1: Open the sample files

The [`samples/`](samples/) folder has small, valid archives that real apps
produce, each with its source folder next to it so you can see what's inside.
Open each one in your app and check what its first page says.

| Sample | What it checks |
|--------|----------------|
| [`hello.mdz`](samples/hello.mdz) | The smallest archive a producer creates. |
| [`field-guide.mdz`](samples/field-guide.mdz) | One document in several files: relative links with `../` and `#fragments`, a space (`%20`) and a non-ASCII name in a link, an image floated with `align="right"`, a cover, and every manifest field, with `created` and `modified` in their two different forms. |
| [`team-notes.mdz`](samples/team-notes.mdz) | Project mode: separate documents that must not be joined into one. |
| [`hand-zipped.mdz`](samples/hand-zipped.mdz) | No `manifest.json`, plus a `README.md`. The entry point is `notes.md`, not `README.md`. |
| [`keep-on-save.mdz`](samples/keep-on-save.mdz) | Edit, save, and check that unknown files and unknown manifest fields survive. |

### Step 2: Validate what your app writes

Install the [`mdz` command line](https://github.com/mdzip-project/mdzip-cli#installation)
(Windows, macOS and Linux), then check every kind of file your app writes:
a new document, a document with images, and an existing file after editing
and saving it.

```sh
mdz validate my-file.mdz     # exit code 0 = valid; errors use the spec's ERR_ codes
mdz inspect my-file.mdz      # shows the resolved entry point, mode and manifest
mdz ls my-file.mdz --long    # lists every entry
```

Aim for no errors and no warnings. A note (for example "no `manifest.json`")
on a file your app only opened is fine; on a file your app created, it isn't.

To check the "keep what you don't recognize" rules, list `keep-on-save.mdz`
before and after saving it in your app and compare.

### Step 3: Run the conformance fixtures

The [`fixtures/`](../fixtures/README.md) folder is the automated version:
archives and JSON case files with expected results, used by every MDZip
implementation's test suite. It includes broken and hostile archives that the
samples deliberately don't. Copy them from a released tag with
`tools/sync-fixtures.mjs` and run the ones that match your roles:

| Your role | Fixture checks |
|-----------|----------------|
| Consumer (all) | `T-001`–`T-015`, `T-017` |
| Rendering consumer | also `T-016` (hostile content) |
| Producer: creation | `P-001`, `P-006`, `P-007` |
| Producer: modification | `P-002`–`P-008` (the round-trip checks are `P-004` and `P-005`) |

If you build on an MDZip core library instead of your own ZIP and manifest
code, the library already runs these fixtures; you then mostly need steps 1
and 2. The libraries are listed on [mdzip.org](https://mdzip.org/works-with.html).

### Step 4 (optional): Have an AI coding assistant write the fixture tests

Writing a harness for every case file is mechanical work that AI coding
assistants do well, as long as they're kept from the usual shortcuts: testing
a reimplementation instead of your app's code, or changing an expected result
to make a test pass. Paste this prompt into your assistant from your
project's folder:

<!-- On the next spec release, update the version and URLs below: after
     v1.2.0, the fixtures are in fixtures/ and the catalog in fixtures/README.md. -->

```text
Add MDZip conformance tests to this project, using the official spec fixtures.

Spec version: 1.2.0
Requirements (authoritative):
  https://github.com/mdzip-project/mdzip-spec/blob/v1.2.0/SPEC.md
Fixtures:
  https://github.com/mdzip-project/mdzip-spec/tree/v1.2.0/examples/fixtures
Catalog of the T- and P- checks and their expected results:
  https://github.com/mdzip-project/mdzip-spec/blob/v1.2.0/tests/README.md

1. Copy the fixtures into this project's test folder from the v1.2.0 tag.
   If Node is available, clone the spec repo at that tag outside this
   project and run its tools/sync-fixtures.mjs <test-fixtures-dir> --ref v1.2.0,
   which also writes a SPEC-FIXTURES.json marker. Tests must read the copied
   files, never the network.
2. Work out which roles this project plays: opening .mdz files (consumer),
   creating new ones, saving changes to existing ones, rendering Markdown to
   HTML. Write tests only for the T- and P- checks that apply, and list the
   ones you skip with the reason.
3. Test the project's real code: the same functions it uses to open and save
   files. If it has more than one way to save, test each one. Don't write a
   separate ZIP or manifest reader for the tests; building input archives
   with a ZIP library is fine. If the code that a check needs isn't
   reachable from a test, say so instead of working around it.
4. Make the tests data-driven: one test per case in each *-cases.json file,
   named by the case's id (or its name, where it has no id), so cases added
   in a later spec version are picked up.
5. Never change an expected result, or skip or loosen a test, to make it
   pass. If a fixture looks wrong, check SPEC.md; if they disagree, SPEC.md
   governs. List it so it can be reported to the spec repository.
6. Don't change the project's own code in this task. Run the tests and finish
   with a table: check or case id, pass / fail / skipped, and for each failure
   the spec section it violates and what the code did instead.
```

Review the tests it writes before trusting a green result: check that they
call your app's code and that failures name a real requirement.

## 4. Common mistakes

- **Opening `README.md` as the document.** It is a support file and is set aside during entry point discovery.
- **Falling back silently** when `entryPoint` names a file that isn't there. Show an error or a visible warning.
- **Losing unknown content on save**: rebuilding the archive from only the files your app knows, or serializing a typed manifest model that drops unknown fields.
- **Lowercasing or otherwise renaming files**, which breaks case-sensitive links.
- **Backslashes or absolute paths** in entry names, often from building names with the platform's path functions on Windows.
- **No UTF-8 flag** on non-ASCII names, so other tools show them garbled.
- **Always writing ZIP64.** Some ZIP libraries add ZIP64 records to every archive by default; the specification allows them only when an archive needs them (over 4 GB or 65,535 entries).
- **Comparing paths without NFC normalization.** File names can arrive decomposed (NFD), for example from HFS+ volumes on macOS or from other apps; normalize to NFC before writing and before comparing.
- **Clamping `..` at the archive root**, so `../../x.png` silently becomes `x.png`. A link that climbs above the root is unresolved (or, if you support it, points outside the archive).
- **Rendering archive HTML with scripts enabled**, or loading remote images automatically.

## 5. If your app also reads other `.mdz` formats

MDZip isn't the only format that uses the `.mdz` extension. At least one other
also uses a ZIP archive with a root `index.md` and a `manifest.json`, so the
file names alone don't tell you which format you have. Other formats use
different containers, such as 7z. If your app supports more than one, these
rules keep MDZip files working:

- **Only a ZIP archive can be MDZip.** Check the container first.
- **A `manifest.json` with a `spec` object containing `spec.version` is MDZip.**
- **No manifest, or a manifest without `spec.version`, can still be MDZip.**
  Hand-made archives often have neither, and consumers must accept them
  ([§11.3](../SPEC.md#113-manifests-without-version-metadata)). Pick another
  format only on positive evidence, such as fields MDZip doesn't define used
  the way that format's specification describes them. When in doubt, open the
  file as MDZip: its rules ignore fields they don't recognize, and fall back to
  `index.md` when there is no `entryPoint`.
- **Watch for field names that mean something else.** In MDZip, a top-level
  `version` is the version of the *document*, not of a format; the format
  version is `spec.version`. Another format's `version` field in the
  same position means its format version.
- **Save in the format you opened**, unless the user chooses to convert. When
  converting to MDZip, write a new MDZip manifest (`spec.version`,
  `entryPoint`, `title`, `mode`) rather than renaming the old one's fields.
  Fields from the other format that have no MDZip meaning may be kept as
  unknown fields.
- **Encrypted or password-protected archives are not MDZip**
  ([§4](../SPEC.md#4-file-format)), and MDZip apps aren't expected to open them. If your app
  offers encrypted output, tell the user that other MDZip apps won't open it,
  and don't describe it as MDZip.

A listing on mdzip.org covers your app's MDZip support only. Supporting other
formats as well is fine.

## 6. Getting listed on mdzip.org

[mdzip.org](https://mdzip.org/works-with.html) lists apps and tools that work
with `.mdz` files. To be listed, an app needs:

1. A public download or product page.
2. A statement of which roles it supports (open, create, save changes), and which optional features (project mode, links outside the archive).
3. Conformance with the specification for those roles: the required items in [section 2](#2-required-recommended-and-optional) for each role it plays.
4. Archives it creates or saves that pass `mdz validate` with no errors, including `keep-on-save.mdz` after an edit and save.

Conformance is self-assessed: go through the checklist and tests above and say
which version of the specification you checked against. Known gaps are fine to
mention; the listing can say what's supported.

To ask for a listing,
[open an issue](https://github.com/mdzip-project/mdzip-spec/issues) with the
app's name, link, roles and the specification version you tested.

## 7. Questions and feedback

If a requirement is unclear, a sample or fixture looks wrong, or the
specification makes something hard to implement, please
[open an issue](https://github.com/mdzip-project/mdzip-spec/issues) or ask in
[Q&A](https://github.com/mdzip-project/mdzip-spec/discussions/categories/q-a).
Feedback from implementers is how the specification improves.
