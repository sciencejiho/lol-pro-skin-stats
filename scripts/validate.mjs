import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

import { parseCsv } from './csv.mjs';

const args = process.argv.slice(2);
assert.ok(args.length === 0 || (args.length === 2 && args[0] === '--data-dir'),
  'Usage: node scripts/validate.mjs [--data-dir directory]');
const dir = args.length === 2 ? args[1] : 'data/worlds/2025-main-event';
const roster = JSON.parse(readFileSync(`${dir}/roster.json`, 'utf8'));
const evidence = JSON.parse(readFileSync(`${dir}/skin-evidence.json`, 'utf8'));
const vods = JSON.parse(readFileSync(`${dir}/vods.json`, 'utf8'));
const aggregate = JSON.parse(readFileSync(`${dir}/observer-aggregate-reference.json`, 'utf8'));

function readRows(file) {
  const [header, ...cells] = parseCsv(readFileSync(`${dir}/${file}`, 'utf8'));
  assert.ok(header?.length > 0, `${file}: missing header`);
  for (const row of cells) assert.equal(row.length, header.length, `${file}: column count`);
  return cells.map((row) => Object.fromEntries(header.map((name, index) => [name, row[index]])));
}

const games = readRows('games.csv');
const picks = readRows('picks.csv');
assert.equal(roster.games.length, 80);
assert.equal(games.length, 80);
assert.equal(picks.length, 800);
assert.ok(evidence.records.length <= 800);
assert.equal(vods.records.length, 80);
const gamesById = new Map(games.map((game) => [game.game_id, game]));
assert.equal(gamesById.size, 80);
assert.equal(new Set(games.map((game) => game.youtube_url)).size, 80);
const vodsById = new Map(vods.records.map((record) => [record.gameId, record.youtubeUrl]));
assert.equal(vodsById.size, 80);
const picksByKey = new Map(picks.map((pick) =>
  [`${pick.game_id}:${pick.champion_id}`, pick]));
assert.equal(picksByKey.size, 800);

for (const match of roster.games) {
  const game = gamesById.get(match.id);
  assert.ok(game, `Missing VOD for ${match.id}`);
  assert.equal(game.date, match.date);
  assert.match(game.youtube_url, /^https:\/\/www\.youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}$/);
  assert.equal(vodsById.get(match.id), game.youtube_url);
  assert.match(game.lolesports_url, /^https:\/\/lolesports\.com\/en-US\/vod\//);
  const teams = new Set(match.picks.map((pick) => pick.team));
  assert.deepEqual(new Set([game.team_a, game.team_b]), teams);
  assert.ok(Number.isInteger(Number(game.series_game)) && Number(game.series_game) >= 1);
  for (const appearance of match.picks) {
    const pick = picksByKey.get(`${match.id}:${appearance.championId}`);
    assert.ok(pick, `Missing pick: ${match.id}:${appearance.championId}`);
    assert.equal(pick.date, match.date);
    assert.equal(pick.series_game, game.series_game);
    assert.equal(pick.team, appearance.team);
    assert.equal(pick.opponent, appearance.opponent);
    assert.equal(pick.side, appearance.side);
    assert.equal(pick.player, appearance.player);
    assert.equal(pick.youtube_url, game.youtube_url);
    assert.ok(pick.champion);
    assert.ok(['unreviewed', 'default', 'variant', 'unavailable', 'uncertain']
      .includes(pick.chroma_status));
    if (pick.chroma_status === 'variant') assert.ok(pick.chroma);
    if (pick.chroma_status !== 'unreviewed') {
      assert.match(pick.chroma_source_url, /^https:\/\//);
    }
  }
}

const evidenceByKey = new Map();
for (const record of evidence.records) {
  const key = `${record.gameId}:${record.championId}`;
  assert.ok(!evidenceByKey.has(key), `Duplicate skin evidence: ${key}`);
  evidenceByKey.set(key, record);
  const pick = picksByKey.get(key);
  assert.ok(pick);
  assert.equal(pick.player, record.player);
  assert.equal(pick.skin, record.skin);
  assert.equal(pick.source_url, record.sourceUrl);
  assert.match(record.sourceUrl, /^https:\/\//);
  if (['all_champion_appearances_crosschecked',
    'finals_bundle_tracker_agreement', 'vod_commentary_crosschecked',
    'vod_visual_plus_bundle']
    .includes(record.method)) {
    assert.match(record.supportingSourceUrl, /^https:\/\//);
  } else {
    assert.equal(record.supportingSourceUrl, undefined);
  }
}
for (const [key, pick] of picksByKey) {
  assert.equal(Boolean(pick.skin), Boolean(pick.source_url),
    `Skin and source_url must both be set: ${key}`);
  assert.equal(Boolean(evidenceByKey.has(key)), Boolean(pick.skin),
    `Missing skin evidence or stale CSV: ${key}`);
}
assert.match(aggregate.sourceUrl, /^https:\/\//);
assert.ok(aggregate.records.length > 0);
const aggregateKeys = new Set();
for (const record of aggregate.records) {
  const key = `${record.championId}:${record.skin}`;
  assert.ok(!aggregateKeys.has(key), `Duplicate aggregate: ${key}`);
  aggregateKeys.add(key);
  assert.ok(Number.isInteger(record.uses) && record.uses > 0, `Invalid aggregate: ${key}`);
  assert.ok(roster.games.some((game) => game.picks.some((pick) =>
    pick.championId === record.championId)), `Unknown aggregate champion: ${key}`);
  const confirmedMainEventUses = evidence.records.filter((item) =>
    item.championId === record.championId && item.skin === record.skin).length;
  assert.ok(confirmedMainEventUses <= record.uses,
    `Main Event assignments exceed published 84-game total: ${key}`);
}
for (const [championId, publishedAppearances] of
  Object.entries(aggregate.completeChampionDistributions)) {
  const publishedSkinUses = aggregate.records
    .filter((record) => record.championId === championId)
    .reduce((sum, record) => sum + record.uses, 0);
  assert.equal(publishedSkinUses, publishedAppearances,
    `Incomplete published skin distribution: ${championId}`);
  const mainEventAppearances = roster.games.flatMap((game) => game.picks)
    .filter((pick) => pick.championId === championId).length;
  assert.ok(mainEventAppearances <= publishedAppearances,
    `Main Event appearances exceed published 84-game total: ${championId}`);
}
console.log(`Validated 80 games, 800 picks, ${evidence.records.length} sourced skins, and 80 YouTube links`);
