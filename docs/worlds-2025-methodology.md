# Worlds 2025 Main Event skin evidence

Unit of analysis: one champion pick in one Main Event game, identified by
`gameId + championId`. The local ChainCC-derived roster has 80 games and 800
picks. Skin selections are a separate evidence overlay; absent evidence means
unknown, never zero uses or a default skin.

The public LoL Esports feed was sampled for Main Event game
`113475798006599035` through its `getGames`, live `window`, and live `details`
responses. The game metadata includes participant champion IDs, while neither
live-statistics response contains a skin or chroma key. This is a check of one
game and these endpoints, not proof that Riot has no internal skin records; it
does mean that the public responses used for this dataset cannot supply the
missing skin choices. The [feed's documented response fields](https://vickz84259.github.io/lolesports-api-docs/)
likewise list champions, items, and runes rather than selected skins.

The [firsthand Worlds tracker](https://www.reddit.com/r/leagueoflegends/comments/1ox1hn9/fun_facts_about_skins_at_worlds_2025/)
observed the whole 84-game event, including four Play-In games. Its author
describes watching games, recognizing skins, and recording them in Excel.
The importer cross-checks every whole-event count against ChainCC before
assigning a skin to a Main Event game:

- Six champions have one skin in all their appearances: Super Galaxy Rumble
  (21/21), Classic Ambessa (19/19), Striker Ezreal (15/15), Classic Azir
  (14/14), Prestige Blood Moon Aatrox (5/5), and Corporate Mundo (5/5).
- In a comment on the same post, the observer reports four wins with Masque of
  the Black Rose Renata Glasc. ChainCC shows exactly four Renata Glasc picks in
  the full event, all wins. Thus every Renata pick used that skin; one was in
  Play-In and three were in the Main Event. One of the latter was already
  supported by the grand-final report, adding two new Main Event picks.
- The observer also names SKT T1 Elise as a used skin. Elise appeared once in
  all 84 games, so ON's Main Event pick is identified. This makes eight
  champions whose full-event appearances are covered by one named skin.
- For Kai'Sa, Xayah, and Lucian, the tracker reports a dominant skin in all
  but one appearance (17/18, 10/11, and 8/9). It separately names the only
  player who chose each alternative. Each such player used that champion
  exactly once in the whole event, so all 38 appearances can be assigned.
- The tracker names Faker and Poby as the only two players who used only base
  skins. Faker had 24 whole-event games and Poby had five. Their 20 and five
  Main Event picks respectively are base-skin selections. The separate
  mid-lane base-skin totals (75, or 51 without Faker) reconcile Faker's count.
- The post identifies skins for 21 other player/champion combinations that each
  occurred exactly once in all 84 games. Two overlap the all-champion rule.
  The T1 wardrobe list is incomplete for some champions: it omits Oner's
  finals Viego and Keria's finals Poppy, although both picks appear in the
  match roster. Its stated Keria skin total also differs from the number of
  entries in that list. A named skin there therefore establishes that it was
  used during the tournament, but does not establish that it was used in
  *every* game where that player picked the champion. Repeated picks from
  the list are not assigned without game-specific evidence.
- One of these is Canyon's Nidalee: the observer reports that Canyon used his
  own World Championship skin, and ChainCC shows only one Canyon Nidalee pick
  in the event. [Riot's Nidalee page](https://www.leagueoflegends.com/en-gb/champions/nidalee/)
  names his 2020 champion skin DWG Nidalee.
- Not every aggregate can safely identify a game. For example, the post lists
  four Secret Agent Xin Zhao uses and separately calls Canyon its only user,
  whereas ChainCC has only three Canyon Xin Zhao picks in the full event.
  This conflict is left unresolved and none of those picks is assigned from it.

These methods yield 160 sourced picks. An [esports.gg report on T1's grand-final
skins](https://esports.gg/news/league-of-legends/worlds-2025-skin-bundles/)
explicitly identifies five additional on-stage selections: T1 Varus, Neo PAX
Sivir, Classic Yunara, Hextech Renekton, and Masque of the Black Rose Renata
Glasc. The report distinguishes actual selections from the promotional store
bundles, so bundle contents alone are not treated as evidence. The five
player/champion pairs each occur once in the grand final and are joined to
their exact ChainCC game IDs.

Nine further grand-final picks have the same skin in both the report's role
bundle and the [independent observer's T1 wardrobe](https://www.reddit.com/r/leagueoflegends/comments/1ox1hn9/fun_facts_about_skins_at_worlds_2025/):
Oner's Marauder Xin Zhao, Fnatic Jarvan IV, Eternum Nocturne, and Dragonslayer
Pantheon; Keria's Winter Wonder Lulu, Cosmic Dawn Rakan, and PROJECT: Leona;
and Doran's Lumberjack Sion and Coven Camille. The bundle alone is not proof
because the report notes substitutions; agreement with the observer supplies
the second source. The observer writes "FNC Jarvan IV"; the canonical client
name is "Fnatic Jarvan IV". Oner's Viego and Keria's Poppy remain unknown
because their skins are not identified in that wardrobe list.
Each of these nine evidence records carries both `sourceUrl` (the bundle
report) and `supportingSourceUrl` (the observer's wardrobe).

Gumayusi's [post-tournament stream recap](https://www.reddit.com/r/SKTT1/comments/1p5xlhn/gumayusis_review_and_insight_of_worlds_2025_games/)
also names the skin he used as Miss Fortune in finals game five. The recap
uses its former name, Mafia Miss Fortune. [Riot's patch 10.13 notes](https://www.leagueoflegends.com/en-au/news/game-updates/patch-10-13-notes/)
confirm that its current name is Crime City Miss Fortune. This adds one
game-specific player statement.

The official English YouTube VODs expose automatic English captions. A bounded
scan of all 80 game VODs found 29 candidate uses of the word "skin"; most were
ability-name transcription errors or general discussion. Three mentions could
be joined to a specific pick:

- [Finals game four, about 16:30](https://www.youtube.com/watch?v=l47xGNAvX4M&t=990s):
  commentary explicitly identifies deokdam's Caitlyn as the DRX skin. [Riot's
  Caitlyn page](https://www.leagueoflegends.com/en-us/champions/caitlyn/)
  confirms the client name **DRX Caitlyn**.
- [G2 vs BLG, about 9:06](https://www.youtube.com/watch?v=4cnUcX2JA6A&t=546s):
  commentary refers to Caps's on-screen Anivia as the eagle skin. The
  independent [Worlds observer](https://www.reddit.com/r/leagueoflegends/comments/1ox1hn9/fun_facts_about_skins_at_worlds_2025/)
  names **Bird of Prey Anivia** among the skins used in this event; that is the
  eagle design in [Riot's Anivia catalog](https://www.leagueoflegends.com/en-gb/champions/anivia/).
- [HLE vs Gen.G, about 12:09](https://www.youtube.com/watch?v=HIkkXzh5AuI&t=729s):
  commentary points out the traffic-cone pillar when discussing the skin choice.
  Peanut is the game's only Trundle, and [contemporary PBE coverage](https://www.surrenderat20.net/2014/11/116-pbe-update.html)
  identifies that ability model as **Constable Trundle**.

These are automatic-caption leads, not separately checked audio transcripts.
The two skin-design deductions carry their second source in
`supportingSourceUrl`. A [different Rek'Sai commentary mention](https://www.youtube.com/watch?v=qJFdgnR6OY8&t=1135s)
appears to discuss Pool Party while the observer reports no Pool Party Rek'Sai
in the event; it is left unresolved and no skin is assigned from it.
The caption endpoint later returned a Google request-limit page when sampled
again; the saved scan contains only the 29 candidate passages, so a wider
transcript search requires fresh access to the official VODs.

An [esports.gg year-end skin review](https://esports.gg/news/league-of-legends/best-league-of-legends-skins-in-2025/)
also explicitly names KT PerfecT's Sahn-Uzal Mordekaiser in the grand final.
ChainCC places his only Mordekaiser pick in final game four, so that exact
game receives the reported skin.

The [official MKOI–T1 game-one VOD at 12:00](https://www.youtube.com/watch?v=QhKKq1S9TmQ&t=720s)
shows Myrwn's Mordekaiser in top lane with the large red orb mace and exposed
torso of [Sahn-Uzal Mordekaiser](https://www.youtube.com/watch?v=vEJ3z2QqKf8&t=35s),
rather than Pentakill Mordekaiser's guitar-shaped weapon. This is recorded as
one manually reviewed game pick. The broadcast does not establish a chroma.
The tracker reports six Sahn-Uzal uses in eight Mordekaiser picks, but that
aggregate is not used to fill the other five unidentified picks.

The [firsthand observer's Worlds 2025 review](https://www.reddit.com/r/leagueoflegends/comments/1ox1hn9/fun_facts_about_skins_at_worlds_2025/)
also says both Medardas did not use their release skins. The
[Mel cosmetics timeline](https://wiki.leagueoflegends.com/en-us/Mel/Cosmetics)
shows Arcane Councilor Mel was the only alternative to her base appearance
during Worlds; [Riot's release notes](https://www.leagueoflegends.com/en-sg/news/game-updates/patch-25-s1-2-notes/)
date it to January 2025, while [Riot's later patch notes](https://www.leagueoflegends.com/en-us/news/game-updates/patch-25-24-notes/)
date her next skin to December 2025. ChainCC has three Mel picks across the
84-game event, two by Faker and one by Bdd. This supports Classic Mel for
Bdd's final game-three pick as an inference; it was not independently seen
in the game VOD. The record keeps both source links.

Together, these sources yield **182/800 sourced picks (22.75%)**. The first
160 are deductions from a firsthand observer's published data, not independent
video checks. Five finals entries are explicitly named in the esports.gg report,
nine are cross-checked against the observer's T1 wardrobe, one comes from the
translated player statement, three from timed VOD commentary, and one from
the year-end report. Two additional picks were visually reviewed in official VODs,
and one Mel pick was inferred from the observer's statement and cosmetic timeline.
All other skin choices remain unknown.

In [finals game one at about 11:00](https://www.youtube.com/watch?v=sfVFGFfec64&t=660s),
Keria's Poppy appears in the white cafe outfit with orange hair. The
[T1 finals bundle report](https://esports.gg/news/league-of-legends/worlds-2025-skin-bundles/)
lists Cafe Cuties Poppy, although it warns that some bundle skins differ from
actual game choices. The visible model plus that report supports the specific
skin. The broadcast resolution does not establish a chroma, so its status
remains `unreviewed`.

The [official BLG–100 Thieves game 1 VOD](https://www.youtube.com/watch?v=Row83yX7Ae0)
is a candidate visual source for Bin's Rek'Sai pick on October 15. A sampled
frame showed the post-draft stage, where the skin could not be identified, so
no skin was assigned from it. All 15 Main Event Rek'Sai picks remain unknown
at the game level. Patching skins by sampling individual video frames was not
continued because it does not scale reliably across 800 picks.

The downloadable `worlds-2025-skin-entry.csv` gives one row per pick. Its
`skin` column starts with the 182 entries above; the other 618 cells are blank.
The date, series game number, sides, teams, player, champion, official YouTube
VOD and source URL columns help manual entry and later review. The VODs were
matched using LoL Esports event date, teams, and game number; all 80 have an
English YouTube video. A filled CSV can be reconciled against game ID and
champion ID before publication.

Chroma is independent from skin. An unreviewed chroma does not imply the
default color. The entry sheet starts all 800 chroma statuses as `unreviewed`;
it can later distinguish confirmed default, a named variant, unavailable,
and visually uncertain chroma choices, each with a source link when reviewed.

## Archived game data and skin IDs

We checked the [Leaguepedia scoreboard parser's raw-game lookup](https://github.com/Leaguepedia/leaguepedia-scoreboard-parser/blob/master/leaguepedia_sb_parser/components/fetch_game.py)
and the [Leaguepedia V5 data API record for MKOI–T1 game one](https://lol.fandom.com/api.php?action=query&prop=revisions&titles=V5%20data%3ALOLTMNT01_300794&rvprop=content&rvslots=main&format=json).
The record contains all ten participants, including Myrwn's Mordekaiser, but
neither the participant objects nor the rest of this game JSON contain a skin
or chroma field. The parser's scoreboard result also omits skin. This one-game
check does not prove that every archived source lacks skin data; it does mean
this public Leaguepedia path cannot currently fill the missing picks.

[Riot's Live Client Data API](https://developer.riotgames.com/docs/lol#live-client-data-api)
documents `skinID` in `/liveclientdata/playerlist`, but that endpoint is served
by a running game client at `127.0.0.1:2999`. It is not an archive for the
2025 tournament. [Riot's Data Dragon documentation](https://developer.riotgames.com/docs/lol#data-dragon)
provides the names and IDs of skins and chromas, not a historical record of
which participant selected one in a particular game. Thus these catalogs can
validate a manually identified skin but cannot assign it to a game by
themselves.

## VOD navigation hints

For manual review, `gameplay-hints.csv` keeps the original official VOD link for
all 80 games and a tentative chapter link for 65 of them. We read the
YouTube-provided chapter titles with `yt-dlp` on 2026-11-08 and selected the
first chapter at or after 250 seconds whose title suggests early gameplay,
excluding chapters labelled draft, analysis, or recap. Eight videos returned
no chapters; seven others had no suitable title. The `review_status` field
marks 63 of these as **unverified navigation hints**. YouTube chapters are
sometimes inaccurate: one VOD labels its 47-second mark as "Game start"
despite a preceding draft chapter. In finals game one, the automated 6:27
"Early game" chapter still shows the stage; we replaced its hint with
[verified in-game footage at 9:20](https://www.youtube.com/watch?v=sfVFGFfec64&t=560s).
The [FLY–T1 game at 9:20](https://www.youtube.com/watch?v=6wj8x1ySMzU&t=560s)
was also checked and shows the in-game clock at 0:52. Its navigation hint
is now marked verified. We sampled the transition from draft to gameplay in
that VOD: the large stage and draft splashes show champion art, then the
broadcast cuts to the game map. It does not show a readable loading screen
with the ten selected skins. A comment on the observer's post mentions a
pre-game screen with skin splashes, but that cannot be used as a shortcut for
this official VOD. The sampled gameplay models were too small to distinguish
the remaining Mordekaiser skins confidently.
The other chapter hints can help a reviewer navigate but are not evidence for
a skin, chroma, or the precise match start time. The original VOD URL remains
available in every row.

One targeted lead remains unresolved: a [contemporaneous T1–CFO discussion](https://www.reddit.com/r/SKTT1/comments/1o81g05/t1_vs_cfo_worlds_swiss_stage/)
suggests that Oner used his own Vi skin in the October 16 game
`LOLTMNT01_296949`. The firsthand tracker confirms that Oner used T1 Vi at
some point in the tournament, but he played Vi in two Main Event games. The
discussion's wording is tentative, and the available low-resolution VOD frames
do not distinguish T1 Vi from other skins confidently. Both Oner Vi picks
therefore remain unknown until a clearer game-specific source is found.

## High-leverage manual review: Mordekaiser

The firsthand tracker reports **Sahn-Uzal Mordekaiser in six of eight**
appearances, names **Pentakill Mordekaiser** as another used skin, and names
**King of Clubs Mordekaiser** for Doran. ChainCC places all eight Mordekaiser
picks in the Main Event; Doran and PerfecT are now sourced. This leaves one
Pentakill and five Sahn-Uzal picks among these six games. Identifying the
Pentakill game from a clear official VOD view would make all six assignable
by elimination, subject to checking the tracker against the footage. No new
skin is assigned solely from these aggregate counts.

| Date | Player | Game ID | Official game VOD |
| --- | --- | --- | --- |
| 2025-10-15 | Bwipo | `LOLTMNT01_296748` | [FLY–T1, visible at 10:06](https://www.youtube.com/watch?v=6wj8x1ySMzU&t=606s) |
| 2025-10-16 | Bwipo | `LOLTMNT01_296903` | [VKS–FLY](https://www.youtube.com/watch?v=ES2vDP1lZj0) |
| 2025-10-18 | Hiro02 | `LOLTMNT01_298440` | [FLY–TSW](https://www.youtube.com/watch?v=FqXzm4-FCCQ) |
| 2025-10-25 | 369 | `LOLTMNT01_300771` | [TES–BLG](https://www.youtube.com/watch?v=V9AgrsUzMHY) |
| 2025-10-25 | Myrwn | `LOLTMNT01_300794` | [MKOI–T1, visible at 12:05](https://www.youtube.com/watch?v=QhKKq1S9TmQ&t=725s) |
| 2025-10-31 | Flandre | `LOLTMNT01_303216` | [AL–T1](https://www.youtube.com/watch?v=zvALENbYZjU) |

Those timestamps show the champion on screen, but the broadcast model is small
and the first form of [Sahn-Uzal](https://www.youtube.com/watch?v=vEJ3z2QqKf8&t=35s)
and [Pentakill](https://www.youtube.com/watch?v=8k9lhsLslSw&t=35s) both have
dark armor and red weapon effects. This visual sample does not identify the
exception. Keep all six picks unknown until a clearer game view or direct
game-specific source distinguishes the skins.

## Automated source check

Riot's [Match-V5 issue tracker](https://github.com/RiotGames/developer-relations/issues/754)
confirms that regular match participants can have `championSkinId`. That does
not establish access to Worlds tournament-realm matches through Match-V5.
The public LoL Esports game and live-stats endpoints used for this dataset do
not include a skin field. In particular, the archived
[game-three window](https://feed.lolesports.com/livestats/v1/window/113475871524050786)
and [details](https://feed.lolesports.com/livestats/v1/details/113475871524050786)
responses for the 2025 grand final returned participant champion data and
frame details, but no skin field when checked on 2026-11-08.
[Riot's esports data page](https://riotesportsdata.com/en-us/league-of-legends/)
says broader community access to the separate LoL Esports Data Portal is still
being rolled out. No skin value is inferred from an absent field or from a
promotional skin bundle.

[GRID's file-download documentation](https://docs.grid.gg/public/documentation/api-documentation/in-game-data/grid-file-download-api)
lists Riot Game Agnostic Match History files for supported series. It requires
a GRID API key; an unauthenticated request to the documented list endpoint
returned HTTP 401 on 2026-11-08. The public documentation does not establish
that these files contain a selected skin or chroma field, nor that the 2025
Worlds files can be obtained under non-commercial access. Do not count this
as a verified source of game-level skin choices without inspecting an
authorized sample and confirming its field and coverage.

The current proskin.gg site describes archiving matches from 2026 onward.
Its public matches query returned no 2025 records when checked on 2026-11-08,
so it cannot fill this tournament. Revisit these sources if their coverage or
access changes.

The older Leaguepedia wiki has a [2017 Worlds Main Event skins page](https://lol.fandom.com/wiki/2017_Season_World_Championship/Main_Event/Skins),
but its [MediaWiki page query for the corresponding 2025 page](https://lol.fandom.com/api.php?action=query&format=json&titles=2025_Season_World_Championship%2FMain_Event%2FSkins)
returns `missing`. The 2015–2017 skin archive therefore does not provide a
2025 game-skin table under the same page series. This check does not rule out
a differently named or privately held dataset.

Two other public match archives were checked on 2026-11-08. The
[League2025WorldData project](https://github.com/KayXi2014/League2025WorldData)
scrapes the Worlds 2025 Leaguepedia match history, but its published match
table has picks, teams, dates, and results rather than skins. The
[GPTilt esports matches dataset](https://huggingface.co/datasets/gptilt/lol-esports-matches)
includes a Leaguepedia game ID, Riot game ID, picks, and a VOD field, but its
published schema has no skin or chroma field. Neither can supply a skin value
for the 618 still-unidentified Main Event picks.

The [source-site importer](https://github.com/sciencejiho/web-main/blob/main/scripts/import-worlds-2025-skin-evidence.mjs)
regenerates the evidence overlay from the ChainCC file and the reviewed source
claims. Review its JSON diff before syncing this repository. Do not extend
the singleton mapping to repeat picks without a game-specific source.
