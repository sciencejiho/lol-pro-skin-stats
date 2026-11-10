# 2026 international-event entry sheets

The 2026 files are **skin review worksheets**, not verified skin-use results. All `skin` fields start empty. A `chroma` cell shows `default` only when the selected skin has no other chroma in its lookup list. No broadcast frames were reviewed for these new sheets.

| Event | Scope | Match source | Games | Picks | Last game in snapshot |
| --- | --- | --- | ---: | ---: | --- |
| Worlds | Main Event, from October 23 | ChainCC `WLDs` | 68 | 680 | November 8, 2026 |
| MSI | Play-In and Bracket, June 28 to July 12 | ChainCC `MSI` | 71 | 710 | July 12, 2026 |
| EWC | Main Event, July 15 to 19 | ChainCC `EWC` | 51 | 510 | July 19, 2026 |

The snapshot was generated on November 10, 2026 from [ChainCC's 2026 player data](https://chaincc.lol/free/data), licensed CC BY 4.0. ChainCC supplies the game IDs, dates, teams, players, sides, and champions. A game enters a sheet only if it has five players on each side. Worlds is still in progress; its final is scheduled for November 14, according to the [official Worlds primer](https://lolesports.com/en-GB/news/worlds-2026-primer). The Worlds counts above describe the downloaded snapshot, not the eventual final event total.

The script pairs each ChainCC series with the [official LoL Esports schedule and VOD data](https://lolesports.com/). Every listed 2026 game has a YouTube VOD. The link prefers English when available; `games.csv` records the selected `vod_locale`. MSI has 71 English links. Worlds has 62 English and 6 Arabic links. EWC has 18 English and 33 French links. The VOD links are for finding and checking a pick; they do not establish the skin by themselves.

The skin and chroma dropdowns use [CommunityDragon client data](https://raw.communitydragon.org/) for patch 16.13 at MSI and EWC, and patch 16.20 at Worlds. Champion IDs and display names use [Riot Data Dragon 16.22.1](https://ddragon.leagueoflegends.com/cdn/16.22.1/data/en_US/champion.json). The lookup lists contain all skins for champions picked in each event at that patch. Each skin gets a `default` chroma choice. No skin is selected automatically.

Run `uv run --with openpyxl python scripts/build-2026-entry.py` to refresh all three 2026 datasets and the match indexes from the public sources. This command **recreates** the 2026 workbooks and CSV files, so copy any manual skin or chroma reviews elsewhere before running it again. The 2025 workbook is left untouched; only its `matches.md` index is refreshed from `games.csv`.
