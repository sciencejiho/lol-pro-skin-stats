import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { copyFileSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { parseCsv, writeCsv } from './csv.mjs';

const source = 'data/worlds/2025-main-event';
const script = 'scripts/import-reviewed-picks.mjs';

function fixture() {
  const dir = mkdtempSync(join(tmpdir(), 'worlds-reviewed-picks-'));
  for (const file of ['picks.csv', 'skin-evidence.json', 'games.csv',
    'roster.json', 'vods.json']) {
    copyFileSync(join(source, file), join(dir, file));
  }
  const rows = parseCsv(readFileSync(join(dir, 'picks.csv'), 'utf8'));
  const header = rows[0];
  const game = header.indexOf('game_id');
  const champion = header.indexOf('champion_id');
  const row = rows.find((cells) => cells[game] === 'LOLTMNT01_297691'
    && cells[champion] === 'Vi');
  assert.ok(row);
  return { dir, rows, row, header };
}

function run(dir) {
  return spawnSync(process.execPath, [script, '--data-dir', dir], {
    cwd: process.cwd(), encoding: 'utf8',
  });
}

function validate(dir) {
  return spawnSync(process.execPath, ['scripts/validate.mjs', '--data-dir', dir], {
    cwd: process.cwd(), encoding: 'utf8',
  });
}

test('imports one sourced CSV edit into evidence without changing existing claims', () => {
  const { dir, rows, row, header } = fixture();
  try {
    row[header.indexOf('skin')] = 'PROJECT: Vi';
    row[header.indexOf('source_url')] = 'https://www.youtube.com/watch?v=7WO9NOl-ASg&t=600s';
    writeFileSync(join(dir, 'picks.csv'), writeCsv(rows));
    const original = JSON.parse(readFileSync(join(dir, 'skin-evidence.json'), 'utf8'));
    const result = run(dir);
    assert.equal(result.status, 0, result.stderr);
    const updated = JSON.parse(readFileSync(join(dir, 'skin-evidence.json'), 'utf8'));
    assert.deepEqual(updated.records.slice(0, original.records.length), original.records);
    assert.deepEqual(updated.records.at(-1), {
      gameId: 'LOLTMNT01_297691', championId: 'Vi', player: 'Hizto',
      skin: 'PROJECT: Vi',
      sourceUrl: 'https://www.youtube.com/watch?v=7WO9NOl-ASg&t=600s',
      method: 'manual_review',
    });
    assert.equal(run(dir).status, 0);
    assert.equal(validate(dir).status, 0);
    assert.equal(JSON.parse(readFileSync(join(dir, 'skin-evidence.json'), 'utf8'))
      .records.length, original.records.length + 1);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('validation rejects a CSV skin omitted from the evidence overlay', () => {
  const { dir, rows, row, header } = fixture();
  try {
    row[header.indexOf('skin')] = 'PROJECT: Vi';
    row[header.indexOf('source_url')] = 'https://www.youtube.com/watch?v=7WO9NOl-ASg&t=600s';
    writeFileSync(join(dir, 'picks.csv'), writeCsv(rows));
    const result = validate(dir);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Missing skin evidence/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('rejects an unsourced CSV skin without modifying evidence', () => {
  const { dir, rows, row, header } = fixture();
  try {
    row[header.indexOf('skin')] = 'PROJECT: Vi';
    writeFileSync(join(dir, 'picks.csv'), writeCsv(rows));
    const before = readFileSync(join(dir, 'skin-evidence.json'), 'utf8');
    const result = run(dir);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /source_url/);
    assert.equal(readFileSync(join(dir, 'skin-evidence.json'), 'utf8'), before);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('rejects a skin entered against an unknown game pick before writing evidence', () => {
  const { dir, rows, row, header } = fixture();
  try {
    row[header.indexOf('game_id')] = 'LOLTMNT01_UNKNOWN';
    row[header.indexOf('skin')] = 'PROJECT: Vi';
    row[header.indexOf('source_url')] = 'https://www.youtube.com/watch?v=7WO9NOl-ASg&t=600s';
    writeFileSync(join(dir, 'picks.csv'), writeCsv(rows));
    const before = readFileSync(join(dir, 'skin-evidence.json'), 'utf8');
    const result = run(dir);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Unknown game pick/);
    assert.equal(readFileSync(join(dir, 'skin-evidence.json'), 'utf8'), before);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
