#!/usr/bin/env node
// Copy the spec's shared fixtures (fixtures/) from a released spec tag into
// an implementation's test folder, and record what was copied. Tags up to
// v1.2.0 kept them in examples/fixtures/; the tool reads either layout.
//
//   node tools/sync-fixtures.mjs <target-dir> [--ref v1.2.1]
//   node tools/sync-fixtures.mjs <target-dir> --working-tree
//   node tools/sync-fixtures.mjs <target-dir> --check
//
// Sync writes every fixture file at <ref> into <target-dir> and a marker,
// SPEC-FIXTURES.json, with the ref, its commit and each file's SHA-256. Files
// in <target-dir> that aren't spec fixtures (an implementation's own extra
// cases) are left alone; spec fixtures removed since the last sync are
// deleted.
//
// --working-tree copies the fixtures as they are on disk in this checkout,
// including uncommitted changes, for testing an implementation against a
// spec draft. The marker records "working-tree" instead of a commit.
//
// --check verifies <target-dir> against its marker and exits non-zero on any
// difference, so an implementation's tests or CI can catch a hand-edited or
// stale copy. It doesn't need this repository: it only reads the marker.
//
// Pin implementations to a released tag, not a branch: fixtures on a draft
// branch describe rules implementations may not support yet.

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const MARKER = 'SPEC-FIXTURES.json';
// Newest layout first. Only files directly in the folder are fixtures; its
// src/ subfolder (the archives' source folders) is never copied.
const FIXTURE_DIRS = ['fixtures', 'examples/fixtures'];
const specRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const args = process.argv.slice(2);
const refAt = args.indexOf('--ref');
const ref = refAt >= 0 ? args[refAt + 1] : null;
const target = args.find((a, i) => !a.startsWith('--') && !(refAt >= 0 && i === refAt + 1));
const check = args.includes('--check');
const workingTree = args.includes('--working-tree');

if (!target || (refAt >= 0 && !ref) || (workingTree && ref)) {
  console.error(
    'usage: node tools/sync-fixtures.mjs <target-dir> [--ref <tag> | --working-tree]\n' +
      '       node tools/sync-fixtures.mjs <target-dir> --check'
  );
  process.exit(2);
}

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const git = (...a) => execFileSync('git', ['-C', specRoot, ...a], { maxBuffer: 256 * 1024 * 1024 });

if (check) {
  const markerPath = join(target, MARKER);
  if (!existsSync(markerPath)) {
    console.error(`No ${MARKER} in ${target}; run a sync first.`);
    process.exit(1);
  }
  const marker = JSON.parse(readFileSync(markerPath, 'utf8'));
  const problems = [];
  for (const [name, expected] of Object.entries(marker.files)) {
    const p = join(target, name);
    if (!existsSync(p)) problems.push(`missing: ${name}`);
    else if (sha256(readFileSync(p)) !== expected) problems.push(`changed: ${name}`);
  }
  if (problems.length) {
    console.error(`Fixtures in ${target} differ from spec ${marker.ref}:\n  ${problems.join('\n  ')}`);
    process.exit(1);
  }
  console.log(`Fixtures in ${target} match spec ${marker.ref} (${Object.keys(marker.files).length} files).`);
  process.exit(0);
}

let useRef;
let commit;
let names;
let read;
if (workingTree) {
  useRef = 'working-tree';
  commit = 'working-tree';
  const dir = FIXTURE_DIRS[0];
  names = readdirSync(join(specRoot, dir), { withFileTypes: true })
    .filter((d) => d.isFile())
    .map((d) => d.name);
  read = (name) => readFileSync(join(specRoot, dir, name));
} else {
  useRef = ref ?? 'HEAD';
  if (!ref) console.warn('No --ref given; using HEAD. Pin implementations to a released tag (e.g. --ref v1.2.1).');
  commit = git('rev-parse', `${useRef}^{commit}`).toString().trim();
  const listAt = (dir) =>
    git('ls-tree', '-r', '--name-only', commit, `${dir}/`)
      .toString()
      .split('\n')
      .filter(Boolean)
      .map((p) => p.slice(dir.length + 1));
  const dir = FIXTURE_DIRS.find((d) => listAt(d).length > 0);
  if (!dir) {
    console.error(`No fixtures at ${useRef}: none of ${FIXTURE_DIRS.join(', ')} exists there.`);
    process.exit(1);
  }
  names = listAt(dir);
  read = (name) => git('show', `${commit}:${dir}/${name}`);
}
names = names.filter((n) => n !== 'README.md' && !n.includes('/')).sort();

mkdirSync(target, { recursive: true });
const previous = existsSync(join(target, MARKER)) ? JSON.parse(readFileSync(join(target, MARKER), 'utf8')) : null;
const files = {};
for (const name of names) {
  const data = read(name);
  writeFileSync(join(target, name), data);
  files[name] = sha256(data);
}
for (const name of Object.keys(previous?.files ?? {})) {
  if (!(name in files)) rmSync(join(target, name), { force: true });
}
const marker = {
  source: 'https://github.com/mdzip-project/mdzip-spec',
  ref: useRef,
  commit,
  note: 'Copied by mdzip-spec tools/sync-fixtures.mjs. Do not edit these files by hand; add implementation-specific cases in separate files.',
  files,
};
writeFileSync(join(target, MARKER), JSON.stringify(marker, null, 2) + '\n');
const where = workingTree ? 'the working tree' : `${useRef} (${commit.slice(0, 7)})`;
console.log(`Synced ${names.length} fixture files from spec ${where} into ${target}.`);
