import { readFileSync, writeFileSync } from 'node:fs';

import { parseCsv, writeCsv } from './csv.mjs';

const BASE = 'https://esports-api.lolesports.com/persisted/gw';
// Public browser key used by the LoL Esports website. No user credentials.
const API_KEY = '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z';
const DIRECTORY = 'data/worlds/2025-main-event';
const ROSTER = `${DIRECTORY}/roster.json`;
const PICKS = `${DIRECTORY}/picks.csv`;
const GAMES = `${DIRECTORY}/games.csv`;
const VIDEO_ID = /^[A-Za-z0-9_-]{11}$/;

async function get(path, parameters) {
  const url = new URL(`${BASE}/${path}`);
  url.search = new URLSearchParams({ hl: 'en-US', ...parameters });
  for (let attempt = 0; attempt < 3; attempt += 1) {
    const response = await fetch(url, {
      headers: { 'x-api-key': API_KEY }, signal: AbortSignal.timeout(15000),
    });
    if (response.ok) return response.json();
    if (![429, 500, 502, 503, 504].includes(response.status)) {
      throw new Error(`${path}: HTTP ${response.status}`);
    }
    await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
  }
  throw new Error(`${path}: transient failure after three attempts`);
}

function normalizeTeam(name) {
  return (name === 'Gen.G Esports' ? 'Gen.G' : name).toLowerCase();
}

function matchKey(date, teams, number) {
  return `${date}|${teams.map(normalizeTeam).sort().join('|')}|${number}`;
}

const snapshot = JSON.parse(readFileSync(ROSTER, 'utf8'));
if (snapshot.games.length !== 80) throw new Error('Expected 80 Main Event games');
const rosterByKey = new Map();
const numbersBySeries = new Map();
for (const game of snapshot.games) {
  const teams = [...new Set(game.picks.map((pick) => pick.team))];
  if (game.picks.length !== 10 || teams.length !== 2) {
    throw new Error(`Invalid game roster: ${game.id}`);
  }
  const series = matchKey(game.date, teams, 0);
  const number = (numbersBySeries.get(series) ?? 0) + 1;
  numbersBySeries.set(series, number);
  const key = matchKey(game.date, teams, number);
  if (rosterByKey.has(key)) throw new Error(`Duplicate roster key: ${key}`);
  rosterByKey.set(key, { game, teams, number });
}

const tournaments = await get('getTournamentsForLeague', {
  leagueId: '98767975604431411',
});
const tournament = tournaments.data.leagues.flatMap((league) => league.tournaments)
  .find(({ slug }) => slug === 'worlds_2025');
if (!tournament) throw new Error('Worlds 2025 tournament not found');
const completed = await get('getCompletedEvents', { tournamentId: tournament.id });
const events = completed.data.schedule.events.filter(({ startTime }) =>
  startTime.slice(0, 10) >= '2025-10-15');
const details = [];
for (let index = 0; index < events.length; index += 4) {
  const batch = await Promise.all(events.slice(index, index + 4).map((event) =>
    get('getEventDetails', { id: event.match.id })));
  details.push(...batch);
}

const vodByGame = new Map();
for (let index = 0; index < events.length; index += 1) {
  const event = events[index];
  const detail = details[index].data.event;
  if (!detail || detail.id !== event.match.id) {
    throw new Error(`Missing event detail: ${event.match.id}`);
  }
  const date = event.startTime.slice(0, 10);
  const teams = detail.match.teams.map(({ name }) => name);
  for (const game of detail.match.games.filter(({ state }) => state === 'completed')) {
    const key = matchKey(date, teams, game.number);
    const roster = rosterByKey.get(key);
    if (!roster || vodByGame.has(roster.game.id)) {
      throw new Error(`Official VOD cannot be paired to one roster game: ${key}`);
    }
    const vod = game.vods.find(({ provider, locale, parameter }) =>
      provider === 'youtube' && locale === 'en-US' && VIDEO_ID.test(parameter));
    if (!vod) throw new Error(`No English YouTube VOD for ${key}`);
    const videoId = vod.parameter;
    vodByGame.set(roster.game.id, {
      videoId,
      youtubeUrl: `https://www.youtube.com/watch?v=${videoId}`,
      lolesportsUrl: `https://lolesports.com/en-US/vod/${event.match.id}/${game.number}/${videoId}`,
      matchId: event.match.id,
      esportsGameId: game.id,
    });
  }
}
if (vodByGame.size !== 80) {
  throw new Error(`Expected 80 matched VODs, found ${vodByGame.size}`);
}

const gameRows = [[
  'date', 'game_id', 'series_game', 'team_a', 'team_b', 'youtube_url',
  'lolesports_url', 'lolesports_match_id', 'lolesports_game_id',
]];
for (const game of snapshot.games) {
  const { teams, number } = [...rosterByKey.values()]
    .find((row) => row.game.id === game.id);
  const vod = vodByGame.get(game.id);
  gameRows.push([
    game.date, game.id, number, ...teams, vod.youtubeUrl, vod.lolesportsUrl,
    vod.matchId, vod.esportsGameId,
  ]);
}
writeFileSync(GAMES, writeCsv(gameRows));

const rows = parseCsv(readFileSync(PICKS, 'utf8'));
const header = rows.shift();
const gameIdIndex = header.indexOf('game_id');
if (gameIdIndex === -1 || rows.length !== 800) {
  throw new Error('Expected 800 pick rows with game IDs');
}
for (const column of ['chroma_status', 'chroma', 'chroma_source_url', 'youtube_url']) {
  if (!header.includes(column)) header.push(column);
}
const position = Object.fromEntries(header.map((name, offset) => [name, offset]));
for (const row of rows) {
  const vod = vodByGame.get(row[gameIdIndex]);
  if (!vod) throw new Error(`No VOD for pick: ${row[gameIdIndex]}`);
  row[position.chroma_status] ??= 'unreviewed';
  row[position.chroma] ??= '';
  row[position.chroma_source_url] ??= '';
  row[position.youtube_url] = vod.youtubeUrl;
}
const orderedColumns = [
  'date', 'game_id', 'series_game', 'side', 'team', 'opponent',
  'player', 'champion_id', 'champion', 'skin', 'source_url',
  'chroma_status', 'chroma', 'chroma_source_url', 'youtube_url',
];
if (header.length !== orderedColumns.length
  || orderedColumns.some((column) => !(column in position))) {
  throw new Error('Unexpected pick CSV columns');
}
writeFileSync(PICKS, writeCsv([
  orderedColumns,
  ...rows.map((row) => orderedColumns.map((column) => row[position[column]] ?? '')),
]));
console.log(`Matched ${vodByGame.size} official English YouTube VODs to ${rows.length} picks`);
