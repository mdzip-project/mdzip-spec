# Manifest Metadata Draft (Discussion Notes)

Status: draft notes captured from design discussion.  
Scope: non-normative (for review before updating `SPEC.md`).

## Summary

We are moving away from a single manifest version property (for example, `mdz`) toward structured metadata that separates:

- compatibility target (`spec`)
- producer provenance (`producer`) with distinct application and core-library versions
- optional human attribution (`author`)

## Proposed Manifest Shape

```json
{
  "spec": {
    "name": "mdzip-spec",
    "version": "1.0.1"
  },
  "producer": {
    "application": {
      "name": "mdzip-cli",
      "version": "1.0.0-beta.3",
      "url": "https://example.com/mdzip-cli"
    },
    "core": {
      "name": "mdzip-core",
      "version": "0.8.2",
      "url": "https://example.com/mdzip-core"
    }
  },
  "author": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "url": "https://example.com/~jane"
  }
}
```

## Field Intent

- `spec`: compatibility anchor for the archive format/specification.
- `producer.application`: user-facing tool/application that generated the archive.
- `producer.core`: underlying producer library/runtime used by the application.
- `author`: optional human/content author metadata.
- `url`: optional discovery/provenance URL for `producer.application`, `producer.core`, and `author`.
- `author.email`: optional contact address for human/content author attribution.
- `modified`: draft transitional field that MAY be either an ISO 8601 string or an object (`when`, optional `by`).
- `created`: draft transitional field aligned with `modified`; MAY be either an ISO 8601 string or an object (`when`, optional `by`) for symmetry.

Rationale for split versions:

- application releases and core-library releases are often decoupled;
- troubleshooting and provenance are easier when both version tracks are preserved;
- this avoids overloading a single `producer.version` value with ambiguous meaning.

## Conformance Direction (Current Consensus)

Important boundary: these rules target conforming producer implementations, not all hand-authored manifests.

- A conforming producer MUST include `spec.version` when it writes `manifest.json`.
- A conforming producer SHOULD include `producer.application.name` and `producer.application.version`.
- A conforming producer SHOULD include `producer.application.url` when a stable project/product URL exists.
- A conforming producer SHOULD include `producer.core.name` and `producer.core.version` when a reusable core library/runtime is part of the build pipeline.
- A conforming producer SHOULD include `producer.core.url` when a stable project/library URL exists.
- A conforming producer SHOULD include `author.url` and `author.email` when that metadata is available and appropriate to disclose.
- During draft `1.0.x`, a conforming consumer MUST accept `modified` as either a string (legacy draft form) or object form (`modified.when`, optional `modified.by`).
- During draft `1.0.x`, a conforming consumer should accept `created` as either a string (legacy draft form) or object form (`created.when`, optional `created.by`).
- Manifests that are hand-authored (or otherwise not created by a conforming producer) MAY omit `spec.version`.

## Consumer Behavior Direction

- Consumers MUST NOT assume `manifest.json` was producer-generated.
- If `spec.version` is present, consumers validate compatibility against supported version/range behavior.
- If `spec.version` is absent, consumers treat version as unknown and apply fallback handling (for example, default discovery/compatibility behavior, warning policy, or profile-defined handling).
- Consumers SHOULD ignore unknown manifest fields for forward compatibility.

## Manifest Optionality

- `manifest.json` remains optional at the archive level.
- Producer requirements above apply only when a conforming producer chooses to emit `manifest.json`.

## Spec Scope Boundary

In the normative spec, define observable behavior (`MUST`/`SHOULD`/`MAY`) for producers and consumers.
Do not require internal architecture (for example, how a core library stores or passes version values internally).

## Terminology Alignment Note (Draft)

Use `producer` as the standards-style role term in normative specification text.
Use `create` as an implementation/API action term in library and application interfaces.

Recommended mapping:

- a `create` method or command is a producer operation;
- code-level language can use `create` while spec conformance language continues to use `producer`.

## Implementation Guidance (Non-Normative)

Core libraries can expose supported spec version/range so that applications can stamp `spec.version` consistently and avoid drift.

When both layers are versioned independently, applications should stamp both `producer.application.version` and `producer.core.version` to preserve reproducibility.

## Migration Note (Draft)

When migrating from legacy manifests with a single version field (for example, `"mdz": "x.y.z"`), map that value to `spec.version` in generated manifests.

## Schema Direction (Draft)

Given increasing manifest complexity, define a versioned JSON Schema as a machine-readable companion to the spec.

Suggested starting point:

- `schema/manifest-1.0.1-draft.schema.json`
- link from `SPEC.md` Section 6 when promoted from notes to normative text
- include draft `modified` dual-form support (`string` OR object with required `when`, optional `by`)
- include symmetric draft `created` dual-form support to match `modified`
- keep forward-compatibility posture (`additionalProperties: true` / unknown fields tolerated)

Draft intent: keep normative behavior in the prose spec, and use schema for deterministic validation/tooling.

