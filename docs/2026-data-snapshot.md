# 2026 international-event entry sheets

The 2026 files are skin review worksheets. Thirty picks have been checked against the player skin labels shown in official game VODs: 20 at MSI and 10 at Worlds. Their exact video times are in each event's `skin-evidence.csv`; all other blank `skin` fields mean unknown. Ten of those labels explicitly name a chroma. A `chroma` cell may show `default` automatically when the selected skin has no other chroma in its lookup list; that formula is not a video-based chroma review.

| Event | Scope | Match source | Games | Picks | Last game in snapshot |
| --- | --- | --- | ---: | ---: | --- |
| Worlds | Main Event, from October 23 | ChainCC `WLDs` | 72 | 720 | November 9, 2026 |
| MSI | Play-In and Bracket, June 28 to July 12 | ChainCC `MSI` | 71 | 710 | July 12, 2026 |
| EWC | Main Event, July 15 to 19 | ChainCC `EWC` | 51 | 510 | July 19, 2026 |

The snapshot was generated on November 11, 2026 from [ChainCC's 2026 player data](https://chaincc.lol/free/data), licensed CC BY 4.0. ChainCC supplies the game IDs, dates, teams, players, sides, and champions. A game enters a sheet only if it has five players on each side. Worlds is still in progress; its final is scheduled for November 14, according to the [official Worlds primer](https://lolesports.com/en-GB/news/worlds-2026-primer). The Worlds counts above describe the downloaded snapshot, not the eventual final event total.

The script pairs each ChainCC series with the [official LoL Esports schedule and VOD data](https://lolesports.com/). Every listed 2026 game has a YouTube VOD. The link prefers English when available; `games.csv` records the selected `vod_locale`. MSI has 71 English links. Worlds has 66 English and 6 Arabic links. EWC has 18 English and 33 French links. The VOD links are for finding and checking a pick; they do not establish the skin by themselves.

The skin and chroma dropdowns use [CommunityDragon client data](https://raw.communitydragon.org/) for patch 16.13 at MSI and EWC, and patch 16.20 at Worlds. Champion IDs and display names use [Riot Data Dragon 16.22.1](https://ddragon.leagueoflegends.com/cdn/16.22.1/data/en_US/champion.json). The lookup lists contain all skins for champions picked in each event at that patch. Each skin gets a `default` chroma choice. No skin is selected automatically.

The reviewed 2026 skins came from the consecutive top, jungle, mid, bot, and support player introductions in [MSI game 1](https://www.youtube.com/watch?v=959oVkQIW3o&t=678s), [MSI game 2](https://www.youtube.com/watch?v=EhYA11W1qAI&t=476s), and [Worlds Dplus KIA versus G2](https://www.youtube.com/watch?v=jLbhlvybfiA&t=463s). The [MSI evidence](../data/msi/2026-all-stages/skin-evidence.csv) and [Worlds evidence](../data/worlds/2026-main-event/skin-evidence.csv) tie each label to a game, player, champion, and timestamp. An empty chroma in those files means the broadcast label did not establish a specific variant; it does not establish default.

Run `uv run --with openpyxl python scripts/build-2026-entry.py` to refresh all three 2026 datasets and the match indexes from the public sources. The script checks each evidence row against the game pick, patch lookup, and VOD URL before writing reviewed values into `picks.csv` and the workbook. It recreates the workbooks and CSV files; reviews entered only in Excel must be copied into `skin-evidence.csv` before a refresh. The 2025 workbook is left untouched; only its `matches.md` index is refreshed from `games.csv`.
