"""Build 2026 international-event skin entry sheets from public match data.

Run with: uv run --with openpyxl python scripts/build-2026-entry.py
"""

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from difflib import SequenceMatcher
import csv
import gzip
import io
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo


ROOT = Path(__file__).resolve().parents[1]
DATA_URL = "https://chaincc.lol/data/chaincc-players-2026.csv.gz"
CHAMPIONS_URL = "https://ddragon.leagueoflegends.com/cdn/16.22.1/data/en_US/champion.json"
CDRAGON = "https://raw.communitydragon.org/{patch}/plugins/rcp-be-lol-game-data/global/default/v1/champions/{id}.json"
DDRAGON_SKINS = "https://ddragon.leagueoflegends.com/cdn/{patch}.1/data/en_US/champion/{id}.json"
ESPORTS = "https://esports-api.lolesports.com/persisted/gw/"
API_KEY = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"
EVENTS = {
    "worlds": {"league": "WLDs", "first": "2026-10-23", "last": "2026-11-14", "patch": "16.20", "tournament": "115660540725177488", "stage": "Main Event"},
    "msi": {"league": "MSI", "first": "2026-06-28", "last": "2026-07-12", "patch": "16.13", "tournament": "115570934354631452", "stage": "All stages"},
    "ewc": {"league": "EWC", "first": "2026-07-15", "last": "2026-07-19", "patch": "16.13", "tournament": "116854907266085633", "stage": "Main Event"},
}
HEADERS = ["date", "game_id", "series_game", "side", "team", "opponent", "player", "champion_id", "champion", "skin", "chroma", "youtube_url"]
ROLES = {"top": 0, "jng": 1, "mid": 2, "bot": 3, "sup": 4}
BLUE = PatternFill("solid", fgColor="EAF4FF")
RED = PatternFill("solid", fgColor="FDEBEC")
BLUE_INPUT = PatternFill("solid", fgColor="DCEEFF")
RED_INPUT = PatternFill("solid", fgColor="FADCDD")
DARK = Side(style="thick", color="34495E")
TEAM = Side(style="medium", color="A6B4C2")


def get_bytes(url, headers=None):
    with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0", **(headers or {})}), timeout=30) as response:
        return response.read()


def esports(path, **params):
    url = ESPORTS + path + "?" + urlencode({"hl": "en-US", **params})
    return json.loads(get_bytes(url, {"x-api-key": API_KEY}))


def clean_team(name):
    aliases = {"AG.AL": "Anyone's Legend", "JD Gaming": "Beijing JDG Esports"}
    name = aliases.get(name, name)
    name = name.lower().replace("ø", "o").replace("kia", "").replace("alienware", "")
    name = name.replace("relove", "").replace("mibr", "")
    name = name.replace("esports", "").replace("gaming", "")
    return re.sub(r"[^a-z0-9]", "", name)


def pair_score(left, right):
    a, b = sorted(clean_team(x) for x in left)
    c, d = sorted(clean_team(x) for x in right)
    return (SequenceMatcher(None, a, c).ratio() + SequenceMatcher(None, b, d).ratio()) / 2


def build_games(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["game_id"]].append(row)
    games = []
    for game_id, picks in grouped.items():
        assert len(picks) == 10, (game_id, len(picks))
        sides = {side: [p for p in picks if p["side"].lower() == side] for side in ("blue", "red")}
        assert all(len(group) == 5 for group in sides.values()), game_id
        for side, group in sides.items():
            assert len({p["team_name"] for p in group}) == 1, (game_id, side)
        blue, red = sides["blue"][0]["team_name"], sides["red"][0]["team_name"]
        games.append({"id": game_id, "date": picks[0]["date"][:10], "time": picks[0]["date"], "blue": blue, "red": red, "picks": picks})
    games.sort(key=lambda game: (game["time"], game["id"]))
    counts = defaultdict(int)
    for game in games:
        series = (game["date"], tuple(sorted((game["blue"], game["red"]))))
        counts[series] += 1
        game["number"] = counts[series]
    return games


def attach_vods(games, tournament):
    events = esports("getCompletedEvents", tournamentId=tournament)["data"]["schedule"]["events"]
    details = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        jobs = {pool.submit(esports, "getEventDetails", id=e["match"]["id"]): e for e in events}
        for job in as_completed(jobs):
            event = jobs[job]
            details[event["match"]["id"]] = job.result()["data"]["event"]
    series = defaultdict(list)
    for game in games:
        actual = datetime.fromisoformat(game["time"])
        candidates = []
        for event in events:
            detail = details[event["match"]["id"]]
            if not detail:
                continue
            scheduled = datetime.fromisoformat(event["startTime"].replace("Z", "+00:00")).replace(tzinfo=None)
            hours = (actual - scheduled).total_seconds() / 3600
            if not -4 <= hours <= 36:
                continue
            official_teams = [team["name"] for team in detail["match"]["teams"]]
            score = pair_score((game["blue"], game["red"]), official_teams)
            if score >= 0.78:
                candidates.append((score, -abs(hours), event, detail))
        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        if not candidates:
            continue
        _, _, event, detail = candidates[0]
        series[event["match"]["id"]].append(game)
    matches = 0
    for event_id, series_games in series.items():
        event = next(item for item in events if item["match"]["id"] == event_id)
        detail = details[event_id]
        official_games = {game["number"]: game for game in detail["match"]["games"] if game["state"] == "completed"}
        # A missing roster game would shift every later number in the series.
        if len(official_games) != len(series_games):
            continue
        for number, game in enumerate(sorted(series_games, key=lambda item: item["time"]), 1):
            game["number"] = number
            official = official_games.get(game["number"])
            if not official:
                continue
            vod = next((v for v in official["vods"] if v["provider"] == "youtube" and v["locale"] == "en-US" and re.fullmatch(r"[A-Za-z0-9_-]{11}", v["parameter"])), None)
            if not vod:
                vod = next((v for v in official["vods"] if v["provider"] == "youtube" and re.fullmatch(r"[A-Za-z0-9_-]{11}", v["parameter"])), None)
            if vod:
                video = vod["parameter"]
                game["youtube_url"] = f"https://www.youtube.com/watch?v={video}"
                game["vod_locale"] = vod["locale"]
                game["lolesports_url"] = f"https://lolesports.com/en-US/vod/{event['match']['id']}/{game['number']}/{video}"
                game["lolesports_match_id"] = event["match"]["id"]
                game["lolesports_game_id"] = official["id"]
                matches += 1
    return matches


def make_catalog(champion_ids, champion_info, patch):
    skin_rows, chroma_rows = [], []
    def fetch(champion_id):
        url = CDRAGON.format(patch=patch, id=champion_info[champion_id]["key"])
        riot_url = DDRAGON_SKINS.format(patch=patch, id=champion_id)
        return champion_id, url, json.loads(get_bytes(url)), riot_url, json.loads(get_bytes(riot_url))["data"][champion_id]["skins"]
    with ThreadPoolExecutor(max_workers=12) as pool:
        jobs = [pool.submit(fetch, champion_id) for champion_id in sorted(champion_ids)]
        for job in as_completed(jobs):
            champion_id, url, data, riot_url, riot_skins = job.result()
            champion_name = champion_info[champion_id]["name"]
            known_ids = set()
            for skin in data["skins"]:
                name = f"Classic {champion_name}" if skin["isBase"] else skin["name"]
                skin_rows.append((champion_id, champion_name, name, str(skin["id"]), url))
                known_ids.add(str(skin["id"]))
                key = f"{champion_id}|{name}"
                chroma_rows.append((key, champion_id, name, "default", "", url))
                for chroma in skin.get("chromas", []):
                    chroma_rows.append((key, champion_id, name, chroma["name"], str(chroma["id"]), url))
                    # Data Dragon also lists chroma IDs among its skin entries.
                    known_ids.add(str(chroma["id"]))
            for skin in riot_skins:
                if str(skin["id"]) in known_ids:
                    continue
                name = skin["name"]
                skin_rows.append((champion_id, champion_name, name, str(skin["id"]), riot_url))
                chroma_rows.append((f"{champion_id}|{name}", champion_id, name, "default", "", riot_url))
    skin_rows.sort(key=lambda row: (row[0], row[2]))
    chroma_rows.sort(key=lambda row: (row[1], row[2], row[3] != "default", row[3]))
    return skin_rows, chroma_rows


def add_table(sheet, name, end_col, end_row, stripes=False):
    from openpyxl.utils import get_column_letter
    table = Table(displayName=name, ref=f"A1:{get_column_letter(end_col)}{end_row}")
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=stripes)
    sheet.add_table(table)


def write_workbook(path, games, skin_rows, chroma_rows, reviews):
    wb = Workbook()
    picks = wb.active
    picks.title = "Picks"
    skin_sheet = wb.create_sheet("Skin lookup")
    chroma_sheet = wb.create_sheet("Chroma lookup")
    picks.append(HEADERS)
    for sheet, columns, data in (
        (skin_sheet, ["champion_id", "champion", "skin", "skin_id", "source"], skin_rows),
        (chroma_sheet, ["champion_skin_key", "champion_id", "skin", "chroma", "chroma_id", "source"], chroma_rows),
    ):
        sheet.append(columns)
        for row in data:
            sheet.append(row)
        sheet.freeze_panes = "A2"
        for cell in sheet[1]:
            cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="243B53")
        add_table(sheet, "Worlds2026" + sheet.title.replace(" ", ""), len(columns), sheet.max_row, True)
    skin_sheet.column_dimensions["A"].width = 21
    skin_sheet.column_dimensions["B"].width = 22
    skin_sheet.column_dimensions["C"].width = 38
    chroma_sheet.column_dimensions["A"].width = 55
    chroma_sheet.column_dimensions["D"].width = 42
    for col, width in {"A": 13, "B": 25, "C": 12, "D": 11, "E": 24, "F": 24, "G": 20, "H": 20, "I": 20, "J": 34, "K": 28, "L": 48}.items():
        picks.column_dimensions[col].width = width
    for cell in picks[1]:
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="243B53")
        cell.alignment = Alignment(vertical="center")
    picks.row_dimensions[1].height = 24
    for game in games:
        for side, team, opponent in (("Blue", game["blue"], game["red"]), ("Red", game["red"], game["blue"])):
            players = [row for row in game["picks"] if row["side"].lower() == side.lower()]
            players.sort(key=lambda row: ROLES.get(row["position"].lower(), 99))
            for index, player in enumerate(players):
                row_num = picks.max_row + 1
                review = reviews.get((game["id"], player["playername"], player["champion_id"]))
                values = [date.fromisoformat(game["date"]), game["id"], game["number"], side, team, opponent, player["playername"], player["champion_id"], player["champion"], review["skin"] if review else None, review["chroma"] if review and review["chroma"] else None, game.get("youtube_url", "")]
                picks.append(values)
                for col in range(1, 13):
                    cell = picks.cell(row_num, col)
                    cell.font = Font(name="Arial", size=10, bold=(col == 9), color="263238")
                    cell.fill = (BLUE_INPUT if side == "Blue" else RED_INPUT) if col in (10, 11) else (BLUE if side == "Blue" else RED)
                    if index == 0:
                        if side == "Blue":
                            cell.border = Border(top=DARK)
                        else:
                            cell.border = Border(top=TEAM)
                picks.cell(row_num, 1).number_format = "yyyy-mm-dd"
                if game.get("youtube_url"):
                    picks.cell(row_num, 12).hyperlink = game["youtube_url"]
                if not review or not review["chroma"]:
                    picks.cell(row_num, 11).value = f'=IF($J{row_num}="","",IF(COUNTIF(\'Chroma lookup\'!$A$2:$A${len(chroma_rows)+1},$H{row_num}&"|"&$J{row_num})=1,"default",""))'.replace("\\'", "'")
    picks.freeze_panes = "A2"
    add_table(picks, "Worlds2026Picks", 12, picks.max_row)
    skin_end = len(skin_rows) + 1
    chroma_end = len(chroma_rows) + 1
    skin_validation = DataValidation(type="list", formula1=f'OFFSET(INDIRECT("\'Skin lookup\'!$C$2"),MATCH($H2,INDIRECT("\'Skin lookup\'!$A$2:$A${skin_end}"),0)-1,0,COUNTIF(INDIRECT("\'Skin lookup\'!$A$2:$A${skin_end}"),$H2),1)', allow_blank=True)
    chroma_validation = DataValidation(type="list", formula1=f'OFFSET(INDIRECT("\'Chroma lookup\'!$D$2"),MATCH($H2&"|"&$J2,INDIRECT("\'Chroma lookup\'!$A$2:$A${chroma_end}"),0)-1,0,COUNTIF(INDIRECT("\'Chroma lookup\'!$A$2:$A${chroma_end}"),$H2&"|"&$J2),1)', allow_blank=True)
    picks.add_data_validation(skin_validation)
    picks.add_data_validation(chroma_validation)
    skin_validation.add(f"J2:J{picks.max_row}")
    chroma_validation.add(f"K2:K{picks.max_row}")
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.calculation.calcMode = "auto"
    wb.save(path)


def write_match_index(directory, event, stage):
    with (directory / "games.csv").open(newline="") as stream:
        games = list(csv.DictReader(stream))
    matches = defaultdict(list)
    for game in games:
        key = game.get("lolesports_match_id") or (game["date"], tuple(sorted((game["team_a"], game["team_b"]))))
        matches[key].append(game)
    lines = [
        f"# {event} 2026 match coverage" if event != "Worlds 2025" else "# Worlds 2025 match coverage",
        "",
        f"{stage}. {len(matches)} matches, {len(games)} games, {len(games) * 10} picks. Match rows below list games present in this repository.",
        "",
        "| Date | Match | Games recorded | Video |",
        "| --- | --- | ---: | --- |",
    ]
    for group in sorted(matches.values(), key=lambda rows: (rows[0]["date"], rows[0]["team_a"], rows[0]["team_b"])):
        first = group[0]
        vod = next((row["youtube_url"] for row in group if row["youtube_url"]), "")
        video = f"[Open VOD]({vod})" if vod else "Pending"
        lines.append(f"| {first['date']} | {first['team_a']} vs {first['team_b']} | {len(group)} | {video} |")
    lines += ["", "[Game and VOD details](games.csv) · [Pick rows](picks.csv)", ""]
    (directory / "matches.md").write_text("\n".join(lines))


def load_reviews(directory, games, skin_rows, chroma_rows):
    path = directory / "skin-evidence.csv"
    if not path.exists():
        return {}
    picks = {(game["id"], row["playername"], row["champion_id"]): game for game in games for row in game["picks"]}
    skins = {(row[0], row[2]) for row in skin_rows}
    chromas = {(row[1], row[2], row[3]) for row in chroma_rows}
    reviews = {}
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            key = (row["game_id"], row["player"], row["champion_id"])
            assert key in picks and key not in reviews, key
            assert (row["champion_id"], row["skin"]) in skins, key
            assert not row["chroma"] or (row["champion_id"], row["skin"], row["chroma"]) in chromas, key
            expected_url = f'{picks[key]["youtube_url"]}&t={row["video_time_seconds"]}s'
            assert row["source_url"] == expected_url, key
            reviews[key] = row
    return reviews


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", choices=(*EVENTS, "all"), default="all")
    args = parser.parse_args()
    raw = gzip.decompress(get_bytes(DATA_URL)).decode("utf-8-sig")
    all_rows = list(csv.DictReader(io.StringIO(raw)))
    champions = json.loads(get_bytes(CHAMPIONS_URL))["data"]
    by_name = {value["name"].lower(): value for value in champions.values()}
    by_name["wukong"] = champions["MonkeyKing"]
    info = {key: {"name": value["name"], "key": value["key"]} for key, value in champions.items()}
    selected = EVENTS if args.event == "all" else {args.event: EVENTS[args.event]}
    for slug, config in selected.items():
        rows = [row for row in all_rows if row["league"] == config["league"] and config["first"] <= row["date"][:10] <= config["last"]]
        for row in rows:
            champion = by_name.get(row["champion"].lower())
            if not champion:
                raise ValueError(f"Unknown champion {row['champion']}")
            row["champion_id"] = champion["id"]
        games = build_games(rows)
        matched = attach_vods(games, config["tournament"])
        ids = {row["champion_id"] for row in rows}
        skin_rows, chroma_rows = make_catalog(ids, info, config["patch"])
        directory = ROOT / "data" / slug / ("2026-main-event" if slug != "msi" else "2026-all-stages")
        directory.mkdir(parents=True, exist_ok=True)
        reviews = load_reviews(directory, games, skin_rows, chroma_rows)
        with (directory / "games.csv").open("w", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["date", "start_time_utc", "game_id", "series_game", "team_a", "team_b", "youtube_url", "vod_locale", "lolesports_url", "lolesports_match_id", "lolesports_game_id"])
            for game in games:
                writer.writerow([game["date"], game["time"], game["id"], game["number"], game["blue"], game["red"], *(game.get(key, "") for key in ("youtube_url", "vod_locale", "lolesports_url", "lolesports_match_id", "lolesports_game_id"))])
        with (directory / "picks.csv").open("w", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(HEADERS)
            for game in games:
                for side, team, opponent in (("Blue", game["blue"], game["red"]), ("Red", game["red"], game["blue"])):
                    for row in sorted((r for r in game["picks"] if r["side"].lower() == side.lower()), key=lambda r: ROLES.get(r["position"].lower(), 99)):
                        review = reviews.get((game["id"], row["playername"], row["champion_id"]))
                        writer.writerow([game["date"], game["id"], game["number"], side, team, opponent, row["playername"], row["champion_id"], row["champion"], review["skin"] if review else "", review["chroma"] if review else "", game.get("youtube_url", "")])
        filename = f"{slug}-2026-skin-entry.xlsx"
        write_workbook(directory / filename, games, skin_rows, chroma_rows, reviews)
        write_match_index(directory, {"worlds": "Worlds", "msi": "MSI", "ewc": "EWC"}[slug], config["stage"])
        (directory / "snapshot.json").write_text(json.dumps({"event": slug.upper(), "stage": config["stage"], "source": DATA_URL, "sourceRetrieved": date.today().isoformat(), "throughDate": max(game["date"] for game in games), "patch": config["patch"], "games": len(games), "picks": len(rows), "officialVodsMatched": matched, "reviewedSkins": len(reviews), "skinOptions": len(skin_rows), "chromaOptionsIncludingDefault": len(chroma_rows)}, indent=2) + "\n")
        print(f"{slug}: {len(games)} games, {len(rows)} picks, {matched} VODs, {len(skin_rows)} skins, {len(chroma_rows)} chroma choices")
    if args.event == "all":
        write_match_index(ROOT / "data" / "worlds" / "2025-main-event", "Worlds 2025", "Main Event")


if __name__ == "__main__":
    main()
