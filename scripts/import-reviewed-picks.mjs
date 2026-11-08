import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

import { parseCsv } from './csv.mjs';

const DEFAULT_DIR = 'data/worlds/2025-main-event';
const columns = ['game_id', 'champion_id', 'player', 'skin', 'source_url'];
const args = process.argv.slice(2);
if (args.length !== 0 && (args.length !== 2 || args[0] !== '--data-dir')) {
  throw new Error('Usage: node scripts/import-reviewed-picks.mjs [--data-dir directory]');
}
const dir = args.length === 2 ? args[1] : DEFAULT_DIR;
const csv = parseCsv(readFileSync(join(dir, 'picks.csv'), 'utf8'));
const [header, ...rows] = csv;
if (rows.length !== 800 || columns.some((name) => !header.includes(name))
  || rows.some((row) => row.length !== header.length)) {
  throw new Error('Expected 800 complete pick rows with skin and source columns');
}
const field = Object.fromEntries(columns.map((name) => [name, header.indexOf(name)]));
const roster = JSON.parse(readFileSync(join(dir, 'roster.json'), 'utf8'));
const rosterPicks = new Map(roster.games.flatMap((game) => game.picks.map((pick) => (
  [`${game.id}:${pick.championId}`, pick]
))));
if (rosterPicks.size !== 800) throw new Error('Expected 800 unique roster picks');
const evidencePath = join(dir, 'skin-evidence.json');
const evidence = JSON.parse(readFileSync(evidencePath, 'utf8'));
if (!Array.isArray(evidence.records)) throw new Error('Skin evidence records are missing');
const known = new Map();
for (const record of evidence.records) {
  const key = `${record.gameId}:${record.championId}`;
  if (known.has(key)) throw new Error(`Duplicate skin evidence: ${key}`);
  known.set(key, record);
}
const seen = new Set();
const additions = [];
for (const row of rows) {
  const gameId = row[field.game_id];
  const championId = row[field.champion_id];
  const player = row[field.player];
  const skin = row[field.skin].trim();
  const sourceUrl = row[field.source_url].trim();
  const key = `${gameId}:${championId}`;
  if (!gameId || !championId || !player || seen.has(key)) {
    throw new Error(`Invalid or duplicate pick: ${key}`);
  }
  seen.add(key);
  if (rosterPicks.get(key)?.player !== player) {
    throw new Error(`Unknown game pick or player: ${key}`);
  }
  const previous = known.get(key);
  if (previous) {
    if (previous.player !== player || previous.skin !== skin
      || previous.sourceUrl !== sourceUrl) {
      throw new Error(`CSV conflicts with existing skin evidence: ${key}`);
    }
    continue;
  }
  if (!skin && !sourceUrl) continue;
  if (!skin || !/^https:\/\/\S+$/.test(sourceUrl)) {
    throw new Error(`Skin and https source_url are required together: ${key}`);
  }
  additions.push({ gameId, championId, player, skin, sourceUrl,
    method: 'manual_review' });
}
if (additions.length > 0) {
  evidence.records.push(...additions);
  writeFileSync(evidencePath, `${JSON.stringify(evidence, null, 2)}\n`);
}
console.log(`Imported ${additions.length} reviewed picks; ${evidence.records.length} sourced skins total`);
