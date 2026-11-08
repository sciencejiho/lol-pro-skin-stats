# Worlds 2025 Main Event skin evidence

Unit of analysis: one champion pick in one Main Event game, identified by
`gameId + championId`. The local ChainCC-derived roster has 80 games and 800
picks. Skin selections are a separate evidence overlay; absent evidence means
unknown, never zero uses or a default skin.

The [firsthand Worlds tracker](https://www.reddit.com/r/leagueoflegends/comments/1ox1hn9/fun_facts_about_skins_at_worlds_2025/)
observed the whole 84-game event, including four Play-In games. Its author
describes watching games, recognizing skins, and recording them in Excel.
The importer cross-checks every whole-event count against ChainCC before
assigning a skin to a Main Event game:

- Six champions have one skin in all their appearances: Super Galaxy Rumble
  (21/21), Classic Ambessa (19/19), Striker Ezreal (15/15), Classic Azir
  (14/14), Prestige Blood Moon Aatrox (5/5), and Corporate Mundo (5/5).
- For Kai'Sa, Xayah, and Lucian, the tracker reports a dominant skin in all
  but one appearance (17/18, 10/11, and 8/9). It separately names the only
  player who chose each alternative. Each such player used that champion
  exactly once in the whole event, so all 38 appearances can be assigned.
- The tracker names Faker and Poby as the only two players who used only base
  skins. Faker had 24 whole-event games and Poby had five. Their 20 and five
  Main Event picks respectively are base-skin selections. The separate
  mid-lane base-skin totals (75, or 51 without Faker) reconcile Faker's count.
- The post names skins for 20 other player/champion combinations that each
  occurred exactly once in all 84 games. Two overlap the all-champion rule.
  The T1 wardrobe list is incomplete for some champions, so repeated picks
  from that list are not assigned without game-specific evidence.

The methods yield **156/800 sourced picks (19.5%)**. These are deductions
from a firsthand observer's published data, not 156 independent video checks.
All other skin choices remain unknown.

The [official BLG–100 Thieves game 1 VOD](https://www.youtube.com/watch?v=Row83yX7Ae0)
is a candidate visual source for Bin's Rek'Sai pick on October 15. A sampled
frame showed the post-draft stage, where the skin could not be identified, so
no skin was assigned from it. All 15 Main Event Rek'Sai picks remain unknown
at the game level. Patching skins by sampling individual video frames was not
continued because it does not scale reliably across 800 picks.

The downloadable `worlds-2025-skin-entry.csv` gives one row per pick. Its
`skin` column starts with the 156 entries above; the other 644 cells are blank.
The date, series game number, sides, teams, player, champion, official YouTube
VOD and source URL columns help manual entry and later review. The VODs were
matched using LoL Esports event date, teams, and game number; all 80 have an
English YouTube video. A filled CSV can be reconciled against game ID and
champion ID before publication.

Chroma is independent from skin. An unreviewed chroma does not imply the
default color. The entry sheet starts all 800 chroma statuses as `unreviewed`;
it can later distinguish confirmed default, a named variant, unavailable,
and visually uncertain chroma choices, each with a source link when reviewed.

Regenerate the overlay with `node scripts/import-worlds-2025-skin-evidence.mjs
<chaincc-players-2025.csv.gz>` and review the JSON diff. Do not extend the
singleton mapping to repeat picks without a game-specific source.
