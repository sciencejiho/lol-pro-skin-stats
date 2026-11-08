# LoL pro skin stats / 프로 경기 스킨 기록

프로 리그 오브 레전드 경기의 **실제로 선택된 스킨**을 경기·선수·챔피언 단위로 기록하는 공개 데이터 저장소입니다. 우승팀 기념 스킨 목록과는 다릅니다. 현재 입력표는 **2025 월즈 메인 이벤트 80경기·800픽**을 담고 있습니다.

| 파일 | 내용 |
| --- | --- |
| [경기별 YouTube 링크](data/worlds/2025-main-event/games.csv) | 80경기의 공식 LoL Esports 영어 VOD와 경기 ID |
| [VOD JSON](data/worlds/2025-main-event/vods.json) | 웹사이트에서 쓰는 경기 ID·YouTube 링크 목록 |
| [스킨 입력표](data/worlds/2025-main-event/picks.csv) | 800픽의 날짜·팀·선수·챔피언·스킨·크로마·영상 링크 |
| [경기 원본](data/worlds/2025-main-event/roster.json) | ChainCC에서 가져온 80경기·800픽 |
| [스킨 근거](data/worlds/2025-main-event/skin-evidence.json) | 공개 자료에서 정확한 픽에 연결한 178건 |

## 입력 방법

1. `games.csv`에서 경기를 찾고 `youtube_url`을 여세요. `picks.csv`의 각 픽에도 같은 링크가 있습니다. 이 링크는 픽/밴 화면이 아닌 **실제 경기 영상**으로 이어집니다.
2. `picks.csv`에서 해당 `game_id`로 필터링해 선수·챔피언을 확인하세요. `skin`이 빈칸이면 아직 모르는 것입니다. **기본 스킨이라는 뜻이 아닙니다.** 스킨을 확인한 경우 이름을 입력하고, 가능하면 `source_url`에 확인한 영상의 시점 링크를 넣으세요.
3. 크로마는 스킨과 별도로 기록합니다. 처음에는 모든 행의 `chroma_status`가 `unreviewed`입니다. 영상을 확인했다면 `default`(기본 색상), `variant`(다른 크로마), `unavailable`(해당 스킨에 크로마가 없음), `uncertain`(영상만으로 식별 불가) 중 하나로 바꾸세요. `variant`일 때는 `chroma`에 이름이나 색상을 쓰고, 판정한 경우에는 `chroma_source_url`에 근거 영상 링크를 넣으세요. 크로마를 구별할 수 없을 때는 추측하지 마세요.
4. 날짜, `game_id`, `series_game`, 팀, 선수, 챔피언 ID와 행 수는 유지하세요. 수정한 CSV를 이 저장소의 이슈나 PR로 공유하거나, 사이트 관리자에게 전달하면 검토 후 공개 통계에 반영할 수 있습니다.

현재 178개의 `skin` 값 중 160개는 [직접 관찰한 월즈 2025 기록](https://www.reddit.com/r/leagueoflegends/comments/1ox1hn9/fun_facts_about_skins_at_worlds_2025/)의 대회 전체 집계·특정 선수 언급을 [ChainCC 경기 자료](https://chaincc.lol/free/data)와 맞춰 경기 단위로 좁힌 것입니다. 5개는 [결승전 실제 사용 스킨 보도](https://esports.gg/news/league-of-legends/worlds-2025-skin-bundles/)에 명시됐고, 9개는 그 보도와 관찰자의 T1 스킨 목록이 일치하며, 1개는 [선수의 대회 복기 방송 기록](https://www.reddit.com/r/SKTT1/comments/1p5xlhn/gumayusis_review_and_insight_of_worlds_2025_games/)에서 확인했습니다. 새로 추가한 3개는 공식 경기 VOD의 시점별 해설에서 확인했고, 스킨 외형으로 이름을 특정한 2개에는 보조 출처를 남겼습니다. 영상으로 178건을 각각 재확인한 것은 아닙니다. 나머지 622픽은 미확인입니다. 크로마는 아직 확인한 항목이 없습니다. 추론 범위는 [조사 기록](docs/worlds-2025-methodology.md)에 적었습니다.

## 데이터 출처와 갱신

- 경기·픽: ChainCC, *League of Legends esports match dataset*, [공개 데이터](https://chaincc.lol/free/data), **CC BY 4.0**. 2025년 파일에서 10월 14일 플레이인 4경기를 제외했습니다. 원본 소유와 라이선스는 ChainCC에 있습니다.
- VOD: [LoL Esports](https://lolesports.com/)의 공개 경기 상세 자료에 있는 `en-US` YouTube 영상 ID를 경기 날짜·두 팀·세트 번호로 연결했습니다. `scripts/fetch-worlds-2025-vods.mjs`가 80경기를 다시 조회하고 입력표에 링크를 채웁니다. 영상 및 관련 상표는 해당 소유자에게 있습니다.
- 스킨: [월즈 2025 직접 관찰 기록](https://www.reddit.com/r/leagueoflegends/comments/1ox1hn9/fun_facts_about_skins_at_worlds_2025/), [결승전 실제 사용 스킨 보도](https://esports.gg/news/league-of-legends/worlds-2025-skin-bundles/), [선수의 대회 복기 방송 기록](https://www.reddit.com/r/SKTT1/comments/1p5xlhn/gumayusis_review_and_insight_of_worlds_2025_games/), 공식 경기 VOD의 시점 링크를 픽별 출처로 표시합니다. 확인되지 않은 스킨은 임의로 채우지 않습니다.
- 크로마 식별: [Riot Data Dragon 문서](https://developer.riotgames.com/docs/lol#data-dragon)는 크로마 항목을 `parentSkin`으로 원래 스킨과 연결합니다. 향후 이름을 Riot 스킨·크로마 ID에 연결할 때 이 관계와 **경기 당시 패치**를 함께 확인해야 합니다. 현재 CSV의 크로마는 모두 미검토입니다.

`node scripts/validate.mjs`는 80경기·800픽의 ID·팀·선수·VOD 연결과 현재 근거 178건을 검사합니다. VOD 조회에는 Node.js 20 이상이 필요합니다. 이 저장소는 Riot Games의 공식 프로젝트가 아닙니다.

## English

This public dataset tracks skins actually chosen in pro League of Legends games. It currently covers all 80 games and 800 champion picks of the Worlds 2025 Main Event, with an official English YouTube VOD link for each game. A blank `skin` means **unknown**, not the default skin. Chroma is tracked independently and remains unreviewed until there is evidence.
