import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

import { parseCsv } from './csv.mjs';

const dir = 'data/worlds/2025-main-event';
const roster = JSON.parse(readFileSync(`${dir}/roster.json`, 'utf8'));
const evidence = JSON.parse(readFileSync(`${dir}/skin-evidence.json`, 'utf8'));

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
assert.equal(evidence.records.length, 156);
const gamesById = new Map(games.map((game) => [game.game_id, game]));
assert.equal(gamesById.size, 80);
const picksByKey = new Map(picks.map((pick) =>
  [`${pick.game_id}:${pick.champion_id}`, pick]));
assert.equal(picksByKey.size, 800);

for (const match of roster.games) {
  const game = gamesById.get(match.id);
  assert.ok(game, `Missing VOD for ${match.id}`);
  assert.equal(game.date, match.date);
  assert.match(game.youtube_url, /^https:\/\/www\.youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}$/);
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

for (const record of evidence.records) {
  const pick = picksByKey.get(`${record.gameId}:${record.championId}`);
  assert.ok(pick);
  assert.equal(pick.player, record.player);
  assert.equal(pick.skin, record.skin);
  assert.equal(pick.source_url, record.sourceUrl);
}
console.log('Validated 80 games, 800 picks, 156 sourced skins, and 80 YouTube links');
