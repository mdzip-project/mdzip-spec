# Contributing

Thanks for helping improve the Markdown Zip (`.mdz`) specification.

## Scope

- Normative requirements belong in [SPEC.md](SPEC.md).
- Non-normative rationale belongs in [`reference/`](reference/README.md).
- Example package structures belong in [`examples/`](examples/README.md).
- Conformance expectations belong in [`tests/`](tests/README.md).

## Change Process

1. Open an issue describing the change and rationale.
2. Submit a pull request with focused edits.
3. Update related examples/tests when normative behavior changes.
4. Add an entry in [CHANGELOG.md](CHANGELOG.md).

## Editorial Rules

- Use RFC 2119 terms consistently (`MUST`, `SHOULD`, `MAY`).
- Keep requirements implementation-neutral.
- Avoid feature creep; prefer minimal, interoperable behavior.
- Keep examples deterministic and cross-platform.

## Versioning Policy

- Spec versions follow Semantic Versioning.
- Breaking format changes require a major version bump.
- Backward-compatible additions/clarifications require a minor bump.
- Editorial fixes require a patch bump.
