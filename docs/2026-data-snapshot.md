# 2026 international-event entry sheets

The 2026 files are skin review worksheets. Every listed MSI and Worlds game has been checked for the early-game player introduction cards. Only labels that can be tied to a player, champion, and VOD timestamp are entered. A blank `skin` means unknown, not the default skin. EWC skin review was skipped because its broadcast did not show the skin introductions used for this review.

| Event | Scope | Match source | Games | Picks | Last game in snapshot |
| --- | --- | --- | ---: | ---: | --- |
| Worlds | Main Event, from October 23 | ChainCC `WLDs` | 72 | 720 | November 9, 2026 |
| MSI | Play-In and Bracket, June 28 to July 12 | ChainCC `MSI` | 71 | 710 | July 12, 2026 |
| EWC | Main Event, July 15 to 19 | ChainCC `EWC` | 51 | 510 | July 19, 2026 |

| Event | Games with 10 labels | Partial games | No readable card found | Skin picks recorded | Named chromas |
| --- | ---: | ---: | ---: | ---: | ---: |
| Worlds | 65 | 0 | 7 | 650 | 202 |
| MSI | 45 | 1 | 25 | 458 | 143 |
| EWC | — | — | — | 0 | 0 |

The [MSI review status](../data/msi/2026-all-stages/review-status.csv) and [Worlds review status](../data/worlds/2026-main-event/review-status.csv) cover every listed game. `no_intro_card` means the review found no readable paired skin labels about 30 seconds to 8 minutes after the game began. It does not establish which skins were used. MSI's one partial game has two player cards obscured by a broadcast graphic. The [MSI evidence](../data/msi/2026-all-stages/skin-evidence.csv) and [Worlds evidence](../data/worlds/2026-main-event/skin-evidence.csv) give an exact video time for every recorded pick. A blank evidence `chroma` means the label did not name a variant. An Excel `chroma` cell may show `default` automatically when its skin has no other chroma in the lookup list; that formula is not a video-based chroma review.

The snapshot was generated on November 11, 2026 from [ChainCC's 2026 player data](https://chaincc.lol/free/data), licensed CC BY 4.0. ChainCC supplies game IDs, dates, teams, players, sides, and champions. A game enters a sheet only if it has five players on each side. Worlds is still in progress; its final is scheduled for November 14, according to the [official Worlds primer](https://lolesports.com/en-GB/news/worlds-2026-primer). The Worlds counts above describe this downloaded snapshot.

The builder pairs each ChainCC series with the [official LoL Esports schedule and VOD data](https://lolesports.com/). Every listed 2026 game has a YouTube VOD. The link prefers English when available; `games.csv` records the selected `vod_locale`. MSI has 71 English links. Worlds has 66 English and 6 Arabic links. EWC has 18 English and 33 French links. Some Worlds links point to a full series rather than one game; [VOD game starts](../data/worlds/2026-main-event/vod-game-starts.csv) records the checked time of each game in those videos.

The skin and chroma dropdowns use [CommunityDragon client data](https://raw.communitydragon.org/) for patch 16.13 at MSI and EWC, and patch 16.20 at Worlds. Missing skin IDs in those files are supplemented from Riot Data Dragon for the same patches. Champion IDs and display names use [Riot Data Dragon 16.22.1](https://ddragon.leagueoflegends.com/cdn/16.22.1/data/en_US/champion.json). Each skin gets a `default` chroma choice. No skin is selected automatically.

The review script reads the consecutive top, jungle, mid, bot, and support labels in each game VOD. It requires the OCR result to match that game's player and champion and a patch lookup name. Readable cards missed by OCR were checked visually. Run `uv run --python 3.13 --with yt-dlp --with rapidocr-onnxruntime --with opencv-python --with openpyxl --with imageio-ffmpeg python scripts/review-2026-broadcast-skins.py --event msi --resume` to inspect any MSI games not yet in the status file; use `--event worlds` for Worlds. Video review does not write the entry workbook. Run `uv run --with openpyxl python scripts/build-2026-entry.py` to refresh all three datasets and match indexes. The builder checks each evidence row against its game pick, patch lookup, and VOD URL before writing `picks.csv` and Excel. Reviews entered only in Excel must be copied into `skin-evidence.csv` before a refresh. The 2025 workbook is left untouched.
